#!/usr/bin/env python

'''
Add a user to the htpasswd file for Inktank package access.

1) ask for a username if argument not supplied
2) reject reserved characters (accept only alphanumeric, -_.~)
3) generate a password from the above reserved characters
4) back up the current htpasswd file
5) add the new user/password with htpasswd -b
6) echo the new username/password (plaintext) for communication to customer
'''

HTPASSWD='/home/inktank_site/htpasswd-packages'
SITE_USER='inktank_site'

import grp
import os
import pwd
import random
import shutil
import string
import sys

SITE_UID=pwd.getpwnam(SITE_USER)[2]
SITE_GID=pwd.getpwnam(SITE_USER)[3]
SITE_GROUP=grp.getgrgid(SITE_GID)[0]

VALIDSET=frozenset(set(string.ascii_letters) | set(string.digits) | set('-_.~'))
VALIDSTR=''.join(c for c in VALIDSET)
VALIDSET_DESC='alphanumeric and -_.~'

def valid(s):
    ''' Check that all chars of s are in VALIDSET '''
    return len(set(s) & VALIDSET) == len(set(s))

def generate_password():
    ''' Very dumb 20-character password generation '''
    random.seed()
    return ''.join(random.choice(VALIDSTR) for _ in xrange(20))

def check_ownership(path):
    ''' warn if path not owned by SITE_UID (iff it exists) '''
    if not os.path.exists(path):
        return
    statinfo = os.stat(path)
    if statinfo.st_uid != SITE_UID or statinfo.st_gid != SITE_GID:
        msg='{path} not owned by {user}:{group}'.format(
            path=path,
            user=SITE_USER,
            group=SITE_GROUP
        )
        print >> sys.stderr, msg

def backup_file(path):
    ''' create "path.old" if path exists '''
    if os.path.exists(path):
        # replaces dst, preserves perms/owners
        shutil.copy2(path, path + '.old')

def update_htpasswd(path, username, password):
    ''' use htpasswd -b to add username/password to path '''
    opts = '-b'
    if not os.path.exists:
        opts += ' -c'
    exitcode = os.system(
        'htpasswd {opts} {htpasswd} {username} {password}'.format(
            opts=opts,
            htpasswd=path,
            username=username,
            password=password
        )
    )
    if not exitcode:
        print 'User {username}\nPassword: {password}'.format(
            username=username, password=password)
    return exitcode

def main():
    try:
        username = sys.argv[1]
    except IndexError:
        username = None

    while not username:
        sys.stdout.write('Enter username: ')
        username = sys.stdin.readline()
        username = username[:-1]
        if not valid(username):
            print "Invalid characters in username; use ", VALIDSET_DESC
            username = None

    password = generate_password()

    print 'Username: {username}  Password: {password}'.format(
        username=username, password=password)

    check_ownership(HTPASSWD)
    backup_file(HTPASSWD)
    return update_htpasswd(HTPASSWD, username, password)

if __name__ == '__main__':
    sys.exit(main())
