import sys
import time
import json
import zlib
import base64
import numpy as np
from sklearn import cross_validation
import post_api

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
    'data_file': 'iris.csv',
    'n_samples': 150,
    'n_pred': 3,
    'held_out_test': 0.5,
    'target_column': 'species',
    'workflow_elements': 'classifier',
    'submission_id': 1,
    'submission_fold_id1': 1,
    'submission_fold_id2': 2,
    'submission_files': ['feature_extractor.py', 'classifier.py',
                         'calibrator.py'],
}
# TEST WITH BOSTON HOUSING DATASET
dict_param2 = {
    'data_name': "boston_housing",
    'data_file': 'boston_housing.csv',
    'n_samples': 506,
    'n_pred': 1,
    'held_out_test': 0.5,
    'target_column': 'medv',
    'workflow_elements': 'regressor',
    'submission_id': 2,
    'submission_fold_id1': 3,
    'submission_fold_id2': 4,
    'submission_files': ['regressor.py']
}

list_dict_param = [dict_param1, dict_param2]

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

    # Send data
    post_data = post_api.post_data(host_url, username, userpassd,
                                   data_name, target_column, workflow_elements,
                                   data_file)
    # Get data id
    data_id = json.loads(post_data.content)["id"]

    # Split data into train and test
    post_split = post_api.post_split(host_url, username, userpassd,
                                     held_out_test, data_id)

    # Send submission and fold 1
    priority = 'L'
    skf = cross_validation.ShuffleSplit(int(n_samples * held_out_test))
    train_is1, test_is1 = list(skf)[0]
    post_submission1 = post_api.post_submission_fold(host_url, username,
                                                     userpassd, submission_id,
                                                     submission_fold_id1,
                                                     train_is1, test_is1,
                                                     priority,
                                                     data_id, submission_files)
    task_id1 = json.loads(post_submission1.content)["task_id"]
    print('train-test task id fold 1: ', task_id1)

    # Send submission on fold 2
    train_is2, test_is2 = list(skf)[1]
    post_submission2 = post_api.post_submission_fold(host_url, username,
                                                     userpassd, submission_id,
                                                     submission_fold_id2,
                                                     train_is2, test_is2,
                                                     priority,
                                                     data_id, submission_files)
    task_id2 = json.loads(post_submission2.content)["task_id"]
    print('train-test task id fold 2: ', task_id2)

    # Wait to be sure it was trained and tested and saved in the db (every Xmin)
    time.sleep(58)

    # Get submission prediction
    post_pred = post_api.get_prediction_list(host_url, username, userpassd,
                                             [submission_fold_id1])
    pred = json.loads(post_pred.content)[0]['test_predictions']
    pred = np.fromstring(zlib.decompress(base64.b64decode(pred)), dtype=float)
    pred = pred.reshape(int(n_samples * held_out_test), n_pred)
    sum_prob = np.ones(int(n_samples * held_out_test))
    if (pred.sum(axis=1) == sum_prob).all():
        print('Oh yeah 1!')

    post_pred_new = post_api.get_prediction_new(host_url, username, userpassd,
                                                data_id)
    # if json.loads(post_pred_new.content) == []:
    print json.loads(post_pred_new.content)
    if len(json.loads(post_pred_new.content)) == 1:
        print("Oh yeah 2!")
