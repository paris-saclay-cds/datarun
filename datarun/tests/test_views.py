import os
import json
import nose
# from datarun import views
from datarun.tests import test_app

# TODO test authentication


def check_content_type(headers):
    nose.tools.eq_(headers['Content-Type'], 'application/json')


def test_list_data():
    ld = test_app.get('/raw_data/')
    print(ld)
    print(ld.headers)
    check_content_type(ld.headers)
    resp = json.loads(ld.data)
    # make sure we get a response
    nose.tools.eq_(ld.status_code, 200)
    # make sure there is one raw data element
    nose.tools.eq_(len(resp['raw_data']), 0)


def test_create_data():
    # create a new raw data element
    d = {'name': "boson"}
    with open('requirements.txt', 'r') as ff:
        df = ff.read()
    d['files'] = {'raw_data_test.txt': df}
    ld = test_app.post('/raw_data/', data=json.dumps(d),
                       content_type='application/json')
    print(ld)
    print(ld.headers)
    check_content_type(ld.headers)
    nose.tools.eq_(ld.status_code, 201)

    # Verify we sent the right data back
    resp = json.loads(ld.data)
    nose.tools.eq_(resp['raw_data']["name"], "boson")
    nose.tools.eq_(resp['raw_data']["files_path"], os.getenv('DIR_DATA') +
                   d['name'])

    # Get raw data, should be two
    ld = test_app.get('/raw_data/')
    check_content_type(ld.headers)
    resp = json.loads(ld.data)
    # make sure we get a response
    nose.tools.eq_(ld.status_code, 200)
    nose.tools.assert_in(len(resp), [1, 2])  # 2 if tes run after test_model
