
from calamari_common.remote.mon_remote import MonRemote
from calamari_common.remote.salt_remote import SaltRemote
from calamari_common.remote.base import Unavailable  # noqa


# This is where we would be switching between different Remote
# implementations based on configuration.
def get_remote():
    return MonRemote()
    #return SaltRemote()
