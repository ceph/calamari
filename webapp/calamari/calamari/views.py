from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

#
# How this is populated and where this info lives will need to change from its
# current static form. This is a work-in-progress, but we'll add this static
# info so the UI development can proceed more easily.
#
VERSION = "0.1"
LICENSE = "trial"
REGISTERED = "Inktank, Inc."
HOSTNAME = "calamari.inktank.com"
IPADDR = "10.10.2.3"

@api_view(['GET'])
@permission_classes((AllowAny,))
def info(request):
    return Response({
        "version": VERSION,
        "license": LICENSE,
        "registered": REGISTERED,
        "hostname": HOSTNAME,
        "ipaddr": IPADDR
    })
