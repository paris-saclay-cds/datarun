from rest_framework.renderers import JSONRenderer


class RunappJSONRenderer(JSONRenderer):
    media_type = 'application/vnd.datarun.runapp+json'
