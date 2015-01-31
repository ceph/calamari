Administering users and assigning roles:
========================================

Calamari is a multiuser system and has user roles.

What is it:
-----------
There are three roles available in calamari readonly, read/write, and superuser. These user credentials can be used to login to the dashboard and access the API.
users with the readonly role may see every resource requests to PUT POST PATCH or DELETE in the API will be forbidden. The UI will also hide resources based on the Allow response header. 

Read/write user role has the ability to see every resource and add or changes any resource that is not users and roles.

The superuser role is not limited in any capability that calamari posses. This role can add and modify users and associate roles with users.



How do I administer it:
-----------------------

calamari-ctl will be the interface for creating, modifying, and, removing users.
It will also allow users to be assigned a role.


Creating a user:
^^^^^^^^^^^^^^^^

.. code-block:: bash

   calamari-ctl add_user alice --email aprogrammer@planetearth.org

This will add alice as a read/write user by default. Notice that we set no password. Alice is currently a locked account. Accounts without passwords are not allowed access.

.. code-block:: bash

    calamari-ctl change_password alice

Username is required to be unique.

Disable/enable a user:
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    calmari-ctl disable_user alice
    calmari-ctl enable_user alice


Assigning a role to a user:
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    calamari-ctl assign_role alice --role readonly

Users and roles form a Many to One relationship. Users only have one role. A user may only be assigned one role at a time.

