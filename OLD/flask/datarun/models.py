from datarun import db
# from sqlalchemy.dialects.postgresql import JSON


class RawData(db.Model):
    __tablename__ = 'raw_data'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    files_path = db.Column(db.String(200), nullable=True)
    submissions = db.relationship('Submission', backref='raw_data',
                                  lazy='dynamic')
    workflow_elements = db.Column(db.String(200), nullable=False)
    target_column = db.Column(db.String(40), nullable=False)

    def __init__(self, name, files_path, workflow_elements, target_column):
        self.name = name
        self.files_path = files_path
        self.workflow_elements = workflow_elements
        self.target_column = target_column

    def __repr__(self):
        return 'RawData( id {}, name {}, file_path {} )'.format(self.id,
                                                                self.name,
                                                                self.files_path)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Submission(db.Model):
    __tablename__ = 'submission'

    id = db.Column(db.Integer, primary_key=True)
    files_path = db.Column(db.String(200), nullable=True)
    submission_folds = db.relationship('SubmissionFold', backref='submission',
                                       lazy='dynamic')
    raw_data_id = db.Column(db.Integer, db.ForeignKey('raw_data.id'))

    def __init__(self, submission_id, files_path, raw_data_id):
        self.id = submission_id
        self.files_path = files_path
        self.raw_data_id = raw_data_id

    def __repr__(self):
        return 'Submission( id {}, files_path {}, raw_data_id {} )'. \
                format(self.id, self.files_path, self.raw_data_id)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
# TODO? put files in the database
# class SubmissionFile(db.Model):
#     __tablename__ = 'submission_file'
#
#    id = db.Column(db.Integer, primary_key=True)


class SubmissionFold(db.Model):
    __tablename__ = 'submission_folds'

    id = db.Column(db.Integer, primary_key=True)
    # submission_fold_id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    train_is = db.Column(db.Text, nullable=False)
    test_is = db.Column(db.Text, nullable=False)
    # TODO? Do we need to output full_train_predictions and test_predictions
    full_train_predictions = db.Column(db.Text)
    test_predictions = db.Column(db.Text)
    state = db.Column(db.Enum('todo', 'trained', 'validated', 'tested',
                              'error', name='state'), default='todo')
    log_messages = db.Column(db.Text)
    train_time = db.Column(db.Float, nullable=True)
    validation_time = db.Column(db.Float, nullable=True)
    test_time = db.Column(db.Float, nullable=True)
    train_cpu_time = db.Column(db.Float, nullable=True)
    train_memory = db.Column(db.Float, nullable=True)

    def __init__(self, submission_fold_id, submission_id, train_is, test_is,
                 state='todo'):
        # self.submission_fold_id = submission_fold_id
        self.id = submission_fold_id
        self.submission_id = submission_id
        self.train_is = train_is
        self.test_is = test_is
        self.state = state

    def __repr__(self):
        return 'SubmissionFold( id {}, submission_id {}, state {} )'. \
                format(self.id, self.submission_id, self.state)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
