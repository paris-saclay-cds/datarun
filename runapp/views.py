import os
from .models import RawData, Submission, SubmissionFold
from .serializers import RawDataSerializer, SubmissionSerializer
from .serializers import SubmissionFoldSerializer
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
data_directory = os.environ.get('DIR_DATA', 'data')
submission_directory = os.environ.get('DIR_SUBMISSION', 'submission')


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
       'rawdata': reverse('rawdata-list', request=request, format=format),
       'submissionfold': reverse('submissionfold-list', request=request,
                                 format=format)
    })


def save_files(dir_data, data):
    "save files from data['files'] in directory dir_data"
    os.mkdir(dir_data)
    os.system('touch ' + dir_data + '/__init__.py')
    for n_ff, ff in data['files'].items():
        with open(dir_data + '/' + n_ff, 'w') as o_ff:
            o_ff.write(ff)


class RawDataList(APIView):
    """
    List all raw dataset, or create a new dataset
    """

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        raw_datas = RawData.objects.all()
        serializer = RawDataSerializer(raw_datas, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        if 'name' in data.keys() and 'files_path' not in data.keys():
            this_data_directory = data_directory + '/' + request.data['name']
            data['files_path'] = this_data_directory
        serializer = RawDataSerializer(data=data)
        if serializer.is_valid():
            # save raw data file
            kk = request.data['files'].keys()[0]
            request.data['files'][request.data['name'] + '.csv'] = \
                request.data['files'][kk]
            request.data['files'].pop(kk)
            if 'files_path' in data.keys():
                this_data_directory = data['files_path']
            save_files(this_data_directory, request.data)
            # save raw data in the database
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmissionFoldList(APIView):
    """
    List all submission on CV fold, or create a new one
    """

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        submission_folds = SubmissionFold.objects.all()
        serializer = SubmissionFoldSerializer(submission_folds, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        if 'databoard_s_id' in data.keys():
            data['databoard_s'] = data['databoard_s_id']
            if 'files_path' not in data.keys():
                this_submission_directory = submission_directory + \
                                '/sub_{}'.format(request.data['databoard_s_id'])
                data['files_path'] = this_submission_directory
        # create associated submission if it does not exist in the db
        try:
            Submission.objects.get(
                            databoard_s_id=request.data['databoard_s_id'])
        except:
            serializer_submission = SubmissionSerializer(data=data)
            if serializer_submission.is_valid():
                # save submission files
                # TODO: better to save them in the db?
                if 'files_path' in data.keys():
                    this_submission_directory = data['files_path']
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmissionFoldDetail(APIView):
    """
    Retrieve a SubmissionFold instance to check its state
    """

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self, pk):
        try:
            return SubmissionFold.objects.get(pk=pk)
        except SubmissionFold.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        submission_fold = self.get_object(pk)
        serializer = SubmissionFoldSerializer(submission_fold)
        return Response(serializer.data)


# @app.route('/split_train_test/', methods=['POST'])
# @auth.login_required
def split_train_test(request):
    data = request.data
    if 'random_state' in data:
        random_state = data['random_state']
    else:
        random_state = 42
    held_out_test_size = data['held_out_test_size']
    raw_data = RawData.objects.get(id=data['raw_data_id'])
    raw_filename = raw_data.files_path + '/' + raw_data.name
    train_filename = raw_data.files_path + '/train.csv'
    test_filename = raw_data.files_path + '/test.csv'
    task = tasks.prepare_data(raw_filename, held_out_test_size,
                              train_filename, test_filename,
                              random_state=random_state)
    # return jsonify({'Soon done! task id': task.id}), 201
