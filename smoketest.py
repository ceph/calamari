#!/usr/bin/env python
#
# smoketest <distro>
# use teuthology to set up a one-machine cluster on <distro>,
# install -agent, -restapi, and -webapp on it, and validate
# basic functionality
#

import logging
import os
import sys
import select
from subprocess import Popen, PIPE, check_output, CalledProcessError
import textwrap
import webbrowser
import paramiko

yaml = '''roles:
- [mon.0, osd.0, osd.1, osd.2, client.0]

tasks:
- chef:
- install:
   branch: dumpling
- ceph:
- interactive:
'''

#yamlshort = '''roles:
#- [client.0]
#
#tasks:
#- interactive:
#'''

OWNER='calamari-autotest@odds'
#REPODIR='packages'
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

def make_cluster(yamlfile, release):
    #cmd = 'teuthology --machine-type=vps --lock ' \
    #      '--owner=' + OWNER + ' ' + yamlfile
    cmd = 'teuthology --machine-type=mira --lock ' \
          '--owner=' + OWNER + ' ' + yamlfile
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    proc_infd = proc.stdin.fileno()
    proc_outfd = proc.stdout.fileno()
    proc_errfd = proc.stderr.fileno()
    returncode, host = show_fds_and_watch(
        proc, proc_infd, proc_outfd, proc_errfd, 100,
        host_leadin='INFO:teuthology.task.internal:roles: ubuntu@',
        terminator='Ceph test interactive mode',
    )
    if returncode:
        return None, None, returncode
    return proc, host, None

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
        return run_cmd('ssh ubuntu@{host} "rpm --import http://download.inktank.com/keys/release.asc"'.format(host=host))
    else:
       return False

def write_file(contents, path, host):
    proc = Popen(
        'ssh ubuntu@{host}'.format(host=host),
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True,
    )
    out, err = proc.communicate('echo "{contents}" | \
        sudo dd of={path}'.format(path=path, contents=contents))
    if proc.returncode:
        if err:
            wr_red(err)
            return False
    sys.stdout.write(out)
    return True

def install_repo(host, release, flavor):
    if flavor == 'deb':
        contents='deb https://{username}:{password}@download.inktank.com' \
                 '/{packages}/deb {release} main'.format( 
                     username='dmick', password='dmick', packages=PKGDIR,
                     release=release)
        if not write_file(
            contents, '/etc/apt/sources.list.d/inktank.list', host
        ):
            wr_red('write sources.list.d failed')
            return False
        return run_cmd('sudo apt-get update')
    elif flavor == 'rpm':
        contents=textwrap.dedent('''
        [inktank]
        name=Inktank Storage, Inc.
        baseurl=https://{username}:{password}@download.inktank.com/{packages}/rpm/{release}
        gpgcheck=1
        enabled=1
        '''.format(username='dmick', password='dmick', packages=PKGDIR,
            release=release))
        if not write_file(
            contents, '/etc/yum.repos.d/inktank.repo', host
        ):
            wr_red('write yum.repos.d failed')
            return False
        return run_cmd('sudo yum makecache')
    else:
       return False

def install_package(package, host, flavor):
    if flavor == 'deb':
        pkgcmd = 'DEBIAN_FRONTEND=noninteractive sudo -E apt-get -y' \
                 'install {package}'
    elif flavor == 'rpm':
        pkgcmd = 'sudo yum -y install {package}'
    else:
        wr_red('install_package: bad flavor ' + flavor + '\n')
        return False
    pkgcmd = pkgcmd.format(package=package)

    logging.getLogger('paramiko').addHandler(logging.StreamHandler())
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='ubuntu')
    try:
        i, o, e = ssh.exec_command(pkgcmd.format(host=host))
        for l in o:
            sys.stdout.write(l)
        for l in e:
            wr_err(l)
        ssh.close()
        return True
    except Exception as e:
        wr_red(e)
        ssh.close()
        return False

def setup_realname_crushmap(host):
    script = textwrap.dedent('''
        ceph osd getcrushmap -o /tmp/mymap
        crushtool -d /tmp/mymap -o /tmp/mymap.txt
        sed -i 's/localhost/{host}/g' /tmp/mymap.txt
        crushtool -c /tmp/mymap.txt -o /tmp/mymap.new
        ceph osd setcrushmap -i /tmp/mymap.new
    '''.format(host=host))
    if not write_file(script, '/tmp/crushedit', host): return False
    return run_cmd('ssh {host} bash -x /tmp/crushedit'.format(host=host))

def main():
    release=sys.argv[1] if len(sys.argv) >= 2 else 'precise'
    if release in ['precise', 'wheezy']:
        flavor = 'deb'
    elif release in ['rhel6.4', 'centos6.4']:
        flavor = 'rpm'
    else:
        wr_red('Unsupported release ' + release)
        return 1

    try:
        yamlfile = os.tmpnam()
        f = open(yamlfile, 'w+')
        f.write(yaml)
        # f.write(yamlshort)
        f.close()
        proc, host, returncode = make_cluster(yamlfile, release)
        if returncode:
            return returncode
        sys.stdout.write('Set up cluster on '+host+'\n' )
        setup_realname_crushmap(host)
        if not install_repokey(host, flavor) or \
           not install_repo(host, release, flavor) or \
           not install_package('calamari-agent', host, flavor) or \
           not install_package('calamari-restapi', host, flavor) or \
           not install_package('calamari-webapp', host, flavor):
            return 1
        #XXX how do I do this outside the GUI?
        #setup_localhost_cluster(host)
        webbrowser.open('http://{host}/dashboard'.format(host))
        sys.stdout.write('Hit <return> to tear down\n')
        _ = sys.stdin.readline()
        # kill teuthology, vm
        proc.stdin.close()

    finally:
        os.unlink(yamlfile)

if __name__ == '__main__':
    sys.exit(main())
