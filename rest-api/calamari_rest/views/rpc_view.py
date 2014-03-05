

"""
Helpers for writing django views and rest_framework ViewSets that get
their data from cthulhu with zeroRPC
"""


from rest_framework import viewsets, status
from rest_framework.views import APIView
from zerorpc import LostRemote
from rest_framework.response import Response
import zerorpc

from calamari_common.config import CalamariConfig
config = CalamariConfig()


class DataObject(object):
    """
    A convenience for converting dicts from the backend into
    objects, because django_rest_framework expects objects
    """
    def __init__(self, data):
        self.__dict__.update(data)


class RPCView(APIView):
    serializer_class = None

    def __init__(self, *args, **kwargs):
        super(RPCView, self).__init__(*args, **kwargs)
        self.client = zerorpc.Client()

    def dispatch(self, request, *args, **kwargs):
        self.client.connect(config.get('cthulhu', 'rpc_url'))
        try:
            return super(RPCView, self).dispatch(request, *args, **kwargs)
        finally:
            self.client.close()

    @property
    def help(self):
        return self.__doc__

    @property
    def help_summary(self):
        return ""

    def handle_exception(self, exc):
        try:
            return super(RPCView, self).handle_exception(exc)
        except LostRemote as e:
            return Response({'detail': "RPC error ('%s')" % e},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE, exception=True)

    def metadata(self, request):
        ret = super(RPCView, self).metadata(request)

        actions = {}
        # TODO: get the fields marked up with whether they are:
        # - [allowed|required|forbidden] during [creation|update] (6 possible kinds of field)
        # e.g. on a pool
        # id is forbidden during creation and update
        # pg_num is required during create and optional during update
        # pgp_num is optional during create or update
        # nothing is required during update
        if hasattr(self, 'update'):
            print self.__class__
            actions['PATCH'] = self.serializer_class().metadata()
        if hasattr(self, 'create'):
            actions['POST'] = self.serializer_class().metadata()
        ret['actions'] = actions

        return ret


class RPCViewSet(viewsets.ViewSetMixin, RPCView):
    pass
