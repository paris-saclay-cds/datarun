import sys
import os
import timeit
import zlib
import base64
import resource
import numpy as np
import pandas as pd
from importlib import import_module
from sklearn.cross_validation import train_test_split, StratifiedShuffleSplit
from celery import shared_task
from celery.utils.log import get_task_logger
# os.environ['DJANGO_SETTINGS_MODULE'] = 'datarun.settings'
# from django.conf import settings
list_path = os.environ.get('DIR_SUBMISSION').split('/')
if '' == list_path[-1]:
    list_path = list_path[0:-1]
list_path = list_path[0:-1]
dir_module = '/'.join(list_path)
sys.path.insert(0, dir_module)

logger = get_task_logger(__name__)


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


def cpu_time_resource():
    cpu_user = resource.getrusage(resource.RUSAGE_SELF).ru_utime
    cpu_system = resource.getrusage(resource.RUSAGE_SELF).ru_stime
    return cpu_user + cpu_system


def memory_usage_resource():
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.
    return mem


@shared_task
def add(x, y):
    return x + y


def save_submission_fold_db(submission_fold, log_messages,
                            submission_fold_state, metrics,
                            full_train_predictions, test_predictions):
    submission_fold.log_messages = log_messages
    submission_fold.state = submission_fold_state
    submission_fold.test_predictions = test_predictions
    submission_fold.full_train_predictions = full_train_predictions
    if metrics:
        submission_fold.train_time = metrics[u'train_time']
        submission_fold.validation_time = metrics[u'validation_time']
        submission_fold.test_time = metrics[u'test_time']
        submission_fold.train_cpu_time = metrics[u'train_cpu_time']
        submission_fold.test_cpu_time = metrics[u'test_cpu_time']
        submission_fold.train_memory = metrics[u'train_memory']
        submission_fold.test_memory = metrics[u'test_memory']
    submission_fold.save()


@shared_task
def task_save_submission_fold_db():
    '''
    Get all new trained tested submission on cv fold and save them in the
    database. This task requires an access to the db
    '''
    logger.info('oh yeah')
    try:
        from runapp.models import SubmissionFold
        # Get all new trained tested submission on cv fold
        submission_folds = SubmissionFold.objects.\
            filter(test_predictions__isnull=True).\
            filter(task_id__isnull=False)
        for submission_fold in submission_folds:
            task = train_test_submission_fold.\
                AsyncResult(submission_fold.task_id)
            if task.state == 'SUCCESS':
                log_message, submission_fold_state, metrics,\
                    full_train_predictions, test_predictions = task.result
                # if 'ERROR' not in log_message and 'error' not in log_message:
                save_submission_fold_db(submission_fold, log_message,
                                        submission_fold_state,
                                        metrics, full_train_predictions,
                                        test_predictions)
    except ImportError:
        logger.info('task_save_submission_fold_db ImportError. OK for runners!')


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
    df_train.to_csv(train_filename, index=False)
    df_test.to_csv(test_filename, index=False)


@shared_task
def custom_prepare_data(raw_data_files_path):
    '''
    Split dataset in train and test datasets FOR CUSTOM DATASET (when a specific
    was submitted with the data)

    :param raw_data_path: path where raw data and specific.py are saved

    :type raw_data_path: string
    '''
    try:
        raw_data_module_path = '/'.join(raw_data_files_path.
                                        replace('//', '/').
                                        split('/')[-2::])
        raw_data_module_path = raw_data_module_path.replace('/', '.')
        specific = import_module('.specific', raw_data_module_path)
        specific.prepare_data(raw_data_files_path)
    except Exception as e:
        raise e


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
        if os.path.isfile(raw_data_files_path + '/specific.py'):
            if raw_data_files_path[-1] == '/':
                raw_data_files_path = raw_data_files_path[0:-1]
            raw_data_module_path = '/'.join(raw_data_files_path.
                                            replace('//', '/').
                                            split('/')[-2::])
            raw_data_module_path = raw_data_module_path.replace('/', '.')
            specific = import_module('.specific', raw_data_module_path)
            X_train, y_train = specific.get_train_data(raw_data_files_path)
            X_test, y_test = specific.get_test_data(raw_data_files_path)
        else:
            X_train, y_train = read_data(raw_data_files_path + '/train.csv',
                                         raw_data_target_column)
            X_test, y_test = read_data(raw_data_files_path + '/test.csv',
                                       raw_data_target_column)
    except:
        log_message = log_message + 'ERROR(split data) \n'
        return log_message, 'TODO', {}, None, None
    # get workflow elements
    list_workflow_elements = workflow_elements.split(',')
    list_workflow_elements = [ww.strip() for ww in list_workflow_elements]
    # train submission on fold
    trained_model, log_train, submission_fold_state, metrics,\
        full_train_predictions = \
        train_submission_fold(submission_files_path, train_is,
                              X_train, y_train, list_workflow_elements)
    log_message = log_message + '\n' + log_train
    if 'ERROR' not in submission_fold_state:
        log_test, submission_fold_state, metrics_test, test_predictions = \
            test_submission_fold(trained_model, X_test, y_test,
                                 list_workflow_elements)
        metrics.update(metrics_test)
        log_message = log_message + '\n' + log_test
        metrics['train_memory'] = memory_usage_resource()
        metrics['test_memory'] = metrics['train_memory']
    else:
        full_train_predictions = None
        test_predictions = None
    return log_message, submission_fold_state, metrics,\
        full_train_predictions, test_predictions


