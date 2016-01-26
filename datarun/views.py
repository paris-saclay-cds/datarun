#!flask/bin/python
import os
from flask import jsonify, abort, make_response, request
from flask.ext.httpauth import HTTPBasicAuth
# from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from datarun import app, db
from datarun.models import RawData, Submission, SubmissionFold

auth = HTTPBasicAuth()

# Submission files are temporarilly saved in submission_directory
# they are likely to be saved in the database as a next step?
# idem for data
data_directory = os.getenv('DIR_DATA')
submission_directory = os.getenv('DIR_SUBMISSION')


def save_files(dir_data, data):
    "save files from data['files'] in directory dir_data"
    os.mkdir(dir_data)
    for n_ff, ff in data['files'].items():
        with open(dir_data + '/' + n_ff, 'w') as o_ff:
            o_ff.write(ff)


@app.route('/raw_data/', methods=['GET'])
# @auth.login_required
def list_data():
    return jsonify({'raw_data': [rd.as_dict() for rd in RawData.query.all()
                                 if rd is not None]})


# @auth.login_required
@app.route('/raw_data/', methods=['POST'])
def create_data():
    if not request.json or 'name' not in request.json \
            or 'target_column' not in request.json \
            or 'workflow_elements' not in request.json:
        abort(400)
    data = request.json
    this_data_directory = data_directory + data['name']
    save_files(this_data_directory, data)
    raw_data = RawData(name=data['name'], files_path=this_data_directory,
                       workflow_elements=data['workflow_elements'],
                       target_column=data['target_column'])
    db.session.add(raw_data)
    db.session.commit()
    return jsonify({'raw_data': raw_data.as_dict()}), 201


@app.route('/submissions_fold/', methods=['GET'])
# @auth.login_required
def index():
    return jsonify({'submissions_fold':
                    [sf.as_dict() for sf in SubmissionFold.query.all()
                     if sf is not None]})


@app.route('/submissions_fold/<int:id>')
# @auth.login_required
def get_submission_state(id):
    if SubmissionFold.query.get(id) is not None:
        return jsonify({'submission_fold':
                        SubmissionFold.query.get(id).as_dict()})
    else:
        return jsonify({'submission_fold': 'empty!'})


@app.route('/submissions_fold/', methods=['POST'])
# @auth.login_required
def create_submission():
    if not request.json or 'submission_fold_id' not in request.json \
                        or 'submission_id' not in request.json:
        abort(400)
    data = request.json
    try:
        # if the submission does not exist in the db, create it
        if not Submission.query.get(data['submission_id']):
            # save submission files TODO: better to save them in the db?
            this_submission_directory = submission_directory + \
                                        'sub_{}'.format(data['submission_id'])
            save_files(this_submission_directory, data)
            submission = Submission(submission_id=data['submission_id'],
                                    files_path=this_submission_directory,
                                    raw_data_id=data['raw_data_id'])
            db.session.add(submission)
            db.session.commit()
    except:
        abort(400)
    # we assume below that train_is and test_is are sent compressed with
    # base64.b64encode(zlib.compress(train_is.tostring()))
    # indices can be retrieved with:
    # np.fromstring(zlib.decompress(base64.b64decode(train_is)), dtype=int)
    try:
        submission_fold = SubmissionFold(submission_fold_id=data[
                                                         'submission_fold_id'],
                                         submission_id=data['submission_id'],
                                         train_is=data['train_is'],
                                         test_is=data['test_is'], state='todo')
        db.session.add(submission_fold)
        db.session.commit()
    except:
        abort(400)
    return jsonify({'submission_fold': submission_fold.as_dict()}), 201


@app.route('/split_train_test/', methods=['POST'])
# @auth.login_required
def split_train_test():
    if not request.json or 'held_out_test_size' not in request.json \
            or 'raw_data_id' not in request.json:
        abort(400)
    # TODO: command to split data
    return jsonify({'Done!': 'Data ready'}), 201


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Oups'}), 404)

if __name__ == '__main__':
    app.run(debug=True)
