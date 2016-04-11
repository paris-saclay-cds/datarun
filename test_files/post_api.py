import requests
import zlib
import base64


def read_compress(file_name):
    with open(file_name, 'r') as ff:
        df = ff.read()
    return base64.b64encode(zlib.compress(df))


def url_post(url1, url2, username, password, data):
    url = url1 + url2
    url = url[0:9] + url[9::].replace('//', '/')
    return requests.post(url, auth=(username, password), json=data)


def url_get(url1, url2, username, password, r_id=None):
    url = url1 + url2
    url = url[0:9] + url[9::].replace('//', '/')
    if r_id:
        url = url + str(r_id) + '/'
    return requests.get(url, auth=(username, password))


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
    return url_post(host_url, '/runapp/rawdata/', username, password,
                    data)


def post_split(host_url, username, password,
               held_out_test, raw_data_id, random_state=42):
    data = {'random_state': random_state, 'held_out_test': held_out_test,
            'raw_data_id': raw_data_id}
    return url_post(host_url, '/runapp/rawdata/split/', username, password,
                    data)


def post_submission_fold(host_url, username, password,
                         sub_id, sub_fold_id, train_is, test_is,
                         priority='L',
                         raw_data_id=None, list_submission_files=None):
    """
    To post submission on cv fold and submission (if not already posted).
    Submission files are compressed (with zlib) and base64-encoded before being
    posted.

    :param host_url: api host url, such as http://127.0.0.1:8000/ (localhost)
    :param username: username to be used for authentication
    :param password: password to be used for authentication
    :param sub_id: id of the submission on databoard
    :param sub_fold_id: id of the submission on cv fold on databoard
    :param train_is: train indices for the cv fold
    :param test_is: test indices for the cv fold
    :param priority: priority level to train test the model: L for low
    and H for high

    :type host_url: string
    :type username: string
    :type password: string
    :type sub_id: integer
    :type sub_fold_id: integer
    :type train_is: numpy array
    :type test_is: numpy array
    :type priority: string
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
    return url_post(host_url, '/runapp/submissionfold/', username, password,
                    data)


def get_prediction_list(host_url, username, password,
                        list_submission_fold_id):
    """
    Get predictions given a list of submission on cv fold ids

    :param host_url: api host url, such as http://127.0.0.1:8000/ (localhost)
    :param username: username to be used for authentication
    :param password: password to be used for authentication
    :param list_submission_fold_id: list of submission on cv fold ids from which
    we want the predictions

    :type host_url: string
    :type username: string
    :type password: string
    :type list_submission_fold_id: list
    """
    data = {'list_submission_fold': list_submission_fold_id}
    return url_post(host_url, '/runapp/testpredictions/list/', username,
                    password, data)


def get_prediction_new(host_url, username, password,
                       raw_data_id):
    """
    Get all new predictions given a raw data id

    :param host_url: api host url, such as http://127.0.0.1:8000/ (localhost)
    :param username: username to be used for authentication
    :param password: password to be used for authentication
    :param raw_data_id: id of a data set from which we want new predictions

    :type host_url: string
    :type username: string
    :type password: string
    :type raw_data_id: integer
    """
    data = {'raw_data_id': raw_data_id}
    return url_post(host_url, '/runapp/testpredictions/new/', username,
                    password, data)


def get_raw_data(host_url, username, password):
    """
    Get all raw data sets

    :param host_url: api host url, such as http://127.0.0.1:8000/ (localhost)
    :param username: username to be used for authentication
    :param password: password to be used for authentication

    :type host_url: string
    :type username: string
    :type password: string
    """
    return url_get(host_url, '/runapp/rawdata/', username, password)


def get_submission_fold_light(host_url, username, password):
    """
    Get all submissions on cv fold
    only main info: id, associated submission id, state, and new

    :param host_url: api host url, such as http://127.0.0.1:8000/ (localhost)
    :param username: username to be used for authentication
    :param password: password to be used for authentication

    :type host_url: string
    :type username: string
    :type password: string
    """
    return url_get(host_url, '/runapp/submissionfold-light/', username,
                   password)


def get_submission_fold(host_url, username, password):
    """
    Get all submission on cv fold (all attributes)

    :param host_url: api host url, such as http://127.0.0.1:8000/ (localhost)
    :param username: username to be used for authentication
    :param password: password to be used for authentication

    :type host_url: string
    :type username: string
    :type password: string
    """
    return url_get(host_url, '/runapp/submissionfold/', username, password)


def get_submission_fold_detail(host_url, username, password,
                               submission_fold_id):
    """
    Get details about a submission on cv fold given its id

    :param host_url: api host url, such as http://127.0.0.1:8000/ (localhost)
    :param username: username to be used for authentication
    :param password: password to be used for authentication
    :param submission_fold_id: id of the submission on cv fold

    :type host_url: string
    :type username: string
    :type password: string
    :param submission_fold_id: integer
    """
    return url_get(host_url, '/runapp/submissionfold/', username, password,
                   r_id=submission_fold_id)