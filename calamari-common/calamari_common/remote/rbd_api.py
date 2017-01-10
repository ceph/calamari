import rados
import rbd

RADOS_NAME = 'client.admin'
RBD_TIMEOUT = 20
RBD_COMMAND = ['create_image', 'remove_image', 'rename_image']


class RbdApi(object):
    """
    This Class is a safe wrapper of librbd.
    Provide thin RBD operation interfaces.
    """

    def __init__(self, cluster_name="ceph"):
        self._cluster_name = cluster_name
        self._rbd_inst = rbd.RBD()
        self._ioctx = None
        self._dest_ioctx = None
        self._image = None
        self._result = {}

    def create_image(self, arg_dict):
        """
        Create an rbd image. The arg_dict should have the follow attributes.
        Required parameters:
            "pool_name": the name of context in which to create the image
            "image_name": what the image is called
            "size": how big the image is in bytes
        Optional parameters:
            "order": the image is split into (2**order) byte objects, default is None
            "old_format": whether to create an old-style image that
                           is accessible by old clients, but can't
                           use more advanced features like layering.
                        default is True
            "features": bitmask of features to enable, default is 0
            "stripe_unit": stripe unit in bytes (default 0 for object size), default is 0
            "stripe_count": objects to stripe over before looping, default is 0
       """
        order = arg_dict.get('order', None)
        old_format = arg_dict.get('old_format', True)
        features = arg_dict.get('features', 0)
        stripe_unit = arg_dict.get('stripe_unit', 0)
        stripe_count = arg_dict.get('stripe_count', 0)
        self._rbd_inst.create(self._ioctx, arg_dict['image_name'], arg_dict['size'], order,
                              old_format, features, stripe_unit, stripe_count)

    def remove_image(self, arg_dict):
        """
        Delete an RBD image. 
        """
        self._rbd_inst.remove(self._ioctx, arg_dict['image_name'])

    def image_resize(self, arg_dict):
        """
        Change the size of the image.

         param size: the new size of the image
         type size: int
        """
        self._image.resize(arg_dict['size'])

    def copy_image(self, arg_dict):
        """
        Copy the image to another location.

        param dest_ioctx: determines which pool to copy into
        type dest_ioctx: :class:`rados.Ioctx`
        param dest_name: the name of the copy
        type dest_name: str
        raises: :class:`ImageExists`
        """
        self._image.copy(self._dest_ioctx, arg_dict['dest_image'])

    def rename_image(self, arg_dict):
        """
        Rename an RBD image.
        """
        self._rbd_inst.rename(self._ioctx, arg_dict['old_name'], arg_dict['new_name'])

    def create_snap_shot(self, arg_dict):
        """
        Create a snapshot of the image.

        :param snap_name: the name of the snapshot
        :type snap_name: str
        :raises: :class:`ImageExists`
        """
        self._image.create_snap(arg_dict['snap_name'])

    def remove_snap_shot(self, arg_dict):
        """
        Delete a snapshot of the image.

        :param snap_name: the name of the snapshot
        :type snap_name: str
        :raises: :class:`IOError`, :class:`ImageBusy`
        """
        self._image.remove_snap(arg_dict['snap_name'])

    def protect_snap(self, arg_dict):
        """
        Mark a snapshot as protected. This means it can't be deleted
        until it is unprotected.

        :param snap_name: the snapshot to protect
        :type snap_name: str
        :raises: :class:`IOError`, :class:`ImageNotFound`
        """
        self._image.protect_snap(arg_dict['snap_name'])

    def unprotect_snap(self, arg_dict):
        """
        Mark a snapshot unprotected. This allows it to be deleted if
        it was protected.
        :param snap_name: the snapshot to unprotect
        :type snap_name: str
        :raises: :class:`IOError`, :class:`ImageNotFound`
        """
        self._image.unprotect_snap(arg_dict['snap_name'])

    def roll_back_snapshot(self, arg_dict):
        """
        Revert the image to its contents at a snapshot. This is a
        potentially expensive operation, since it rolls back each
        object individually.
        """
        self._image.rollback_to_snap(arg_dict['snap_name'])

    def clone_image(self, arg_dict):
        """
        Clone a parent rbd snapshot into a COW sparse child.
        """
        features = arg_dict.get('features', 0)
        order = arg_dict.get('order', None)
        self._rbd_inst.clone(self._ioctx, arg_dict['image_name'], arg_dict['snap_name'], self._dest_ioctx,
                             arg_dict['clone_image'], features, order)

    def flatten_image(self, arg_dict):
        """
        Flatten clone image (copy all blocks from parent to child)
        """
        self._image.flatten()

    def old_format(self, arg_dict):
        """
        Find out whether the image uses the old RBD format.

        :returns: bool - whether the image uses the old RBD format
        """
        is_old = self._image.old_format()
        self._result[arg_dict['image_name']].update({'old_format': is_old})

    def list_snaps(self, arg_dict):
        """
        Iterate over the snapshots of an image.

        :returns: :class:`SnapIterator`
        """
        snap_info = {}
        for elem in self._image.list_snaps():
            elem['protected'] = self._image.is_protected_snap(elem['name'])
            snap_info[elem['name']] = elem
        self._result[arg_dict['image_name']].update({'snaps': snap_info})

    def get_image_stat(self, arg_dict):
        """
        Get information about the image. Currently parent pool and
        parent name are always -1 and ''.

        :returns: dict - contains the following keys:

            * ``size`` (int) - the size of the image in bytes

            * ``obj_size`` (int) - the size of each object that comprises the
              image

            * ``num_objs`` (int) - the number of objects in the image

            * ``order`` (int) - log_2(object_size)

            * ``block_name_prefix`` (str) - the prefix of the RADOS objects used
              to store the image

            * ``parent_pool`` (int) - deprecated

            * ``parent_name``  (str) - deprecated

            See also :meth:`format` and :meth:`features`.

        """
        self._result[arg_dict['image_name']].update({'stat': self._image.stat()})

    def get_image_parent_info(self, arg_dict):
        """
        Get information about a cloned image's parent (if any)

        :returns: tuple - ``(pool name, image name, snapshot name)`` components
                  of the parent image
        :raises: :class:`ImageNotFound` if the image doesn't have a parent
        """
        self._result[arg_dict['image_name']].update({'parent': self._image.parent_info()})

    def parse_rbd_commands(self, commands):
        self._result = {}
        for i, (prefix, arg_dict) in enumerate(commands):

            if not hasattr(self, prefix):
                continue

            func = getattr(self, prefix)
            cluster_handle = rados.Rados(name=RADOS_NAME, clustername=self._cluster_name, conffile='')
            cluster_handle.connect(timeout=RBD_TIMEOUT)

            try:
                self._ioctx = cluster_handle.open_ioctx(arg_dict['pool_name'])
                self._dest_ioctx = cluster_handle.open_ioctx(arg_dict['dest_pool']) \
                    if arg_dict.has_key('dest_pool') else None

                try:

                    if prefix not in RBD_COMMAND:
                        name = arg_dict['image_name']
                        snap_shot = arg_dict.get('snap_shot', None)
                        read_only = arg_dict.get('read_only', False)
                        self._result[name] = self._result.get(name, {})
                        self._image = rbd.Image(self._ioctx, arg_dict['image_name'], snap_shot, read_only)

                    try:
                        func(arg_dict)
                    finally:
                        self._image.close() if self._image else None

                finally:
                    self._dest_ioctx.close() if self._dest_ioctx else None
                    self._ioctx.close() if self._ioctx else None

            finally:
                cluster_handle.shutdown()

        return self._result