def train_submission_fold(submission_files_path, train_is, X_train,
                          y_train, list_workflow_elements):
    module_path = '/'.join(submission_files_path.replace('//', '/').
                           split('/')[-2::])
    module_path = module_path.replace('/', '.')
    train_is = np.fromstring(zlib.decompress(base64.b64decode(train_is)),
                             dtype=int)
    log_message = ''
    metrics = {}
    # Train
    start = timeit.default_timer()
    start_cpu = cpu_time_resource()
    try:
        trained_submission = train_model(module_path, list_workflow_elements,
                                         X_train, y_train, train_is)
        submission_fold_state = 'TRAINED'
    except Exception, e:
        submission_fold_state = 'ERROR'
        log_message = log_message + _make_error_message(e) + ' - ERROR(train)\n'
        return None, log_message, submission_fold_state, None, None
    end = timeit.default_timer()
    end_cpu = cpu_time_resource()
    metrics['train_time'] = end - start
    metrics['train_cpu_time'] = end_cpu - start_cpu
    # Validation
    start = timeit.default_timer()
    try:
        predictions = test_model(trained_submission, list_workflow_elements,
                                 X_train, range(len(y_train)))
        if len(predictions) == len(y_train):
            predictions = base64.b64encode(zlib.compress(
                predictions.tostring()))
            full_train_predictions = predictions
            submission_fold_state = 'VALIDATED'
        else:
            log_message = log_message + 'Wrong full train prediction size: \n'\
                          + '{} instead of {} \n'.format(len(predictions),
                                                         len(y_train))\
                          + ' - ERROR(validation)\n'
            submission_fold_state = 'ERROR'
            full_train_predictions = None
    except Exception, e:
        submission_fold_state = 'ERROR'
        log_message = log_message + _make_error_message(e) +\
            ' - ERROR(validation)\n'
        return None, log_message, submission_fold_state, None, None
    end = timeit.default_timer()
    end_cpu = cpu_time_resource()
    metrics['validation_time'] = end - start
    return trained_submission, log_message, submission_fold_state,\
        metrics, full_train_predictions


def test_submission_fold(trained_submission, X_test, y_test,
                         list_workflow_elements):
    log_message = ''
    metrics = {}
    start = timeit.default_timer()
    start_cpu = cpu_time_resource()
    try:
        predictions = test_model(trained_submission, list_workflow_elements,
                                 X_test, range(len(y_test)))
        if len(predictions) == len(y_test):
            test_predictions = base64.b64encode(zlib.compress(
                predictions.tostring()))
            submission_fold_state = 'TESTED'
        else:
            log_message = log_message + 'Wrong test prediction size: \n'\
                          + '{} instead of {} \n'.format(len(predictions),
                                                         len(y_test))\
                          + ' - ERROR(test)\n'
            submission_fold_state = 'ERROR'
            test_predictions = None
    except:
        log_message = log_message + 'Problem in test_model - ERROR(test)'
        submission_fold_state = 'ERROR'
        test_predictions = None
        pass
    end = timeit.default_timer()
    end_cpu = cpu_time_resource()
    metrics['test_time'] = end - start
    metrics['test_cpu_time'] = end_cpu - start_cpu
    return log_message, submission_fold_state, metrics, test_predictions


def train_model(module_path, list_workflow_elements, X, y, train_is):
    if type(X) == pd.core.frame.DataFrame:
        X_train = X.iloc[train_is]
        y_train = y.iloc[train_is]
    else:
        X_train = [X[i] for i in train_is]
        y_train = np.array([y[i] for i in train_is])
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
    if type(X) == pd.core.frame.DataFrame:
        X_test = X.iloc[test_is]
    else:
        X_test = [X[i] for i in test_is]
    if 'feature_extractor' in list_workflow_elements:
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
