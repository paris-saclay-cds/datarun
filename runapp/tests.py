import os
import base64
import zlib
import numpy as np
from sklearn import cross_validation
from test.test_support import EnvironmentVarGuard
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from runapp.models import RawData, Submission, SubmissionFold
import runapp.tasks as task


class ModelTests(TestCase):
    def setUp(self):
        self.env = EnvironmentVarGuard()
        self.env.set('DIR_DATA', 'test_data/')
        self.env.set('DIR_SUBMISSION', 'test_submission/')
        try:
            os.mkdir(self.env['DIR_DATA'])
        except:
            os.system('rm -rf ' + self.env['DIR_DATA'] + '/iris')
        try:
            os.mkdir(self.env['DIR_SUBMISSION'])
        except:
            os.system('rm -rf ' + self.env['DIR_SUBMISSION'] + '/*')
        os.system('touch ' + self.env['DIR_SUBMISSION'] + '/__init__.py')
        RawData.objects.create(name='iris',
                               files_path=self.env['DIR_DATA'],
                               workflow_elements='classifier',
                               target_column='species')
        raw_data_iris = RawData.objects.get(name='iris')
        Submission.objects.create(databoard_s_id=1,
                                  files_path=self.env['DIR_SUBMISSION'],
                                  raw_data=raw_data_iris)
        train_is = np.arange(20)
        train_is = base64.b64encode(zlib.compress(train_is.tostring()))
        test_is = np.arange(20, 40)
        test_is = base64.b64encode(zlib.compress(test_is.tostring()))
        submission = Submission.objects.get(databoard_s_id=1)
        SubmissionFold.objects.create(databoard_sf_id=1,
                                      databoard_s=submission,
                                      train_is=train_is,
                                      test_is=test_is, state='todo')

    def test_get_models(self):
        raw_data = RawData.objects.get(name='iris')
        submission = Submission.objects.get(databoard_s_id=1)
        submission_fold = SubmissionFold.objects.get(databoard_sf_id=1)
        self.assertEqual(raw_data, submission.raw_data)
        self.assertEqual(submission, submission_fold.databoard_s)


class WorkflowTests(APITestCase):
    def setUp(self):
        self.env = EnvironmentVarGuard()
        self.env.set('DIR_DATA', 'test_data')
        self.env.set('DIR_SUBMISSION', 'test_submission')
        self.user = User.objects.create_user(username='test', email='t@t.com',
                                             password='test')
        self.client.login(username='test', password='test')

    def test_workflow(self):
        """
        Make sure we can create raw data, submission, and submission on cv
        fold, and that we can train test submissions on cv fold
        """
        with self.env:
            # Make sure we can create raw data
            # --------------------------------
            url = reverse('rawdata')
            raw_data_name = "iris"
            raw_data_file = 'test_files/iris.csv'
            n_samples = 150
            held_out_test = 0.5
            target_column = 'species'
            workflow_elements = 'classifier'
            data = {'name': raw_data_name, 'target_column': target_column,
                    'workflow_elements': workflow_elements}
            with open(raw_data_file, 'r') as ff:
                df = ff.read()
            data['files'] = {'raw_data_test.txt': df}

            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(RawData.objects.count(), 1)  # or 2??
            self.assertEqual(RawData.objects.all()[0].name, raw_data_name)

            # Make sure we can submit a submission on cv fold
            # -----------------------------------------------
            url = reverse('submissionfold-list')
            subf_id, sub_id = 2, 2
            raw_data_id = RawData.objects.all()[0].pk
            file1 = 'test_files/feature_extractor.py'
            file2 = 'test_files/classifier.py'
            file3 = 'test_files/calibrator.py'
            data = {'databoard_sf_id': subf_id, 'databoard_s_id': sub_id,
                    # 'raw_data': {'id': raw_data_id}}
                    'raw_data': raw_data_id}
            skf = cross_validation.ShuffleSplit(int(n_samples * held_out_test))
            train_is, test_is = list(skf)[0]
            train_is = base64.b64encode(zlib.compress(train_is.tostring()))
            test_is = base64.b64encode(zlib.compress(test_is.tostring()))
            data['train_is'] = train_is
            data['test_is'] = test_is
            with open(file1, 'r') as ff:
                df1 = ff.read()
            with open(file2, 'r') as ff:
                df2 = ff.read()
            with open(file3, 'r') as ff:
                df3 = ff.read()
            data['files'] = {file1.split('/')[-1]: df1,
                             file2.split('/')[-1]: df2,
                             file3.split('/')[-1]: df3}
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Submission.objects.count(), 1)
            self.assertEqual(SubmissionFold.objects.count(), 1)

            # Make sure we can split data into train and test sets
            # ----------------------------------------------------
            raw_data = RawData.objects.get(id=raw_data_id)
            raw_filename = raw_data.files_path + '/' + raw_data.name + '.csv'
            train_filename = raw_data.files_path + '/train.csv'
            test_filename = raw_data.files_path + '/test.csv'
            task.prepare_data(raw_filename, held_out_test,
                              train_filename, test_filename,
                              random_state=42)
            # TODO with the view

            # Make sure we can train and test a submission on cv fold
            # -------------------------------------------------------
            submission_fold = SubmissionFold.objects.get(
                                        databoard_sf_id=subf_id)
            logs = task.train_test_submission_fold(submission_fold)
            print('** logs **', logs)
            print('submission fold state:', submission_fold.state)
            pred = np.fromstring(zlib.decompress(
               base64.b64decode(submission_fold.test_predictions)), dtype=float)
            pred = pred.reshape(int(n_samples * held_out_test), 3)
            sum_prob = np.ones(int(n_samples * held_out_test))
            self.assertTrue((pred.sum(axis=1) == sum_prob).all())