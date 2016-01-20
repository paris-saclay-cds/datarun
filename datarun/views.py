#!flask/bin/python
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask import jsonify  # , abort, make_response
from flask.ext.httpauth import HTTPBasicAuth
# from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from datarun import app

# app = Flask(__name__)
# app.config.from_object(os.getenv('APP_SETTINGS'))
# db = SQLAlchemy(app)
auth = HTTPBasicAuth()

from datarun.models import SubmissionFold


@app.route('/submissions_fold/', methods=['GET'])
@auth.login_required
def index():
    return jsonify({'submissions_fold': SubmissionFold.query.all()})


@app.route('/submissions_fold/<int:id>')
@auth.login_required
def get_submission_state(id):
    return jsonify({'submission_fold': SubmissionFold.query.get(id)})


@app.route('/submissions_fold/', methods=['POST'])
@auth.login_required
def create_submission():
    if not request.json or 'submission_fold_id' not in request.json:
        abort(400)
    submission_fold = SubmissionFold(request.json.submission_fold_id,
                                     )
    return jsonify({'submission_fold': SubmissionFold.query.get(id)})


if __name__ == '__main__':
    app.run(debug=True)
