from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from runapp import views

urlpatterns = [
    url(r'^runapp/rawdata/$', views.RawDataList.as_view(), name='rawdata'),
    url(r'^runapp/submissionfold/$', views.SubmissionFoldList.as_view(),
        name='submissionfold-list'),
    url(r'^runapp/submissionfold/(?P<pk>[0-9]+)/$',
        views.SubmissionFoldDetail.as_view(), name='submissionfold-detail'),
    url(r'^runapp/rawdata/split/$',
        views.SplitTrainTest.as_view(), name='rawdata-split'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
