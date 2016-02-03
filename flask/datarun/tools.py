import timeit
import zlib
import base64
import numpy as np
import pandas as pd
from importlib import import_module
from sklearn.cross_validation import train_test_split, StratifiedShuffleSplit
import celery


def read_data(filename, target_column):
    data = pd.read_csv(filename)
    y_array = data[target_column].values
    X_array = data.drop([target_column], axis=1).values
    return X_array, y_array


def _make_error_message(e):
    if hasattr(e, 'traceback'):
        return str(e.traceback)
    else:
        return repr(e)


@celery.task
def add(x, y):
    return x + y


@celery.task
def prepare_data(raw_filename, held_out_test_size, train_filename,
                 test_filename, random_state=42):
    df = pd.read_csv(raw_filename)
    df_train, df_test = train_test_split(
        df, test_size=held_out_test_size, random_state=random_state)
    df_train.to_csv(train_filename)
    df_test.to_csv(test_filename)


@celery.task
def train_test_submission_fold(submission_fold):
    log_message = ''
    # get raw data
    raw_data = submission_fold.submission.raw_data
    try:
        X_train, y_train = read_data(raw_data.files_path + '/train.csv')
        X_test, y_test = read_data(raw_data.files_path + '/test.csv')
    except:
        log_message = log_message + 'ERROR: split data \n'
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


def train_submission_fold(submission_fold, X_train, y_train,
                          list_workflow_elements):
    module_path = submission_fold.submission.files_path
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
    end = timeit.default_timer()
    submission_fold.train_time = end - start
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
    end = timeit.default_timer()
    submission_fold.validation_time = end - start
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
    return log_message


def train_model(module_path, list_workflow_elements, X, y, train_is):
    X_train = X.iloc[train_is]
    y_train = y.iloc[train_is]
    nb_applied_elements = 0
    # it is here assumed that workflow elements are in the right order
    for workflow_element in list_workflow_elements:
        if workflow_element == 'feature_extractor':
            nb_applied_elements += 1
            feature_extractor = import_module('.feature_extractor', module_path)
            fe = feature_extractor.FeatureExtractor()
            fe.fit(X_train, y_train)
            X_train = fe.transform(X_train)
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
                # Calibration
                calibrator = import_module('.calibrator', module_path)
                calib = calibrator.Calibrator()
                y_probas = clf.predict_proba(X_calib_train)
                calib.fit(y_probas, y_calib_train)
                if nb_applied_elements == len(list_workflow_elements):
                    return fe, clf, calib
            else:
                clf.fit(X_train, y_train)
                if nb_applied_elements == len(list_workflow_elements):
                    return fe, clf
        elif workflow_element == 'regressor':
            nb_applied_elements += 1
            regressor = import_module('.regressor', module_path)
            reg = regressor.Regressor()
            reg.fit(X_train, y_train)
            if nb_applied_elements == len(list_workflow_elements):
                return fe, reg


def test_model(trained_model, list_workflow_elements,  X, test_is):
    X_test = X[test_is]
    if 'feature_extraction' in list_workflow_elements:
        fe = trained_model[0]
        X_test = fe.transform(X_test)
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
