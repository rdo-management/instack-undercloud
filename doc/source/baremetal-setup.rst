Baremetal Environment Setup
===========================

instack-undercloud can be deployed in an all baremetal environment. One
baremetal node will be used as the undercloud, and other available baremetal
nodes will be used for the Overcloud deployment.

Minimum System Requirements
---------------------------

In order to produce a usable OpenStack install this setup requires five
baremetal machines: one machine for the undercloud, and one machine for each
Overcloud node.

.. image:: images/InstackSetup.png

The setup requires baremetal machines with the following minimum specifications:

* multi-core CPU
* 4GB memory
* 60GB free disk space

The undercloud machine needs to run RHEL 7.1 x86_64 or CentOS 7 x86_64,
which is discussed more below.

Preparing the Baremetal Environment
-----------------------------------

Networking
^^^^^^^^^^

The overcloud nodes will be deployed from the undercloud machine and therefore the machines need to have have their network settings modified to allow for the overcloud nodes to be PXE boot'ed using the undercloud machine. As such, the setup requires that:

* All overcloud machines in the setup must support IPMI
* A management provisioning network is setup for all of the overcloud machines.
  One NIC from every machine needs to be in the same broadcast domain of the
  provisioning network. In the tested environment, this required setting up a new
  VLAN on the switch. Note that you should use the same NIC on each of the
  overcloud machines ( for example: use the second NIC on each overcloud
  machine). This is because during installation we will need to refer to that NIC
  using a single name across all overcloud machines e.g. em2
* The provisioning network NIC should not be the same NIC that you are using
  for remote connectivity to the undercloud machine. During the undercloud
  installation, a openvswitch bridge will be created for Neutron and the
  provisioning NIC will be bridged to the openvswitch bridge. As such,
  connectivity would be lost if the provisioning NIC was also used for remote
  connectivity to the undercloud machine.
* The overcloud machines can PXE boot off the NIC that is on the private VLAN.
  In the tested environment, this required disabling network booting in the BIOS
  for all NICs other than the one we wanted to boot and then ensuring that the
  chosen NIC is at the top of the boot order (ahead of the local hard disk drive
  and CD/DVD drives).
* For each overcloud machine you have: the MAC address of the NIC that will PXE
  boot on the provisioning network the IPMI information for the machine (i.e. IP
  address of the IPMI NIC, IPMI username and password)

Refer to the following diagram for more information

.. image:: images/TripleO_Network_Diagram_.jpg

Setting Up The Undercloud Machine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Select a machine within the baremetal environment on which to install the
   undercloud.
#. Install RHEL 7.1 x86_64 or CentOS 7 x86_64 on this machine.
#. If needed, create a non-root user with sudo access to use for installing the
   Undercloud::

        sudo useradd stack
        sudo passwd stack  # specify a password
        echo "stack ALL=(root) NOPASSWD:ALL" | sudo tee -a /etc/sudoers.d/stack
        sudo chmod 0440 /etc/sudoers.d/stack

#. Create a json file describing your baremetal nodes.  For example::

    {
        "nodes":[
            {
                "pm_type":"pxe_ipmitool",
                "mac":[
                    "fa:16:3e:2a:0e:36"
                ],
                "cpu":"2",
                "memory":"4096",
                "disk":"40",
                "arch":"x86_64",
                "pm_user":"admin",
                "pm_password":"password",
                "pm_addr":"10.0.0.8"
            },
            {
                "pm_type":"pxe_ipmitool",
                "mac":[
                    "fa:16:3e:da:39:c9"
                ],
                "cpu":"2",
                "memory":"4096",
                "disk":"40",
                "arch":"x86_64",
                "pm_user":"admin",
                "pm_password":"password",
                "pm_addr":"10.0.0.15"
            },
            {
                "pm_type":"pxe_ipmitool",
                "mac":[
                    "fa:16:3e:51:9b:68"
                ],
                "cpu":"2",
                "memory":"4096",
                "disk":"40",
                "arch":"x86_64",
                "pm_user":"admin",
                "pm_password":"password",
                "pm_addr":"10.0.0.16"
            }
        ]
    }
.. only:: external

   .. admonition:: RHEL
      :class: rhel-tag

       Register the host machine using Subscription Management::

          sudo subscription-manager register --username="[your username]" --password="[your password]"
          # Find this with `subscription-manager list --available`
          sudo subscription-manager attach --pool="[pool id]"
          # Verify repositories are available
          sudo subscription-manager repos --list
          # Enable repositories needed
          sudo subscription-manager repos --enable=rhel-7-server-rpms \
              --enable=rhel-7-server-optional-rpms --enable=rhel-7-server-extras-rpms \
              --enable=rhel-7-server-openstack-6.0-rpms
