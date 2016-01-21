import json
import nose
from datarun import views
from tests import test_app

# TODO test authentication


def check_content_type(headers):
    nose.tools.eq_(headers['Content-Type'], 'application/json')


def test_list_data():
    ld = test_app.get('/raw_data/')

