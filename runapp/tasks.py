import os
import timeit
import zlib
import base64
import numpy as np
import pandas as pd
from importlib import import_module
from sklearn.cross_validation import train_test_split, StratifiedShuffleSplit
from celery import shared_task
from runapp.models import SubmissionFold
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
def prepare_data(raw_filename, held_out_test_size, train_filename,
                 test_filename, random_state=42):
    df = pd.read_csv(raw_filename)
    df_train, df_test = train_test_split(
        df, test_size=held_out_test_size, random_state=random_state)
    df_train.to_csv(train_filename)
    df_test.to_csv(test_filename)


@shared_task
def train_test_submission_fold(submission_fold_id):
    submission_fold = SubmissionFold.objects.\
        get(databoard_sf_id=submission_fold_id)
    log_message = ''
    # get raw data
    raw_data = submission_fold.databoard_s.raw_data
    try:
        X_train, y_train = read_data(raw_data.files_path + '/train.csv',
                                     raw_data.target_column)
        X_test, y_test = read_data(raw_data.files_path + '/test.csv',
                                   raw_data.target_column)
    except:
        log_message = log_message + 'ERROR: split data \n'
        return log_message
    # get workflow elements
    list_workflow_elements = raw_data.workflow_elements.split(',')
    # train submission on fold
    trained_model, log_train = train_submission_fold(submission_fold,
                                                     X_train, y_train,
                                                     list_workflow_elements)
    if 'error' not in submission_fold.state:
        log_test = test_submission_fold(submission_fold, trained_model, X_test,
                                        y_test, list_workflow_elements)
        return (log_message + '\n' + log_train + '\n' + log_test)
    return (log_message + '\n' + log_train)


def train_submission_fold(submission_fold, X_train, y_train,
                          list_workflow_elements):
    module_path = submission_fold.databoard_s.files_path.replace('/', '.')
    train_is = submission_fold.train_is
    train_is = np.fromstring(zlib.decompress(base64.b64decode(train_is)),
                             dtype=int)
    log_message = ''
    # Train
    start = timeit.default_timer()
    try:
        trained_submission = train_model(module_path, list_workflow_elements,
                                         X_train, y_train, train_is)
        submission_fold.state = 'trained'
    except Exception, e:
        submission_fold.state = 'error'
        log_message = log_message + _make_error_message(e) + '\n'
        return None, log_message
    end = timeit.default_timer()
    submission_fold.train_time = end - start
    submission_fold.save()
    # TODO add resources...
    # Validation
    start = timeit.default_timer()
    try:
        predictions = test_model(trained_submission, list_workflow_elements,
                                 X_train, range(len(y_train)))
        if len(predictions) == len(y_train):
            predictions = base64.b64encode(zlib.compress(
                predictions.tostring()))
            submission_fold.full_train_predictions = predictions
            submission_fold.state = 'validated'
        else:
            log_message = log_message + 'Wrong full train prediction size: \n'\
                          + '{} instead of {} \n'.format(len(predictions),
                                                         len(y_train))
            submission_fold.state = 'error'
    except Exception, e:
        submission_fold.state = 'error'
        log_message = log_message + _make_error_message(e) + '\n'
        return None, log_message
    end = timeit.default_timer()
    submission_fold.validation_time = end - start
    submission_fold.save()
    return trained_submission, log_message


def test_submission_fold(submission_fold, trained_submission, X_test, y_test,
                         list_workflow_elements):
    log_message = ''
    start = timeit.default_timer()
    try:
        predictions = test_model(trained_submission, list_workflow_elements,
                                 X_test, range(len(y_test)))
        if len(predictions) == len(y_test):
            predictions = base64.b64encode(zlib.compress(
                predictions.tostring()))
            submission_fold.test_predictions = predictions
            submission_fold.state = 'tested'
        else:
            log_message = log_message + 'Wrong test prediction size: \n'\
                          + '{} instead of {} \n'.format(len(predictions),
                                                         len(y_test))
            submission_fold.state = 'error'

    except:
        pass
    end = timeit.default_timer()
    submission_fold.test_time = end - start
    submission_fold.save()
    return log_message


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
