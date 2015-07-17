Setting up the Overcloud Network
================================

Once you have deployed the overcloud controller, you need to configure the
overcloud Neutron service. For full documentation on how to do this, see the
Neutron documentation.

.. _basic_network_setup:

Basic Overcloud Networking
--------------------------

For a simple deployment, like the deployment in the Basic Deployment chapter,
you can set up a simple configuration with the external network on the same
subnet as the internal network, in this case 192.0.2.0/24.

To create this, connect to the Undercloud server as the ``stack`` user and
make a file called ``overcloud-network.json`` with the Neutron configuration::

    $ echo "{
        "float": {
            "cidr": "10.0.0.0/8",
            "name": "default-net",
            "nameserver": "8.8.8.8"
        },
        "external": {
            "name": "ext-net",
            "cidr": "192.0.2.0/24",
            "allocation_start": "192.0.2.45",
            "allocation_end": "192.0.2.64",
            "gateway": "192.0.2.1"
        }
    }" > ~/overcloud-network.json


Then source the ``overcloudrc``, and run ``setup-neutron``::

    $ source ~/overcloudrc

    $ setup-neutron -n ~/overcloud-network.json

You can confirm that the networks were created with ``neutron net-list``::

    $ neutron net-list
    +--------------------------------------+-------------+---------------------------------------------------+
    | id                                   | name        | subnets                                           |
    +--------------------------------------+-------------+---------------------------------------------------+
    | d474fe1f-222d-4e32-802b-cde86e746a2a | ext-net     | 01c5f621-1e0f-4b9d-9c30-7dc59592a52f 192.0.2.0/24 |
    | d4746a34-76a4-4b88-8540-6c1f6fd6acb1 | default-net | 4c85b94d-f868-4300-bbbc-8c499cdbbe5e 10.0.0.0/8   |
    +--------------------------------------+-------------+---------------------------------------------------+
