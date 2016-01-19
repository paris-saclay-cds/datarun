#!flask/bin/python
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
# from flask import jsonify, abort, make_response
# from flask.ext.httpauth import HTTPBasicAuth
# from flask.ext.restful import Api, Resource, reqparse, fields, marshal

app = Flask(__name__)
app.config.from_object(os.getenv('APP_SETTINGS'))
db = SQLAlchemy(app)

# auth = HTTPBasicAuth()

# @app.route('/todo/api/v1.0/tasks', methods=['GET'])
# @auth.login_required
# def get_tasks():
#    return jsonify({'tasks': tasks})

if __name__ == '__main__':
    app.run(debug=True)
