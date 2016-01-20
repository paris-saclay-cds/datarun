#!flask/bin/python
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask import jsonify  # , abort, make_response
from flask.ext.httpauth import HTTPBasicAuth
# from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from .models import SubmissionFold

app = Flask(__name__)
app.config.from_object(os.getenv('APP_SETTINGS'))
db = SQLAlchemy(app)

auth = HTTPBasicAuth()


@app.route('/submissions_fold/', methods=['GET'])
@auth.login_required
def index():
    return jsonify({'submissions_fold': SubmissionFold.query.all()})


@app.route('/submissions_fold/<int:id>')
def get_submission_state(id):
    return jsonify({'submission_fold': SubmissionFold.query.get(id)})




if __name__ == '__main__':
    app.run(debug=True)
