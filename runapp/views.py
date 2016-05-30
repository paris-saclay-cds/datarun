import os
import zlib
import base64
import hashlib
from .models import RawData, Submission, SubmissionFold
from .serializers import RawDataSerializer, SubmissionSerializer
from .serializers import SubmissionFoldSerializer, SubmissionFoldLightSerializer
from .serializers import TestPredSubmissionFoldSerializer
from django.http import Http404
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
import tasks


# Submission files are temporarilly saved in submission_directory
# they are likely to be saved in the database as a next step?
# idem for data
data_directory = os.environ.get('DIR_DATA', '/home/datarun/data')
submission_directory = os.environ.get('DIR_SUBMISSION',
                                      '/home/datarun/submission')


def _make_error_message(e):
    if hasattr(e, 'traceback'):
        return str(e.traceback)
    else:
        return repr(e)


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
       'rawdata': reverse('rawdata-list', request=request, format=format),
       'submissionfold': reverse('submissionfold-list', request=request,
                                 format=format)
    })


def save_files(dir_data, data):
    "save files from data['files'] in directory dir_data"
    try:
        if not os.path.exists(dir_data):
            os.makedirs(dir_data)
        os.system('touch ' + dir_data + '/__init__.py')
        for n_ff, ff in data['files'].items():
            with open(dir_data + '/' + n_ff, 'w') as o_ff:
                ff = zlib.decompress(base64.b64decode(ff))
                o_ff.write(ff)
    except Exception as e:
        print(e)


