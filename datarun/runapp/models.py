from __future__ import unicode_literals

from django.db import models


class RawData(models.Model):
    """
    :param name: name of the data set
    :param files_path: path of file where data are saved
    :param workflow_elements: list of workflow elements used to solve the RAMP
    :param target column: name of the target column

    :type name: string
    :type files_path: string
    :type workflow_elements: string
    :type target_column: string
    """

    name = models.CharField(max_length=40, unique=True, null=False)
    files_path = models.CharField(max_length=200, null=True)
    workflow_elements = models.CharField(max_length=200, null=False)
    target_column = models.CharField(max_length=200, null=False)

    def __unicode__(self):
        return 'RawData(id {}, name {}, file_path {})'.format(self.id,
                                                              self.name,
                                                              self.files_path)


class Submission(models.Model):
    """
    :param databoard_s_id: id of the submission in the db of databoard
    :param files_path: path of submitted files
    :param raw_data: associated raw data

    :type databoard_s_id: IntegerField(primary_key=True)
    :type files_path: CharField(max_length=200, null=True)
    :type raw_data: ForeignKey(RawData, null=True, blank=True)
    """
    databoard_s_id = models.IntegerField(primary_key=True)
    files_path = models.CharField(max_length=200, null=True)
    raw_data = models.ForeignKey(RawData, null=True, blank=True)

    def __unicode__(self):
        return 'Submission(databoard id {}, files_path {}, raw_data_id {})'. \
                format(self.databoard_s_id, self.files_path, self.raw_data_id)

# TODO? put files in the database
# class SubmissionFile(models.Model):


class SubmissionFold(models.Model):
    """
    :param databoard_sf_id: id of the submission on cv fold in databoard db
    :param submission: associated submission
    :param train_is: train indices
    :param test_is!: test indices
    :param full_train_predictions: predictions of the entire train dataset
    :param test_predictions: predictions of the test dataset
    :param state: TODO, TRAINED, VALIDATED, TESTED, ERROR
    :param log_messages: logs recorded during train and test
    :param train_time: real clock training time
    :param validation_time: real clock validation time
    :param test_time: real clock testing time
    :param train_cpu_time:  training cpu time
    :param train_memory: training memory usage

    :type databoard_sf_id: IntegerField(primary_key=True)
    :type submission: ForeignKey(Submission, null=True, blank=True)
    :type train_is: TextField
    :type test_is: TextField
    :type full_train_predictions: TextField
    :type test_predictions: TextField
    :type state: CharField, choices.
    :type log_messages: TextField
    :type train_time: FloatField, default=0.
    :type validation_time: FloatField, default=0.
    :type test_time: FloatField, default=0.
    :type train_cpu_time: FloatField, default=0.
    :type train_memory: FloatField, default=0.
    """

    databoard_sf_id = models.IntegerField(primary_key=True)
    submission = models.ForeignKey(Submission, null=False, blank=True)
    train_is = models.TextField(null=False)
    test_is = models.TextField(null=False)
    # TODO? Do we need to output full_train_predictions and test_predictions
    full_train_predictions = models.TextField(null=True)
    test_predictions = models.TextField(null=True)
    STATE_CHOICES = (
        ('TODO', 'to be trained'),
        ('TRAINED', 'trained'),
        ('VALIDATED', 'trained and validated'),
        ('TESTED', 'trained, validated, and tested'),
        ('ERROR', 'error during the train or test'),
    )
    state = models.CharField(max_length=10, choices=STATE_CHOICES,
                             default='TODO', null=True)
    log_messages = models.TextField(null=True)
    train_time = models.FloatField(default=0., null=True)
    validation_time = models.FloatField(default=0., null=True)
    test_time = models.FloatField(default=0., null=True)
    train_cpu_time = models.FloatField(default=0., null=True)
    train_memory = models.FloatField(default=0., null=True)

    def __unicode__(self):
        return 'SubmissionFold(databoard id {}, submission_id {}, state {})'. \
                format(self.databoard_sf_id, self.submission.id, self.state)
