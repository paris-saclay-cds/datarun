from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from runapp import views

urlpatterns = [
    url(r'^rawdata/$', views.RawDataList.as_view(), name='rawdata'),
    url(r'^submissionfold/$', views.SubmissionFoldList.as_view(),
        name='submissionfold-list'),
    url(r'^submissionfold/(?P<pk>[0-9]+)/$',
        views.SubmissionFoldDetail.as_view(), name='submissionfold-detail'),
    url(r'^rawdata/split/$',
        views.SplitTrainTest.as_view(), name='rawdata-split'),
    url(r'^testpredictions/list/$',
        views.GetTestPredictionList.as_view(), name='testpredictions-list'),
    url(r'^testpredictions/new/$',
        views.GetTestPredictionNew.as_view(), name='testpredictions-new'),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