class RawDataList(APIView):
    """List all data set or submit a new one"""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """
        List all raw dataset \n
        - Example with curl (on localhost): \n
        curl -u username:password GET http://127.0.0.1:8000/runapp/rawdata/ \n
        - Example with the python package requests (on localhost): \n
        requests.get('http://127.0.0.1:8000/runapp/rawdata/',\
            auth=('username', 'password'))\n
        ---
        response_serializer: RawDataSerializer
        """
        raw_datas = RawData.objects.all()
        serializer = RawDataSerializer(raw_datas, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Create a new dataset \n
        You have to post the name of the dataset, the target column,\
        the workflow elements, and the raw data file. If your data file does\
        not match the format expected by datarun (a csv with a first row\
            containing the feature and target column name, and then a row for\
            each sample), you can submit a python file containing three\
            functions: prepare_data(data_path), get_train_data(data_path),\
            and get_test_data(data_path)\n
        - Example with curl (on localhost): \n
            curl -u username:password   -H "Content-Type: application/json"\
            -X POST\
            -d '{"name": "iris", "target_column": "species",\
                 "workflow_elements": "classifier",\
                "files": {"iris.csv": 'blablabla', 'specific.py': 'bli'}}'\
                http://127.0.0.1:8000/runapp/rawdata/ \n
            Don't forget double quotes for the json, simple quotes don't work.\n
        - Example with the python package requests (on localhost): \n
            requests.post('http://127.0.0.1:8000/runapp/rawdata/',\
                          auth=('username', 'password'),\
                          json={'name': 'iris', 'target_column': 'species',\
                                 'workflow_elements': 'classifier',\
                        'files': {'iris.csv': 'bla', 'specific.py': 'bli'}})\n
        ---
        request_serializer: RawDataSerializer
        response_serializer: RawDataSerializer
        """
        data = request.data
        if 'name' in data.keys():
            this_data_directory = data_directory + '/' + request.data['name']
            data['files_path'] = this_data_directory
        serializer = RawDataSerializer(data=data)
        if serializer.is_valid():
            # save raw data file
            if len(request.data['files']) > 1:
                # A specific and maybe other raw data files have been submitted
                file_types = [kk.split('.')[-1] for kk in
                              request.data['files'].keys()]
                if 'py' not in file_types:
                    # Error, needs a specific if more that one file is submitted
                    return Response({'error': 'Submit a specific.py \
                                               when submitting several files'},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    # Rename the py file to specific.py
                    # Raw data file names are not modified, since called in
                    # functions of the specific
                    index_specific = file_types.index('py')
                    kk = request.data['files'].keys()[index_specific]
                    if kk != 'specific.py':
                        request.data['files']['specific.py'] = \
                                                   request.data['files'][kk]
                        request.data['files'].pop(kk)
            else:
                # No specific has been submitted, using default functions
                # prepare_data() and read_data() from runapp/task.py
                kk = request.data['files'].keys()[0]
                if kk != request.data['name'] + '.csv':
                    request.data['files'][request.data['name'] + '.csv'] = \
                        request.data['files'][kk]
                    request.data['files'].pop(kk)
            # if 'files_path' in data.keys():
            #     this_data_directory = data['files_path']
            save_files(this_data_directory, request.data)
            # save raw data in the database
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmissionFoldLightList(APIView):
    """To get main info about all submissions on CV fold"""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """
        List main info (id, submission id, state, new) about all submissions\
        on CV fold \n
        - Example with curl (on localhost): \n
            curl -u username:password GET\
            http://127.0.0.1:8000/runapp/submissionfold-light/ \n
        - Example with the python package requests (on localhost): \n
            requests.get('http://127.0.0.1:8000/runapp/submissionfold-light/',\
            auth=('username', 'password'))\n
        ---
        response_serializer: SubmissionFoldLightSerializer
        """
        submission_folds = SubmissionFold.objects.all()
        serializer = SubmissionFoldLightSerializer(submission_folds, many=True)
        return Response(serializer.data)


class SubmissionFoldList(APIView):
    """To get all submissions on CV fold"""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """
        List all submission on CV fold \n
        - Example with curl (on localhost): \n
            curl -u username:password GET\
            http://127.0.0.1:8000/runapp/submissionfold/ \n
        - Example with the python package requests (on localhost): \n
            requests.get('http://127.0.0.1:8000/runapp/submissionfold/',\
            auth=('username', 'password'))\n
        ---
        response_serializer: SubmissionFoldSerializer
        """
        submission_folds = SubmissionFold.objects.all()
        serializer = SubmissionFoldSerializer(submission_folds, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Create a submission on CV fold (and if necessary the associated\
        submission) \n
        - Example with curl (on localhost): \n
            curl -u username:password   -H "Content-Type: application/json"\
            -X POST\
            -d '{"databoard_s_id": 1, "files": {"classifier.py":\
                "import sklearn.."}, "train_is": "hgjhg", "raw_data":1,\
                "databoard_sf_id": 11, "test_is": "kdjhLGf2",\
                "priority": "L"}'\
                http://127.0.0.1:8000/runapp/submissionfold/ \n
            Don't forget double quotes for the json, simple quotes do not work\n
        - Example with the python package requests (on localhost): \n
            requests.post('http://127.0.0.1:8000/runapp/submissionfold/',\
                          auth=('username', 'password'),\
                          json={'databoard_sf_id': 10, 'databoard_s_id': 24,\
                                'raw_data': 8, 'train_is': 'GDHRFdfgfd',\
                                'test_is': 'kdjhLGf2', 'priority': 'L'\
                                'files': {'classifier.py': 'import skle...'}})\n
        Possible to force the submission and submission on CV fold (even if the\
        ids already exist) by adding to the data dictionary \
        "force": 'submission, submission_fold' to resubmit both, or \
        "force": 'submission_fold' to resubmit only the submission on CV fold\n
        ---
        request_serializer: SubmissionFoldSerializer
        response_serializer: SubmissionFoldSerializer
        """
        data = request.data
        if 'databoard_s_id' in data.keys():
            data['databoard_s'] = data['databoard_s_id']
            this_submission_directory = submission_directory + \
                '/sub_{}'.format(request.data['databoard_s_id'])
            data['files_path'] = this_submission_directory
        # if force
        if 'force' in data.keys():
            if 'submission, submission_fold' in data['force']:
                try:
                    os.system('rm -rf ' + data['files_path'])
                    submission = Submission.objects.get(
                        databoard_s_id=data['databoard_s_id'])
                    submission.delete()
                except:
                    pass
            if 'submission_fold' in data['force']:
                try:
                    submission_fold = SubmissionFold.objects.get(
                        databoard_sf_id=data['databoard_sf_id'])
                    submission_fold.delete()
                except:
                    pass
        # create associated submission if it does not exist in the db
        try:
            Submission.objects.get(
                            databoard_s_id=request.data['databoard_s_id'])
        except:
            # create hash of the submission files
            hash_obj = hashlib.md5(open(data['files'].items()[0], 'rb').read())
            for fname in data['files'].items()[1:]:
                hash_obj.update(open(fname, 'rb').read())
            data['hash_files'] = hash_obj.digest()
            # call submission serializer
            serializer_submission = SubmissionSerializer(data=data)
            if serializer_submission.is_valid():
                # save submission files
                save_files(this_submission_directory, data)
                # save submission in the database
                serializer_submission.save()
        # create submission on cv fold
        serializer = SubmissionFoldSerializer(data=data)
        # we assume below that train_is and test_is are sent compressed with
        # base64.b64encode(zlib.compress(train_is.tostring()))
        # indices can be retrieved with:
        # np.fromstring(zlib.decompress(base64.b64decode(train_is)), dtype=int)
        if serializer.is_valid():
            # save submission fold in the database
            serializer.save()
            # Add train-test task to the queue (low priority by default)
            if 'priority' in data.keys():
                priority = data['priority']
            else:
                priority = "L"
            try:
                submission_fold = SubmissionFold.objects.\
                    get(databoard_sf_id=data['databoard_sf_id'])
                raw_data_files_path = submission_fold.databoard_s.\
                    raw_data.files_path
                workflow_elements = submission_fold.databoard_s.\
                    raw_data.workflow_elements
                raw_data_target_column = submission_fold.databoard_s.\
                    raw_data.target_column
                submission_files_path = submission_fold.databoard_s.\
                    files_path
                train_is = submission_fold.train_is
                hash_sub_files = submission_fold.databoard_s.hash_files
                task = tasks.train_test_submission_fold.apply_async(
                    (raw_data_files_path, workflow_elements,
                     raw_data_target_column, submission_files_path, train_is,
                     hash_sub_files),
                    queue=priority)
                # task = tasks.train_test_submission_fold.delay(
                #     raw_data_files_path, workflow_elements,
                #     raw_data_target_column, submission_files_path, train_is)
                task_id = task.id
                submission_fold.task_id = task_id
                submission_fold.save()
            except Exception as e:
                print('Train test not started for submission fold %s'
                      % data['databoard_sf_id'])
                print(e)
                task_id = None
            dd = serializer.data
            dd['task_id'] = task_id
            return Response(dd, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmissionFoldDetail(APIView):
    """Get a submission on CV fold given its id"""

    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return SubmissionFold.objects.get(pk=pk)
        except SubmissionFold.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """
        Retrieve a SubmissionFold instance to check its state \n
        - Example with curl (on localhost): \n
            curl -u username:password GET\
            http://127.0.0.1:8000/runapp/submissionfold/10/ \n
        - Example with the python package requests (on localhost): \n
            requests.get('http://127.0.0.1:8000/runapp/submissionfold/10/',\
            auth=('username', 'password'))\n
        ---
        parameters:
            - name : pk
              description: id of the submission on cv fold in the databoard db
              required: true
              type: interger
              paramType: path
        response_serializer: SubmissionFoldSerializer
        """
        submission_fold = self.get_object(pk)
        serializer = SubmissionFoldSerializer(submission_fold)
        return Response(serializer.data)


class GetTestPredictionList(APIView):
    """Get predictions of submissions on cv fold given their ids"""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        """
        Retrieve predictions (on the test data set) of SubmissionFold instances\
        among a list of id that have been trained and tested \n
        - Example with curl (on localhost): \n
            curl -u username:password -H "Content-Type: application/json"\
            -X POST\
            -d '{"list_submission_fold": [1, 2, 10]}'\
                http://127.0.0.1:8000/runapp/testpredictions/list/ \n
            Don't forget double quotes for the json, simple quotes do not work\n
        - Example with the python package requests (on localhost): \n
            requests.post('http://127.0.0.1:8000/runapp/testpredictions/list/',\
                          auth=('username', 'password'),\
                          json={'list_submission_fold': [1, 2, 10]})\n
        ---
        parameters:
            - name: list_submission_fold
              description: list of submission on cv fold ids
              required: true
              type: list
              paramType: form
        response_serializer: TestPredSubmissionFoldSerializer
        """
        data = request.data
        try:
            ind = data['list_submission_fold']
            tested_sub = SubmissionFold.objects.filter(databoard_sf_id__in=ind)
            serializer = TestPredSubmissionFoldSerializer(tested_sub, many=True)
            for sub in tested_sub:
                sub.new = False
                sub.save()
            return Response(serializer.data)
        except Exception as e:
            error_message = 'You need to post list_submission_fold: a list\
                of submission on cv fold id' + _make_error_message(e)
            return Response({'error': error_message},
                            status=status.HTTP_204_NO_CONTENT)


class GetTestPredictionNew(APIView):
    """Get predictions of submissions on cv fold that have not been requested"""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        """
        Retrieve predictions (on the test data set) of  SubmissionFold\
        instances that have been trained and tested and not yet requested.\
        You can specify a given data challenge by posting the raw_data id. \n
        - Example with curl (on localhost): \n
            curl -u username:password -H "Content-Type: application/json"\
            -X POST\
            -d '{"raw_data_id": 1}'\
                http://127.0.0.1:8000/runapp/testpredictions/new/ \n
            Don't forget double quotes for the json, simple quotes do not work\n
        - Example with the python package requests (on localhost): \n
            requests.post('http://127.0.0.1:8000/runapp/testpredictions/new/',\
                          auth=('username', 'password'),\
                          json={'raw_data_id': 1})\n
        ---
        parameters:
            - name: raw_data_id
              description: id of the raw dataset from which to get predictions
              required: false
              type: integer
              paramType: form
        response_serializer: TestPredSubmissionFoldSerializer
        """
        data = request.data
        try:
            if 'raw_data_id' in data.keys():
                tested_sub = SubmissionFold.\
                   objects.filter(state='TESTED', new=True,
                                  databoard_s__raw_data__id=data['raw_data_id'])
            else:
                tested_sub = SubmissionFold.objects.filter(state='TESTED',
                                                           new=True)
            serializer = TestPredSubmissionFoldSerializer(tested_sub, many=True)
            for sub in tested_sub:
                sub.new = False
                sub.save()
            return Response(serializer.data)
        except:
            return Response({'error': 'Oups, something went wrong!'},
                            status=status.HTTP_204_NO_CONTENT)


class SplitTrainTest(APIView):
    """Split data set into train and test datasets for normal dataset"""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        """
        Split raw data into train and test datasets for normal dataset \n
        - Example with curl (on localhost): \n
            curl -u username:password -H "Content-Type: application/json"\
            -X POST\
            -d '{"random_state": 42, "held_out_test": 0.7, "raw_data_id": 1}'\
                http://127.0.0.1:8000/runapp/rawdata/split/ \n
            Don't forget double quotes for the json, simple quotes do not work\n
        - Example with the python package requests (on localhost): \n
            requests.post('http://127.0.0.1:8000/runapp/raw_data/split/',\
                          auth=('username', 'password'),\
                          json={'random_state': 42, 'held_out_test': 0.7,\
                                'raw_data_id': 1})\n
        ---
        parameters:
            - name: random_state
              description: random state used to split data
              required: false
              type: integer
              paramType: form
            - name: held_out_test
              description: percentage of the dataset kept as test dataset
              required: true
              type: float
              paramType: form
            - name: raw_data_id
              description: id of the raw dataset
              required: true
              type: integer
              paramType: form
        """
        data = request.data
        if 'random_state' in data:
            random_state = data['random_state']
        else:
            random_state = 42
        held_out_test_size = data['held_out_test']
        raw_data = RawData.objects.get(id=data['raw_data_id'])
        raw_filename = raw_data.files_path + '/' + raw_data.name + '.csv'
        train_filename = raw_data.files_path + '/train.csv'
        test_filename = raw_data.files_path + '/test.csv'
        task = tasks.prepare_data.delay(raw_filename, held_out_test_size,
                                        train_filename, test_filename,
                                        random_state=random_state)
        return Response({'task_id': task.id})


class CustomSplitTrainTest(APIView):
    """
    Split data set into train and test datasets for custom dataset
    (when a specific.py was submitted along with raw data
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        """
        Split raw data into train and test datasets for custom dataset \n
        - Example with curl (on localhost): \n
            curl -u username:password -H "Content-Type: application/json"\
            -X POST\
            -d '{"raw_data_id": 1}'\
                http://127.0.0.1:8000/runapp/rawdata/customsplit/ \n
            Don't forget double quotes for the json, simple quotes do not work\n
        - Example with the python package requests (on localhost): \n
            requests.post('http://127.0.0.1:8000/runapp/raw_data/customsplit/',\
                          auth=('username', 'password'),\
                          json={'raw_data_id': 1})\n
        ---
        parameters:
            - name: raw_data_id
              description: id of the raw dataset
              required: true
              type: integer
              paramType: form
        """
        data = request.data
        raw_data = RawData.objects.get(id=data['raw_data_id'])
        task = tasks.custom_prepare_data.delay(raw_data.files_path)
        return Response({'task_id': task.id})
