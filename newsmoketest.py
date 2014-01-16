#!/usr/bin/env python
#
# smoketest <distro>
# use teuthology to set up a one-machine cluster on <distro>,
# install -agent, -restapi, and -webapp on it, and validate
# basic functionality
#

import datetime
import os
import sys
import select
from subprocess import Popen, PIPE, check_output, CalledProcessError
import tempfile
import textwrap
import webbrowser

OWNER='calamari-autotest@odds'
PKGDIR='packages-staging'

sgr0 = check_output('tput sgr0', shell=True)
red = check_output('tput setaf 1', shell=True)

def wr_red(s):
    sys.stderr.write(red)
    sys.stderr.write(s)
    sys.stderr.write(sgr0)

def wr_err(s):
    sys.stderr.write(s)

def show_fds_and_watch(proc, infd, outfd, errfd, timeout,
                       host_leadin=None, terminator=None):
    '''
    As long as proc's alive, loop watching for lines on outfd and errfd,
    outputting to stdout/stderr as appropriate.  If host_leadin is
    seen on stderr, capture the rest of that line as the hostname.
    If terminator is seen on stderr, or timeout expires, return.
    Return exitcode, host (exitcode is None if success)
    '''
    done = False
    host = None
    rlist = [outfd, errfd]
    xlist = [infd, outfd, errfd]
    while not done:
        exitcode = proc.poll()
        if exitcode is not None:
            wr_red('exited with status ' + str(exitcode) + '\n')
            return(exitcode, host)

        readable, _, errlist = select.select(rlist, [], xlist, timeout)
        if not errlist and not readable:
            wr_red('Select timeout, quitting\n')
            break
        if len(errlist):
            wr_red('Exception on fds: ' + str(errlist) + '\n')
            break

        for fd in readable:
            if fd == proc.stdout.fileno():
                o = proc.stdout.readline()
                sys.stdout.write(o)
            elif fd == proc.stderr.fileno():
                e = proc.stderr.readline()
                if host_leadin and e.startswith(host_leadin):
                    host=e[len(host_leadin):].split()[0]
                    wr_red('FOUND HOSTNAME: ' + host + '\n');
                if e.startswith('INFO:'):
                    wr_err(e)
                else:
                    wr_red(e)
                if terminator and terminator in e:
                    done = True
                    break
            else:
                wr_red('UNKNOWN FD OUTPUT ON ' + str(fd) + '\n')
    return None, host

def distro_version(release):
    relmap = dict({
        'precise':('ubuntu', '12.04'),
        'wheezy':('debian', '7.0'),
        'rhel':('rhel', '6.4'),
        'centos':('centos', '6.4'),
    })

    return relmap[release]

def run_cmd(cmd):
    wr_red('smoketest running ' + cmd + '\n')
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    o, e = proc.communicate()
    if proc.returncode:
        wr_red(e)
        return False
    wr_err(e)
    sys.stdout.write(o)
    return True

def install_repokey(host, flavor):
    if flavor == 'deb':
        return run_cmd('ssh ubuntu@{host} "wget -q -O- http://download.inktank.com/keys/release.asc | sudo apt-key add -"'.format(host=host))
    elif flavor == 'rpm':
        return run_cmd('ssh ubuntu@{host} "sudo rpm --import http://download.inktank.com/keys/release.asc"'.format(host=host))
    else:
       return False

def write_file(contents, path, host):
    proc = Popen(
        'ssh ubuntu@{host} sudo dd of={path}'.format(host=host, path=path),
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True,
    )
    out, err = proc.communicate(contents)
    if proc.returncode:
        if err:
            wr_red(err)
            return False
    sys.stdout.write(out)
    return True

def install_repo(host, release, flavor, branch):
    if flavor == 'deb':
        contents='deb https://{username}:{password}@download.inktank.com' \
                 '/{packages}/{branch}/deb {release} main'.format(
                     username='dmick', password='dmick', packages=PKGDIR,
                     release=release, branch=branch)
        if not write_file(
            contents, '/etc/apt/sources.list.d/inktank.list', host
        ):
            wr_red('write sources.list.d failed')
            return False
        run_cmd('ssh ubuntu@{} '
            '"sudo apt-get install apt-transport-https"'.format(host))
        return run_cmd('ssh ubuntu@{} "sudo apt-get update"'.format(host))
    elif flavor == 'rpm':
        distro, version = distro_version(release)
        contents=textwrap.dedent('''
        [inktank]
        name=Inktank Storage, Inc.
        baseurl=https://{username}:{password}@download.inktank.com/{packages}/{branch}/rpm/{distro}{version}
        gpgcheck=1
        enabled=1
        '''.format(username='dmick', password='dmick', packages=PKGDIR,
            distro=distro, version=version, branch=branch))
        if not write_file(
            contents, '/etc/yum.repos.d/inktank.repo', host
        ):
            wr_red('write yum.repos.d failed')
            return False
        return run_cmd('ssh ubuntu@{} "sudo yum makecache"'.format(host))
    else:
       return False

