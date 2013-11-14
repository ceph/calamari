

class CephControl(object):
    """
    Interface for tests to control one or more Ceph clusters under test.

    This can either be controlling the minion-sim, running unprivileged
    in a development environment, or it can be controlling a real life
    Ceph cluster.

    Some configuration arguments may be interpreted by a
    dev implementation as a "simulate this", while a real-cluster
    implementation might interpret them as "I require this state, skip
    the test if this cluster can't handle that".
    """

    def configure(self):
        """
        Tell me about the kind of system you would like
        """
        raise NotImplementedError()


class DevCephControl(CephControl):
    pass


class RealCephControl(CephControl):
    """
    TODO: hook into a real life ceph cluster (provisioned with teuthology?)
    """
    pass
