import json
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
print(task_id)
