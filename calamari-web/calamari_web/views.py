from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.static import serve as static_serve
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from rest_framework import status
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

import zerorpc
from cthulhu.manager.rpc import CTHULHU_RPC_URL

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


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@ensure_csrf_cookie
@never_cache
def login(request):
    if request.method == 'POST':
        username = request.DATA.get('username', None)
        password = request.DATA.get('password', None)
        msg = {}
        if not username:
            msg['username'] = 'This field is required'
        if not password:
            msg['password'] = 'This field is required'
        if len(msg) > 0:
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({
                'message': 'User authentication failed'
            }, status=status.HTTP_401_UNAUTHORIZED)
        auth_login(request, user)
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        return Response({})
    else:
        pass
    request.session.set_test_cookie()
    return Response({})


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def logout(request):
    auth_logout(request)
    return Response({'message': 'Logged out'})


def home(request):
    return HttpResponseRedirect(reverse('dashboard', kwargs={'path': ''}))


@login_required
def serve_dir_or_index(request, path, document_root):
    if len(path) == 0:
        path = 'index.html'
    return static_serve(request, path, document_root)


@login_required
def dashboard(request, path, document_root):
    client = zerorpc.Client()
    client.connect(CTHULHU_RPC_URL)
    clusters = client.list_clusters()
    if not clusters:
        return redirect("/admin/#cluster")
    return serve_dir_or_index(request, path, document_root)
