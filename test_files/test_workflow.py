import time
import json
import zlib
import base64
import numpy as np
from sklearn import cross_validation
import post_api

host_url = "http://127.0.0.1:8000/"
username = "MrTest"
userpassd = "test"

# ----------------------
# TEST WITH IRIS DATASET
# ----------------------
data_name = "iris"
data_file = 'iris.csv'
n_samples = 150
held_out_test = 0.5
target_column = 'species'
workflow_elements = 'classifier'
submission_id = 1
submission_fold_id = 1
submission_files = ['feature_extractor.py', 'classifier.py', 'calibrator.py']

# Send data
post_data = post_api.post_data(host_url, username, userpassd,
                               data_name, target_column, workflow_elements,
                               data_file)
# Get data id
data_id = json.loads(post_data.content)["id"]

# Split data into train and test
post_split = post_api.post_split(host_url, username, userpassd,
                                 held_out_test, data_id)

# Send submission
priority = 'L'
skf = cross_validation.ShuffleSplit(int(n_samples * held_out_test))
train_is, test_is = list(skf)[0]
post_submission = post_api.post_submission_fold(host_url, username, userpassd,
                                                submission_id,
                                                submission_fold_id,
                                                train_is, test_is, priority,
                                                data_id, submission_files)
task_id = json.loads(post_submission.content)["task_id"]
print('train-test task id: ', task_id)

# Wait to be sure it was trained and tested and saved in the db (every X min)
time.sleep(58)

# Get submission prediction
post_pred = post_api.get_prediction_list(host_url, username, userpassd,
                                         [submission_fold_id])
pred = json.loads(post_pred.content)[0]['test_predictions']
pred = np.fromstring(zlib.decompress(base64.b64decode(pred)), dtype=float)
pred = pred.reshape(int(n_samples * held_out_test), 3)
sum_prob = np.ones(int(n_samples * held_out_test))
if (pred.sum(axis=1) == sum_prob).all():
    print('Oh yeah 1!')

post_pred_new = post_api.get_prediction_new(host_url, username, userpassd,
                                            data_id)
if json.loads(post_pred_new.content) == []:
    print("Oh yeah 2!")
