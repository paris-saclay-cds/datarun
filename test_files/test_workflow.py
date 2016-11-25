import os
import sys
import time
import json
import zlib
import base64
import numpy as np
from sklearn import model_selection
import post_api
sys.path.insert(0, '..')
from runapp import tasks

if len(sys.argv) > 1:
    host_url = sys.argv[1]
    username = sys.argv[2]
    userpassd = sys.argv[3]
    print(host_url, username, userpassd)
else:
    host_url = "http://127.0.0.1:8000/"
    username = "MrTest"
    userpassd = "test"

# TEST WITH IRIS DATASET
dict_param1 = {
    'data_name': "iris",
    'data_file': 'iris/iris.csv',
    'extra_files': None,
    'n_samples': 150,
    'n_pred': 3,
    'held_out_test': 0.5,
    'target_column': 'species',
    'workflow_elements': 'classifier',
    'submission_id': 1,
    'submission_fold_id1': 1,
    'submission_fold_id2': 2,
    'submission_files': ['iris/feature_extractor.py', 'iris/classifier.py',
                         'iris/calibrator.py'],
    'new_submission_files': ['iris/other/classifier.py'],
}
# TEST WITH BOSTON HOUSING DATASET
dict_param2 = {
    'data_name': "boston_housing",
    'data_file': 'boston_housing/boston_housing.csv',
    'extra_files': None,
    'n_samples': 506,
    'n_pred': 1,
    'held_out_test': 0.2,
    'target_column': 'medv',
    'workflow_elements': 'regressor',
    'submission_id': 2,
    'submission_fold_id1': 3,
    'submission_fold_id2': 4,
    'submission_files': ['boston_housing/regressor.py'],
    'new_submission_files': None,
}
# TEST WITH VARIABLE STARS DATASET
dict_param3 = {
    'data_name': "variable_stars",
    'data_file': 'variable_stars/data.csv',
    'extra_files': ['variable_stars/data_varlength_features.csv.gz',
                    'variable_stars/variable_stars_datarun.py'],
    'n_samples': 8497,
    'n_pred': 4,
    'held_out_test': 0.7,
    'target_column': 'type',
    'workflow_elements': 'feature_extractor, classifier, calibrator',
    'submission_id': 3,
    'submission_fold_id1': 5,
    'submission_fold_id2': 6,
    'submission_files': ['variable_stars/feature_extractor.py',
                         'variable_stars/classifier.py',
                         'variable_stars/calibrator.py'],
    'new_submission_files': None,
}


# list_dict_param = [dict_param1, dict_param2, dict_param3]
list_dict_param = [dict_param1, dict_param2]
# list_dict_param = [dict_param1]
time_sleep_split = 58  # number of sec to wait after sending the split task
time_sleep_train = 228  # number of sec to wait after sending the split task

