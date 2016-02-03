from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from runapp import views

urlpatterns = [
    url(r'^runapp/rawdata/$', views.RawDataList.as_view()),
    url(r'^runapp/submissionfold/$', views.SubmissionFoldList.as_view()),
    url(r'^runapp/submissionfold/(?P<pk>[0-9]+)/$',
        views.SubmissionFoldDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
