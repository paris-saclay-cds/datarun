import os
import timeit
import zlib
import base64
import numpy as np
import pandas as pd
from importlib import import_module
from sklearn.cross_validation import train_test_split, StratifiedShuffleSplit
from celery import shared_task
os.environ['DJANGO_SETTINGS_MODULE'] = 'datarun.settings'
# from django.conf import settings


def read_data(filename, target_column):
    data = pd.read_csv(filename)
    y_df = data[target_column]
    X_df = data.drop([target_column], axis=1)
    return X_df, y_df


def _make_error_message(e):
    if hasattr(e, 'traceback'):
        return str(e.traceback)
    else:
        return repr(e)


@shared_task
def add(x, y):
    return x + y


@shared_task
def save_submission_fold_db():
    '''
    Get all new trained tested submission on cv fold and save them in the
    database
    '''
    from runapp.models import SubmissionFold
    # Get all new trained tested submission on cv fold
    submission_folds = SubmissionFold.objects.\
        filter(test_predictions__isnull=True).\
        filter(task_id__isnull=False)
    for submission_fold in submission_folds:
        print('status', train_test_submission_fold.AsyncResult(submission_fold.
                                                               task_id).state)


@shared_task
def prepare_data(raw_filename, held_out_test_size, train_filename,
                 test_filename, random_state=42):
    '''
    Split dataset in train and test datasets

    :param raw_filename: name of raw data with path
    :param held_out_test_size: percentage of data for the test dataset
    :param train_filename: name of the file in which we are going to save the
    train dataset
    :param test_filename: name of the file in which we are going to save the
    test dataset

    :type raw_filename: string
    :type held_out_test_size: float (between 0 and 1)
    :type train_filename: string
    :type test_filename: string
    '''
    df = pd.read_csv(raw_filename)
    df_train, df_test = train_test_split(
        df, test_size=held_out_test_size, random_state=random_state)
    df_train.to_csv(train_filename)
    df_test.to_csv(test_filename)


@shared_task
def train_test_submission_fold(raw_data_files_path, workflow_elements,
                               raw_data_target_column, submission_files_path,
                               train_is):
    '''
    Train and test a submission on a fold

    :param raw_data_files_path: path of raw data file
    :param workflow_elements: workflow elements separated by a comma
    :param raw_data_target_column: name of the targetted column
    :param submission_files_path: path of the submission files
    :param train_is: indices of train dataset for this fold (compressed and
    base64 encoded)

    :type raw_data_files_path: string
    :type workflow_elements: string
    :type raw_data_target_column: string
    :type submission_files_path: string
    :type train_is: string
    '''
    log_message = ''
    try:
        X_train, y_train = read_data(raw_data_files_path + '/train.csv',
                                     raw_data_target_column)
        X_test, y_test = read_data(raw_data_files_path + '/test.csv',
                                   raw_data_target_column)
    except:
        log_message = log_message + 'ERROR: split data \n'
        return log_message, 'TODO', {}, None, None
    # get workflow elements
    list_workflow_elements = workflow_elements.split(',')
    # train submission on fold
    trained_model, log_train, submission_fold_state, metrics,\
        full_train_predictions = \
        train_submission_fold(submission_files_path, train_is,
                              X_train, y_train, list_workflow_elements)
    log_message = log_message + '\n' + log_train
    if 'error' not in submission_fold_state:
        log_test, submission_fold_state, metrics_test, test_predictions = \
            test_submission_fold(trained_model, X_test, y_test,
                                 list_workflow_elements)
        metrics.update(metrics_test)
        log_message = log_message + '\n' + log_test
    else:
        full_train_predictions = None
        test_predictions = None
    return log_message, submission_fold_state, metrics,\
        full_train_predictions, test_predictions


def train_submission_fold(submission_files_path, train_is, X_train,
                          y_train, list_workflow_elements):
    module_path = submission_files_path.replace('/', '.')
    train_is = np.fromstring(zlib.decompress(base64.b64decode(train_is)),
                             dtype=int)
    log_message = ''
    metrics = {}
    # Train
    start = timeit.default_timer()
    try:
        trained_submission = train_model(module_path, list_workflow_elements,
                                         X_train, y_train, train_is)
        submission_fold_state = 'trained'
    except Exception, e:
        submission_fold_state = 'error'
        log_message = log_message + _make_error_message(e) + '\n'
        return None, log_message, submission_fold_state, None, None
    end = timeit.default_timer()
    metrics['train_time'] = end - start
    # TODO add resources...
    # Validation
    start = timeit.default_timer()
    try:
        predictions = test_model(trained_submission, list_workflow_elements,
                                 X_train, range(len(y_train)))
        if len(predictions) == len(y_train):
            predictions = base64.b64encode(zlib.compress(
                predictions.tostring()))
            full_train_predictions = predictions
            submission_fold_state = 'validated'
        else:
            log_message = log_message + 'Wrong full train prediction size: \n'\
                          + '{} instead of {} \n'.format(len(predictions),
                                                         len(y_train))
            submission_fold_state = 'error'
            full_train_predictions = None
    except Exception, e:
        submission_fold_state = 'error'
        log_message = log_message + _make_error_message(e) + '\n'
        return None, log_message, submission_fold_state, None, None
    end = timeit.default_timer()
    metrics['validation_time'] = end - start
    return trained_submission, log_message, submission_fold_state,\
        metrics, full_train_predictions