for dict_param in list_dict_param:

    data_name = dict_param['data_name']
    data_file = dict_param['data_file']
    n_samples = dict_param['n_samples']
    n_pred = dict_param['n_pred']
    held_out_test = dict_param['held_out_test']
    target_column = dict_param['target_column']
    workflow_elements = dict_param['workflow_elements']
    submission_id = dict_param['submission_id']
    submission_fold_id1 = dict_param['submission_fold_id1']
    submission_fold_id2 = dict_param['submission_fold_id2']
    submission_files = dict_param['submission_files']
    new_submission_files = dict_param['new_submission_files']
    extra_files = dict_param['extra_files']

    # cleaning old test directories
    temp_data_name = 'temp_test_' + data_name
    os.system('rm -rf sub')
    os.system('rm -rf ' + temp_data_name)

    # Send data
    post_data = post_api.post_data(host_url, username, userpassd,
                                   data_name, target_column, workflow_elements,
                                   data_file, extra_files=extra_files)
    # Get data id
    if post_data.ok:
        data_id = json.loads(post_data.content)["id"]
        print('** Data id on datarun: %s **' % data_id)
    elif "RawData with this name already exists" in post_data.content:
        get_data = post_api.get_raw_data(host_url, username, userpassd)
        list_data = json.loads(get_data.content)
        data_id = [dd['id'] for dd in list_data if
                   dd['name'] == data_name][0]
        print('** Data id on datarun: %s **' % data_id)
    else:
        print('** Problem submitting data to datarun, no data id **')
        raise(NameError, 'problem submissiting')

    # Split data into train and test
    if extra_files:
        post_split = post_api.custom_post_split(host_url, username, userpassd,
                                                data_id)
    else:
        post_split = post_api.post_split(host_url, username, userpassd,
                                         held_out_test, data_id)
    time.sleep(time_sleep_split)
    # os.system('cp variable_stars/*csv* ../test_data/variable_stars/.')

    # Send submission and fold 1
    priority = 'L'
    skf = model_selection.ShuffleSplit(random_state=42)
    n_pts = int(np.floor(n_samples * (1 - held_out_test)))
    skf_list = list(skf.split(np.arange(n_pts)))
    train_is1, test_is1 = skf_list[0]
    post_submission1 = post_api.post_submission_fold(host_url, username,
                                                     userpassd, submission_id,
                                                     submission_fold_id1,
                                                     train_is1, test_is1,
                                                     priority,
                                                     data_id, submission_files,
                                                     force='submission, ' +
                                                     'submission_fold')
    task_id1 = json.loads(post_submission1.content)["task_id"]
    print('train-test task id fold 1: ', task_id1)

    # Send submission on fold 2
    train_is2, test_is2 = skf_list[1]
    post_submission2 = post_api.post_submission_fold(host_url, username,
                                                     userpassd, submission_id,
                                                     submission_fold_id2,
                                                     train_is2, test_is2,
                                                     priority)
    post_submission2 = post_api.post_submission_fold(host_url, username,
                                                     userpassd, submission_id,
                                                     submission_fold_id2,
                                                     train_is2, test_is2,
                                                     priority,
                                                     force='submission_fold')
    task_id2 = json.loads(post_submission2.content)["task_id"]
    print('train-test task id fold 2: ', task_id2)

    # Wait to be sure it was trained and tested and saved in the db (every Xmin)
    time.sleep(time_sleep_train)

    # Get submission prediction of fold1
    post_pred = post_api.get_prediction_list(host_url, username, userpassd,
                                             [submission_fold_id1])
    pred = json.loads(post_pred.content)[0]['test_predictions']
    pred = np.fromstring(zlib.decompress(base64.b64decode(pred)), dtype=float)
    pred = pred.reshape(int(np.ceil(n_samples * held_out_test)), n_pred)

    # Compute locally predictions of fold 1 with original submission file
    os.mkdir(temp_data_name)
    os.system('touch ' + temp_data_name + '/__init__.py')
    raw_data_files_path = '' + temp_data_name + '/'
    abs_raw_data_files_path = os.path.abspath('.') + '/' + temp_data_name + '/'
    if extra_files:
        for ff in (dict_param['extra_files'] + [data_file]):
            if '.py' in ff:
                os.system('cp ' + ff + ' ' + temp_data_name +
                          '/specific.py')
            else:
                os.system('cp ' + ff + ' ' + temp_data_name +
                          '/' + ff.split('/')[-1])
        tasks.custom_prepare_data(abs_raw_data_files_path)
    else:
        os.system('cp ' + data_file + ' ' + temp_data_name +
                  '/' + data_name + '.csv')
        tasks.prepare_data(abs_raw_data_files_path + data_name + '.csv',
                           held_out_test,
                           abs_raw_data_files_path + 'train.csv',
                           abs_raw_data_files_path + 'test.csv')
    os.mkdir('sub')
    for ff in submission_files:
        os.system('cp ' + ff + ' sub/.')
    submission_files_path = 'sub'
    os.system('touch sub/__init__.py')
    tt1 = base64.b64encode(zlib.compress(train_is1.tostring()))
    train_test_local = tasks.train_test_submission_fold(raw_data_files_path,
                                                        workflow_elements,
                                                        target_column,
                                                        submission_files_path,
                                                        tt1, '')
    test_pred = train_test_local[4]
    test_pred = np.fromstring(zlib.decompress(base64.b64decode(test_pred)),
                              dtype=float)
    test_pred = test_pred.reshape(int(np.ceil(n_samples * held_out_test)),
                                  n_pred)
    os.system('rm -rf sub')
    os.system('rm -rf ' + temp_data_name)
    # Compare predictions
    if (pred == test_pred).all():
        print('Oh yeah 1!')

    post_pred_new = post_api.get_prediction_new(host_url, username, userpassd,
                                                data_id)
    # print json.loads(post_pred_new.content)
    if len(json.loads(post_pred_new.content)) == 1:
        print("Oh yeah 2!")

    # Resend submission on fold 1 with different submission files
    if new_submission_files:
        post_submission3 = post_api.post_submission_fold(host_url, username,
                                                         userpassd,
                                                         submission_id,
                                                         submission_fold_id1,
                                                         train_is1, test_is1,
                                                         priority,
                                                         data_id,
                                                         new_submission_files,
                                                         force='submission, ' +
                                                         'submission_fold')
        task_id3 = json.loads(post_submission3.content)["task_id"]
        print('train-test task id fold 1 with other submission files: ',
              task_id3)
        time.sleep(time_sleep_train)
        post_pred3 = post_api.get_prediction_list(host_url, username, userpassd,
                                                  [submission_fold_id1])

        pred3 = json.loads(post_pred3.content)[0]['test_predictions']
        pred3 = np.fromstring(zlib.decompress(base64.b64decode(pred3)),
                              dtype=float)
        pred3 = pred3.reshape(int(np.ceil(n_samples * held_out_test)), n_pred)
        print('pred', pred[0:4, :])
        print('pred3', pred3[0:4, :])
        if (pred == pred3).all():
            print('Problem when submitting a task with same parameters...')
