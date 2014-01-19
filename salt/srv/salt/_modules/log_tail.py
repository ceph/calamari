
import glob
import os
import subprocess


BASE = "/var/log"
LOG_GLOB = "*.log"


def _resolve(base, subpath):
    path = os.path.normpath(os.path.realpath(os.path.join(base, subpath)))
    if not path.startswith(base):
        raise ValueError("Forbidden to us subpath with ../ or symlinks outside base")
    else:
        return path


def list_logs(subpath):
    """
    List files ending .log within /var/log

    :return a list of strings
    """
    path = _resolve(BASE, subpath)
    if not os.path.isdir(path):
        raise IOError("'%s' not found or not a directory" % subpath)

    result = glob.glob(os.path.join(path, LOG_GLOB))
    return [r[len(path) + 1:] for r in result]


def tail(subpath, n_lines):
    """
    Return a string of the last n_lines lines of a log file

    :param subpath: Path relative to the log directory e.g. ceph/ceph.log
    :param n_lines: Number of lines
    :return a string containing n_lines or fewer lines
    """
    path = _resolve(BASE, subpath)
    if not os.path.isfile(path):
        raise IOError("'%s' not found or not an ordinary file")

    # To emit exception if they pass something naughty, rather than have `tail`
    # experience an error
    n_lines = int(n_lines)

    p = subprocess.Popen(["tail", "-n", str(n_lines), path], stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout
