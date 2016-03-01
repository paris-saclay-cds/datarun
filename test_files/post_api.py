import requests
import zlib
import base64


def read_compress(file_name):
    with open(file_name, 'r') as ff:
        df = ff.read()
    return base64.b64encode(zlib.compress(df.tostring()))


def post_data(host_url, username, password,
              data_name, target_column, workflow_elements, data_file):
    """
    To post data to the datarun api.
    Data are compressed (with zlib) and base64-encoded before being posted.

    :param host_url: api host url, such as http://127.0.0.1:8000/ (localhost)
    :param username: username to be used for authentication
    :param password: password to be used for authentication
    :param data_name: name of the raw dataset
    :param target_column: name of the target column
    :param workflow_elements: workflow elements associated with this dataset,
    e.g., feature_extractor, classifier
    :param data_file: name with absolute of the dataset file

    :type host_url: string
    :type username: string
    :type password: string
    :type data_name: string
    :type target_column: string
    :type workflow_elements: string
    :type data_file: string
    """

    data = {'name': data_name, 'target_column': target_column,
            'workflow_elements': workflow_elements}
    df = read_compress(data_file)
    data['files'] = {data_name + '.csv': df}
    requests.post(host_url + '/runapp/rawdata/',
                  auth=('username', 'password'),
                  json=data)


def post_submission_fold(host_url, username, password, priority,
                         sub_id, sub_fold_id, train_is, test_is,
                         raw_data_id=None, list_submission_files=None):
    """
    To post submission on cv fold and submission (if not already posted).
    Submission files are compressed (with zlib) and base64-encoded before being
    posted.

    :param host_url: api host url, such as http://127.0.0.1:8000/ (localhost)
    :param username: username to be used for authentication
    :param password: password to be used for authentication

    :type host_url: string
    :type username: string
    :type password: string
    """
    # Compress train and test indices
    train_is = base64.b64encode(zlib.compress(train_is.tostring()))
    test_is = base64.b64encode(zlib.compress(test_is.tostring()))
    data = {'databoard_sf_id': sub_fold_id, 'databoard_s_id': sub_id,
            'train_is': train_is, 'test_is': test_is}
    # If the submission does not exist, post info needed to save it in the db
    if raw_data_id and list_submission_files:
        data['raw_data'] = raw_data_id
        data['files'] = {}
        for ff in list_submission_files:
            data['files'][ff.split('/')[-1]] = read_compress(ff)
    requests.post(host_url + '/runapp/submissionfold/',
                  auth=('username', 'password'),
                  json=data)
