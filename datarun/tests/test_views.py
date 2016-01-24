import os
import json
import zlib
import nose
import numpy as np
from sklearn import cross_validation
from datarun.tests import test_app
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
# TODO test authentication


def check_content_type(headers):
    nose.tools.eq_(headers['Content-Type'], 'application/json')


def test_list_data():
    ld = test_app.get('/raw_data/')
    check_content_type(ld.headers)
    resp = json.loads(ld.data)
    # make sure we get a response
    nose.tools.eq_(ld.status_code, 200)
    # make sure there is 0 or 1 raw data element (1 if run after test_model)
    nose.tools.assert_in(len(resp['raw_data']), [0, 1])


def test_create_data():
    # create a new raw data element
    raw_data_name = "boson"
    d = {'name': raw_data_name}
    # TODO use a real data file
    with open('requirements.txt', 'r') as ff:
        df = ff.read()
    d['files'] = {'raw_data_test.txt': df}
    ld = test_app.post('/raw_data/', data=json.dumps(d),
                       content_type='application/json')
    check_content_type(ld.headers)
    nose.tools.eq_(ld.status_code, 201)

    # Verify we sent the right data back
    resp = json.loads(ld.data)
    nose.tools.eq_(resp['raw_data']["name"], raw_data_name)
    nose.tools.eq_(resp['raw_data']["files_path"], os.getenv('DIR_DATA') +
                   d['name'])

    # Get raw data, should be 1 or 2 (2 if run after test_model)
    ld = test_app.get('/raw_data/')
    check_content_type(ld.headers)
    resp = json.loads(ld.data)
    # make sure we get a response
    nose.tools.eq_(ld.status_code, 200)
    nose.tools.assert_in(len(resp), [1, 2])


def test_index():
    # list all submission on CV fold
    ld = test_app.get('/submissions_fold/')
    check_content_type(ld.headers)
    resp = json.loads(ld.data)
    # make sure we get a response
    nose.tools.eq_(ld.status_code, 200)
    # check if there is 0 or 1 submission on cv fold (1 if run after test_model)
    nose.tools.assert_in(len(resp['submissions_fold']), [0, 1])


def test_create_submission():
    # create a new submission on cv fold
    subf_id = 2
    sub_id = 2
    raw_data_id = 1
    file1 = 'datarun/tests/test_files/feature_extractor.py'
    file2 = 'datarun/tests/test_files/classifier.py'
    file3 = 'datarun/tests/test_files/calibrator.py'
    d = {'submission_fold_id': subf_id, 'submission_id': sub_id,
         'raw_data_id': raw_data_id}
    skf = cross_validation.ShuffleSplit(100)
    train_is, test_is = list(skf)[0]
    train_is = zlib.compress(np.array(train_is).dumps())
    test_is = zlib.compress(np.array(test_is).dumps())
    d['train_is'] = '' #train_is
    d['test_is'] = '' #test_is
    with open(file1, 'r') as ff:
        df1 = ff.read()
    with open(file2, 'r') as ff:
        df2 = ff.read()
    with open(file3, 'r') as ff:
        df3 = ff.read()
    d['files'] = {file1.split('/')[-1]: df1, file2.split('/')[-1]: df2,
                  file3.split('/')[-1]: df3}
    ld = test_app.post('/submissions_fold/', data=json.dumps(d),
                       content_type='application/json')
    check_content_type(ld.headers)
    nose.tools.eq_(ld.status_code, 201)

    # Verify we sent the right data back
    resp = json.loads(ld.data)
    nose.tools.eq_(resp['submission_fold']["id"], subf_id)

    # Get submission on cv fold, should be 1 or 2 (2 if run after test_model)
    ld = test_app.get('/submissions_fold/')
    check_content_type(ld.headers)
    resp = json.loads(ld.data)
    # make sure we get a response
    nose.tools.eq_(ld.status_code, 200)
    nose.tools.assert_in(len(resp), [1, 2])


def test_submission_state():
    ld = test_app.get('/submissions_fold/1')
    check_content_type(ld.headers)
    # make sure we get a response
    nose.tools.eq_(ld.status_code, 200)