def install_package(package, host, flavor):
    if flavor == 'deb':
        pkgcmd = 'DEBIAN_FRONTEND=noninteractive sudo -E apt-get -y ' \
                 'install {package}'
    elif flavor == 'rpm':
        pkgcmd = 'sudo yum -y install {package}'
    else:
        wr_red('install_package: bad flavor ' + flavor + '\n')
        return False
    pkgcmd = pkgcmd.format(package=package)

    return run_cmd(('ssh ubuntu@{host} ' + pkgcmd).format(host=host))

def setup_realname_crushmap(host):
    script = textwrap.dedent('''
        ceph osd getcrushmap -o /tmp/mymap
        crushtool -d /tmp/mymap -o /tmp/mymap.txt
        sed -i 's/localhost/{host}/g' /tmp/mymap.txt
        crushtool -c /tmp/mymap.txt -o /tmp/mymap.new
        ceph osd setcrushmap -i /tmp/mymap.new
    '''.format(host=host))
    if not write_file(script, '/tmp/crushedit', host):
        return False
    return run_cmd('ssh ubuntu@{host} bash -x /tmp/crushedit'.format(host=host))

def edit_diamond_config(host):
    cmd = 'ssh ubuntu@{host} ' \
          '"sudo sed -i s/calamari/{host}/ /etc/diamond/diamond.conf"'
    if not run_cmd(cmd.format(host=host)):
        return False
    cmd = 'ssh ubuntu@{host} "sudo service diamond restart"'
    return run_cmd(cmd.format(host=host))

def disable_default_nginx(host, flavor):
    script = textwrap.dedent('''
        if [ -f /etc/nginx/conf.d/default.conf ]; then
            mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.disabled
        fi
        if [ -f /etc/nginx/sites-enabled/default ] ; then
            rm /etc/nginx/sites-enabled/default
        fi
        service nginx restart
        service {service} restart
    ''')
    service = {'rpm':'httpd', 'deb':'apache2'}[flavor]
    script = script.format(service=service)
    write_file(script, '/tmp/disable.nginx', host)
    cmd = 'ssh ubuntu@{host} sudo bash /tmp/disable.nginx'.format(host=host)
    return run_cmd(cmd)

def setup_localhost_cluster(host, flavor):
    package = {'rpm':'sqlite', 'deb':'sqlite3'}[flavor]
    if not install_package(package, host, flavor):
        return False
    sqlcmd = 'insert into ceph_cluster (name, api_base_url) ' \
             'values ("{host}", "http://{host}:5000/api/v0.1/");'.format(
              host=host)
    write_file(sqlcmd, '/tmp/create.cluster.sql', host)
    cmd = 'ssh ubuntu@{host} "cat /tmp/create.cluster.sql | sudo sqlite3 /opt/calamari/webapp/calamari/db.sqlite3"'.format(host=host)
    return run_cmd(cmd)

def main():
    release=sys.argv[1] if len(sys.argv) >= 2 else 'precise'
    if release in ['precise', 'wheezy']:
        flavor = 'deb'
    elif release in ['rhel', 'centos']:
        flavor = 'rpm'
    else:
        wr_red('Unsupported release ' + release)
        return 1

    branch = sys.argv[2] if len(sys.argv) >= 3 else 'master'

    retcode = 0
    # use hostname from release
    calamari_xnames = {'centos': 'centos64'}
    if release in calamari_xnames:
        hrelease = calamari_xnames[release]
    else:
        hrelease = release
    host =  'calamari-{hst}.front.sepia.ceph.com'.format(hst=hrelease)
    shost =  'calamari-{hst}'.format(hst=hrelease)
    try:
        #setup_realname_crushmap(host.split('.')[0])
        setup_realname_crushmap(host)
        if not install_repokey(host, flavor) or \
           not install_repo(host, release, flavor, branch) or \
           not install_package('calamari-agent', host, flavor) or \
           not edit_diamond_config(host) or \
           not install_package('calamari-restapi', host, flavor) or \
           not install_package('calamari-server', host, flavor) or \
           not install_package('calamari-clients', host, flavor) or \
           not disable_default_nginx(host, flavor):
            return 1

        setup_localhost_cluster(host, flavor)
        webbrowser.open('http://{host}/'.format(host=host))
        sys.stdout.write('Hit <return> to tear down\n')
        _ = sys.stdin.readline()

        phyz_host_table = {'precise': 'mira014', 'centos64': 'mira017',
                           'wheezy': 'mira007',}
        physhost = phyz_host_table[hrelease] 
        phost = "{physhost}.front.sepia.ceph.com".format(physhost=physhost)
        run_cmd('ssh ubuntu@{phys_host} "sudo virsh suspend {shost}"'.format(shost=shost, phys_host=phost))
        rev_cmd = 'ssh ubuntu@{phys_host} "sudo virsh snapshot-revert {shost} gold"'.format(host=host, phys_host=phost, shost=shost)
        run_cmd(rev_cmd)
        run_cmd('ssh ubuntu@{phys_host} "sudo virsh resume {shost}"'.format(shost=shost, phys_host=phost))
    finally:
        pass

if __name__ == '__main__':
    sys.exit(main())
