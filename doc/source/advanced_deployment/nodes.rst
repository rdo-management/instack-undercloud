Node management
===============

Import Nodes
------------

You can import nodes from JSON or CSV. This tells OpenStack what nodes are
available for usage as overcloud nodes.

.. program:: baremetal import
.. code:: bash

    openstack baremetal import
        [ --json | --csv ]
        <file_in>


.. option:: --json

    Input file is in json format

.. option:: --csv

    Input file is in csv format

.. _baremetal_import-file_in:
.. describe:: <file_in>

    Filename to be imported


JSON File
.........

A JSON file needs to have an array of JSON objects with the following fields:

    * ``pm_type``: The mode of connection to the node. Can be ``IPMI`` or
      ``pxe_ssh``. ``IPMI`` is the normal for baremetal.

    * ``pm_user``: Username for the node's power management.

    * ``pm_password``: Password for the node's power management. For a
      ``pxe_ssh` connection this should be an SSH key.

    * ``pm_addr``: Power management IP for the node.

    * ``mac``: A list of MAC addresses for this node. There needs to be at
      least one, which is the one used for power management of the node.
      (optional)

    * ``cpu``: The number of CPU's in the node. (optional)

    * ``disk``: The size of the disk attached to the node. (optional)

    * ``memory``: The amount of memory in the node. (optional)

    * ``arch``: The CPU architecture. Can be ``"x86_64"`` or ``"i686"``.
        (optional)

The JSON array containing the nodes must either be the root of the JSON file, or
the root must be an object that has the nodes list under a ``"nodes"`` key.
Example::

    [
        {
            "pm_addr": "192.168.122.1",
            "pm_password": "-----BEGIN RSA PRIVATE KEY-----\nFU6%fowIBAAKCAQEArrSs3D1Yzhy5jaTmZhIdsQtyzhlT0U6aSxxgYJBF0BkLQcgcDMzo+SIj\n-----END RSA PRIVATE KEY-----",
            "pm_type": "pxe_ssh",
            "mac": [
                "00:74:4e:63:cd:8e"
            ],
            "pm_user": "root"
        },
        {
            "pm_password": "-----BEGIN RSA PRIVATE KEY-----\nFU6%fowIBAAKCAQEArrSs3D1Yzhy5jaTmZhIdsQtyzhlT0U6aSxxgYJBF0BkLQcgcDMzo+SIj\n-----END RSA PRIVATE KEY-----",
            "pm_type": "pxe_ssh",
            "mac": [
                "00:b4:b7:4f:ee:27"
            ],
            "pm_user": "root",
            "pm_addr": "192.168.122.1"
        }
    ]

The optional fields ``cpu``, ``memory``, ``disk`` and ``arch`` are used to
fill in information about the node configuration, which is later used for
flavor matching. You can leave these out, and instead run the introspection
step below.


CSV File
........

A CSV file must have one node per row with the following columns::

    pm_type, pm_addr, pm_user, pm_password, mac

It should use commas as separators and double quotes as quote characters,
and have no header. Example::

    pxe_ssh,192.168.122.1,root,"KEY1",00:d0:28:4c:e8:e8
    pxe_ssh,192.168.122.1,root,"KEY2",00:7c:ef:3d:eb:60


Node Introspection
------------------

After registering, you will need to run the node introspection.

The node introspection boots up the node vith PXE using a discovery ramdisk
image. That image will introspect the node to find out its hardware
configuration and run benchmarks on it to measure it's performance. This
information is then returned to Ironic, which uses it to match different nodes
to different roles.

The introspection can take a long time, so it's a process running in the
background.

.. program:: baremetal introspection all start
.. code:: bash

    openstack baremetal introspection all start

You must then wait for the instrospection to finish.

.. program:: baremetal introspection all status
.. code:: bash

    openstack baremetal introspection all status

The output is a list of the nodes. If the introspection succeeds, all the nodes
will have ``True`` in the Finished columns, and ``None`` in the Error column::

    +--------------------------------------+----------+-------+
    | Node UUID                            | Finished | Error |
    +--------------------------------------+----------+-------+
    | b25a2f34-22f2-43bd-bb4f-859692e60f7b | True     | None  |
    | 85fe8d51-b148-4445-8275-225a0919b3c1 | True     | None  |
    +--------------------------------------+----------+-------+


You can also start introspection of just one node:

.. program:: baremetal introspection start <UUID>
.. code:: bash

    openstack baremetal introspection start <UUID>


And also here you can get the status for one specific node.

.. program:: baremetal introspection status <UUID>
.. code:: bash

    openstack baremetal introspection status <UUID>


Updating Boot Devices
---------------------

If you rebuild the boot images you need to reconfigure the nodes boot
configuration. You do this with the ``configure boot`` command.

.. program:: baremetal configure boot
.. code:: bash

    openstack baremetal configure boot
