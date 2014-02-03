
import re
import os
import subprocess


BASE = "/var/log"


def _resolve(base, subpath):
    path = os.path.normpath(os.path.realpath(os.path.join(base, subpath)))
    if not path.startswith(base):
        raise ValueError("Forbidden to us subpath with ../ or symlinks outside base")
    else:
        return path


def _is_log_file(path):
    """
    Checks for indications this isn't a log file of interest,
    such as not being a normal file, ending in a number, ending in .gz
    """
    if not os.path.isfile(path):
        return False

    if path.endswith(".gz") or path.endswith(".bz2") or path.endswith(".zip"):
        return False

    if re.match(".+\d+$", path):
        return False

    return True


def list_logs(subpath):
    """
    Recursively list log files within /var/log, or
    a subpath therein if subpath is not '.'

    :return a list of strings which are paths relative to /var/log
    """

    path = _resolve(BASE, subpath)
    if not os.path.isdir(path):
        raise IOError("'%s' not found or not a directory" % subpath)

    files = os.listdir(path)
    files = [os.path.join(path, f) for f in files]

    log_files = [f for f in files if _is_log_file(f)]
    log_files = [r[len(BASE) + 1:] for r in log_files]

    sub_dirs = [f for f in files if os.path.isdir(f)]
    sub_dirs = [f[len(BASE) + 1:] for f in sub_dirs]
    for subdir in sub_dirs:
        log_files.extend(list_logs(subdir))

    return log_files


def tail(subpath, n_lines):
    """
    Return a string of the last n_lines lines of a log file

    :param subpath: Path relative to the log directory e.g. ceph/ceph.log
    :param n_lines: Number of lines
    :return a string containing n_lines or fewer lines
    """
    path = _resolve(BASE, subpath)
    if not os.path.isfile(path):
        raise IOError("'%s' not found or not an ordinary file" % path)

    # To emit exception if they pass something naughty, rather than have `tail`
    # experience an error
    n_lines = int(n_lines)

    p = subprocess.Popen(["tail", "-n", str(n_lines), path], stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout
