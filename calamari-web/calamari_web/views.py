
import socket
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.static import serve as static_serve
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework import status
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from salt.config import master_config
from salt.loader import _create_loader

import zerorpc

from cthulhu.config import CalamariConfig
config = CalamariConfig()


def get_grains():
    """
    Return the salt grains for this host that we are running
    on.  If we support SELinux in the future this may need
    to be moved into a cthulhu RPC as the apache worker may
    not have the right capabilities to query all the grains.
    """
    # Stash grains as an attribute of this function
    if not hasattr(get_grains, 'grains'):
        # Use salt to get an interesting subset of the salt grains (getting
        # everything is a bit slow)
        grains = {}
        c = master_config(config.get('cthulhu', 'salt_config_path'))
        l = _create_loader(c, 'grains', 'grain')
        funcs = l.gen_functions()
        for key in [k for k in funcs.keys() if k.startswith('core.')]:
            ret = funcs[key]()
            if isinstance(ret, dict):
                grains.update(ret)
        get_grains.grains = grains
    else:
        grains = get_grains.grains

    return grains


@api_view(['GET'])
@permission_classes((AllowAny,))
def info(request):
    grains = get_grains()

    try:
        ipaddr = socket.gethostbyname(grains['fqdn'])
    except socket.gaierror:
        # It is annoying, but not rare, to have a host
        # that cannot resolve its own name.
        # From a dict of interface name to list of addresses,
        # we pick the first address from the first interface
        # which has some addresses and isn't a loopback.
        ipaddr = [addrs for name, addrs in grains['ip_interfaces'].items() if
                  name not in ['lo', 'lo0'] and addrs][0][0]

    return Response({
        "version": "2.0",  # TODO: populate from build version (ticket #7082)
        "license": "N/A",
        "registered": "N/A",
        "hostname": grains['host'],
        "fqdn": grains['fqdn'],
        "ipaddr": ipaddr
    })


@api_view(['GET'])
@login_required
def grains(request):
    """
    The info view does not require authentication, because it
    is needed to render basic info like software version.  The full
    grain dump does require authentication because some of
    the info here could be useful to attackers.
    """
    return Response(get_grains())


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
    client.connect(config.get('cthulhu', 'rpc_url'))
    clusters = client.list_clusters()
    if not clusters:
        return redirect("/admin/#cluster")
    return serve_dir_or_index(request, path, document_root)

BOOTSTRAP_TEMPLATE = """
# Calamari minion bootstrap script.
#
# When downloaded from a calamari server instance, downloads
# calamari-salt-minion from that URL before installing it and configuring
# it to point to the server address.
#
# The calamari server will attempt to infer the HTTP and Salt addresses
# from the Host: used to download the script, if this fails override them
# on the command line.

import sys
import subprocess
import os

SALT_PACKAGE = "salt-minion"
SALT_CONFIG_PATH = "/etc/salt/"

if len(sys.argv) > 1:
    BASE_URL = sys.argv[1]
else:
    BASE_URL = "{base_url}"

if len(sys.argv) > 2:
    MASTER = sys.argv[2]
else:
    MASTER = "{master}"

# Configure package repository
# Would be nice to use apt-add-repository, but it's not always there and
# trying to apt-get install it from the net would be a catch-22
open("/etc/apt/sources.list.d/calamari.list", 'w').write("deb {base_url}static/ubuntu precise main")

# Deploy salt minion
subprocess.check_call(["apt-get", "update"])
subprocess.check_call(["apt-get", "install", "-y", "--force-yes", SALT_PACKAGE])
open(os.path.join(SALT_CONFIG_PATH, "minion.d/calamari.conf"), 'w').write("master: %s\\n" % MASTER)

"""


def bootstrap(request):
    # Best effort to work out the URL that the client used to access
    # this server
    proto = "https" if request.is_secure() else "http"
    http_host = request.META['HTTP_HOST']
    my_url = "{0}://{1}/".format(proto, http_host)
    my_hostname = http_host.split(":")[0]

    bootstrap_script = BOOTSTRAP_TEMPLATE.format(
        base_url=my_url, master=my_hostname
    )

    return HttpResponse(bootstrap_script)
