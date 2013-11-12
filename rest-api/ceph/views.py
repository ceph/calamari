from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status
from django.views.decorators.cache import never_cache
from ceph.models import Cluster
from django.contrib.auth.models import User

from ceph.serializers import ClusterSpaceSerializer, ClusterHealthSerializer, UserSerializer,\
    ClusterSerializer, OSDDetailSerializer, OSDListSerializer, ClusterHealthCountersSerializer


class Space(APIView):
    model = Cluster

    def get(self, request, cluster_pk):
        cluster = get_object_or_404(Cluster, pk=cluster_pk)

        #if not cluster.space:
        #    return Response({}, status.HTTP_202_ACCEPTED)
        return Response(ClusterSpaceSerializer(cluster).data)


class Health(APIView):
    model = Cluster

    def get(self, request, cluster_pk):
        cluster = get_object_or_404(Cluster, pk=cluster_pk)
        if not cluster.health:
            return Response({}, status.HTTP_202_ACCEPTED)
        return Response(ClusterHealthSerializer(cluster).data)


class HealthCounters(APIView):
    model = Cluster

    def get(self, request, cluster_pk):
        cluster = get_object_or_404(Cluster, pk=cluster_pk)
        if not cluster.counters:
            return Response({}, status.HTTP_202_ACCEPTED)
        return Response(ClusterHealthCountersSerializer(cluster).data)


class OSDList(APIView):
    model = Cluster

    def _filter_by_pg_state(self, cluster, pg_states):
        """Filter the cluster OSDs by PG states.

        Note that we can't do any nice DB querying here because we aren't
        normalizing out our data to fit the relational model. Thus, this is a
        bit hacky.

        We are modifying the OSD field of this instance of a cluster based on
        the filtering, and passing the result to the serializer. Do not do
        anything like a .save() on this instance; it's just a vehicle for the
        filtered OSDs.
        """
        pg_states = set(map(lambda s: s.lower(), pg_states.split(",")))
        target_osds = set([])
        for state, osds in cluster.osds_by_pg_state.iteritems():
            if state in pg_states:
                target_osds |= set(osds)
        cluster.osds[:] = [o for o in cluster.osds if o['id'] in target_osds]

    def get(self, request, cluster_pk):
        cluster = get_object_or_404(Cluster, pk=cluster_pk)
        if not cluster.osds:
            return Response([], status.HTTP_202_ACCEPTED)
        pg_states = request.QUERY_PARAMS.get('pg_states', None)
        if pg_states:
            if not cluster.pgs:
                return Response([], status.HTTP_202_ACCEPTED)
            self._filter_by_pg_state(cluster, pg_states)
        return Response(OSDListSerializer(cluster).data)


class OSDDetail(APIView):
    model = Cluster

    def get(self, request, cluster_pk, osd_id):
        cluster = get_object_or_404(Cluster, pk=cluster_pk)
        if not cluster.has_osd(osd_id):
            return Response({}, status.HTTP_202_ACCEPTED)
        return Response(OSDDetailSerializer(cluster, osd_id).data)


class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['GET'])
@permission_classes((AllowAny,))
@never_cache
def user_me(request):
    """
    Return information about the current user. If the user is not authenticated
    (i.e. an anonymous user), then 401 is returned with an error message.
    """
    if request.method != 'GET':
        return
    if request.user.is_authenticated():
        return Response(UserSerializer(request.user).data)
    return Response({
        'message': 'Session expired or invalid',
    }, status.HTTP_401_UNAUTHORIZED)
