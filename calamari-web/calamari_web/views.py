

from django.views.static import serve as static_serve
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

import zerorpc

from cthulhu.config import CalamariConfig
config = CalamariConfig()


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