def test_submission_fold(trained_submission, X_test, y_test,
                         list_workflow_elements):
    log_message = ''
    metrics = {}
    start = timeit.default_timer()
    try:
        predictions = test_model(trained_submission, list_workflow_elements,
                                 X_test, range(len(y_test)))
        if len(predictions) == len(y_test):
            test_predictions = base64.b64encode(zlib.compress(
                predictions.tostring()))
            submission_fold_state = 'tested'
        else:
            log_message = log_message + 'Wrong test prediction size: \n'\
                          + '{} instead of {} \n'.format(len(predictions),
                                                         len(y_test))
            submission_fold_state = 'error'
            test_predictions = None
    except:
        pass
    end = timeit.default_timer()
    metrics['test_time'] = end - start
    return log_message, submission_fold_state, metrics, test_predictions


def train_model(module_path, list_workflow_elements, X, y, train_is):
    X_train = X.iloc[train_is]
    y_train = y.iloc[train_is]
    nb_applied_elements = 0
    # it is assimed here that feature extractor takes as input pd.dataframe
    # and output np.array
    if 'feature_extractor' not in list_workflow_elements:
        X_train = np.array(X_train)
        y_train = np.array(y_train)
    # it is here assumed that workflow elements are in the right order
    trained_models = []
    for workflow_element in list_workflow_elements:
        if workflow_element == 'feature_extractor':
            nb_applied_elements += 1
            feature_extractor = import_module('.feature_extractor', module_path)
            fe = feature_extractor.FeatureExtractor()
            fe.fit(X_train, y_train)
            X_train = fe.transform(X_train)
            trained_models.append(fe)
        elif workflow_element == 'classifier':
            nb_applied_elements += 1
            classifier = import_module('.classifier', module_path)
            clf = classifier.Classifier()
            if 'calibrator' in list_workflow_elements:
                nb_applied_elements += 1
                # Train/valid cut for holding out calibration set
                cv = StratifiedShuffleSplit(y_train, n_iter=1, test_size=0.1,
                                            random_state=57)
                calib_train_is, calib_test_is = list(cv)[0]
                X_train_train = X_train[calib_train_is]
                y_train_train = y_train[calib_train_is]
                X_calib_train = X_train[calib_test_is]
                y_calib_train = y_train[calib_test_is]
                # Classification
                clf.fit(X_train_train, y_train_train)
                trained_models.append(clf)
                # Calibration
                calibrator = import_module('.calibrator', module_path)
                calib = calibrator.Calibrator()
                y_probas = clf.predict_proba(X_calib_train)
                calib.fit(y_probas, y_calib_train)
                trained_models.append(calib)
                # if nb_applied_elements == len(list_workflow_elements):
                #     return fe, clf, calib
            else:
                clf.fit(X_train, y_train)
                trained_models.append(clf)
                # if nb_applied_elements == len(list_workflow_elements):
                #     return fe, clf
        elif workflow_element == 'regressor':
            nb_applied_elements += 1
            regressor = import_module('.regressor', module_path)
            reg = regressor.Regressor()
            reg.fit(X_train, y_train)
            trained_models.append(reg)
            # if nb_applied_elements == len(list_workflow_elements):
            #     return fe, reg
    return trained_models


def test_model(trained_model, list_workflow_elements,  X, test_is):
    X_test = X.iloc[test_is]
    if 'feature_extraction' in list_workflow_elements:
        fe = trained_model[0]
        X_test = fe.transform(X_test)
    else:
        X_test = np.array(X_test)
    if 'regressor' in list_workflow_elements \
       and len(list_workflow_elements) < 3:
        reg = trained_model[-1]
        return reg.predict(X_test)
    if 'classifier' in list_workflow_elements \
       and len(list_workflow_elements) < 4:
        if 'calibrator' not in list_workflow_elements:
            clf = trained_model[-1]
        else:
            clf, calib = trained_model[-2], trained_model[-1]
        y_proba = clf.predict_proba(X_test)
        if 'calibrator' in list_workflow_elements:
            y_proba = calib.predict_proba(y_proba)
        return y_proba
