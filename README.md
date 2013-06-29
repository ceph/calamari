Scripts to install Carbon and Graphite-web on CentOS 6.4. Tested against the
minimal installation ISO of CentOS 6.4.

Development Environment
=====

    rpm -Uvh dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
    yum install python-virtualenv


    virtualenv --no-site-package virtualenv
    source virtualenv/bin/activate
    pip install -r requirements.txt
