import os
from .models import RawData, Submission, SubmissionFold
from .serializers import RawDataSerializer, SubmissionSerializer
from .serializers import SubmissionFoldSerializer
from django.http import Http404
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# import tools

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
        serializer = RawDataSerializer(data=request.data)
        if serializer.is_valid():
            # save raw data file
            kk = request.data['files'].keys()[0]
            request.data['files'][request.data['name'] + 'csv'] = \
                request.data['files'][kk]
            request.data['files'].pop(kk)
            this_data_directory = data_directory + request.data['name']
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
        serializer = SubmissionFoldSerializer(data=request.data)
        # we assume below that train_is and test_is are sent compressed with
        # base64.b64encode(zlib.compress(train_is.tostring()))
        # indices can be retrieved with:
        # np.fromstring(zlib.decompress(base64.b64decode(train_is)), dtype=int)
        if serializer.is_valid():
            # if the submission does not exist in the db, create it
            if not Submission.objects.get(request.data['submission_id']):
                serializer_submission = SubmissionSerializer(data=request.data)
                if serializer_submission.is_valid():
                    # save submission files
                    # TODO: better to save them in the db?
                    this_submission_directory = submission_directory + \
                                'sub_{}'.format(request.data['submission_id'])
                    save_files(this_submission_directory, request.data)
                    # save submission in the database
                    serializer_submission.save()
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


# TODO view to train and split dataset
# @app.route('/split_train_test/', methods=['POST'])
# # @auth.login_required
# def split_train_test():
#     if not request.json or 'held_out_test_size' not in request.json \
#             or 'raw_data_id' not in request.json:
#         abort(400)
#     if 'random_state' in request.json:
#         random_state = request.json['random_state']
#     else:
#         random_state = 42
#     held_out_test_size = request.json['held_out_test_size']
#     raw_data = RawData.query.get(request.json['raw_data_id'])
#     raw_filename = raw_data.files_path + '/' + raw_data.name
#     train_filename = raw_data.files_path + '/train.csv'
#     test_filename = raw_data.files_path + '/test.csv'
#     task = tools.prepare_data(raw_filename, held_out_test_size, train_filename,
#                               test_filename, random_state=random_state)
#     return jsonify({'Soon done! task id': task.id}), 201

