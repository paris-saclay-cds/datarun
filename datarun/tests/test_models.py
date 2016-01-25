import os
import base64
import zlib
import numpy as np
from datarun import db
from datarun.models import RawData, Submission, SubmissionFold


def test_raw_data():
    raw_data = RawData(name='iris', files_path=os.getenv('DIR_DATA_TEST'))
    db.session.add(raw_data)
    db.session.commit()


def test_submission():
    raw_data_iris = RawData.query.filter_by(name='iris').first()
    submission = Submission(submission_id=1,
                            files_path=os.getenv('DIR_SUBMISSION_TEST'),
                            raw_data_id=raw_data_iris.id)
    db.session.add(submission)
    db.session.commit()


def test_submission_fold():
    train_is = np.arange(20)
    train_is = base64.b64encode(zlib.compress(train_is.tostring()))
    test_is = np.arange(20, 40)
    test_is = base64.b64encode(zlib.compress(test_is.tostring()))
    submission_fold = SubmissionFold(submission_fold_id=1,
                                     submission_id=1,
                                     train_is=train_is,
                                     test_is=test_is, state='todo')
    db.session.add(submission_fold)
    db.session.commit()


def create_db_test():
    assert len(RawData.query.all()) == 1
