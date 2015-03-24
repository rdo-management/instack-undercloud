Deploying the Overcloud
=======================

All the commands on this page require that the appropriate stackrc file has
been sourced into the environment::

    source stackrc

Registering Nodes
-----------------

Register nodes for your deployment with Ironic::

    instack-ironic-deployment --nodes-json instackenv.json --register-nodes

Discovering Nodes
-----------------

Discover hardware attributes of nodes and match them to a deployment profile::

    instack-ironic-deployment --discover-nodes

Check what profiles were matched for the discovered nodes::

    instack-ironic-deployment --show-profile

Ready-state configuration (for Dell DRAC nodes)
-----------------------------------------------

Configure BIOS based on the deployment profile::

    instack-ironic-deployment --configure-bios

.. note:: The BIOS changes will be applied during the first boot.

Create root RAID volume based on the deployment profile::

    instack-ironic-deployment --configure-root-raid-volume

.. note:: The nodes will be restarted and RAID configuration will happen during
   the first boot.

Discover root block device::

    instack-ironic-deployment --discover-nodes

Create non-root RAID volumes based on the deployment profile::

    instack-ironic-deployment --configure-nonroot-raid-volumes

.. note:: The nodes will be restarted and RAID configuration will happen during
   the first boot.

Deploying Nodes
---------------

Create the necessary flavors::

    instack-ironic-deployment --setup-flavors

If installing on baremetal, copy the sample overcloudrc file and edit to reflect your environment. Then source this file::

    cp /usr/share/instack-undercloud/deploy-baremetal-overcloudrc ~/deploy-overcloudrc
    source deploy-overcloudrc

Deploy the the *openstack-full* image (default of 1 compute and 1 control)::

    instack-deploy-overcloud

Working with the Overcloud
--------------------------

To generate an appropriate rc file for interacting the overcloud, run::

    instack-create-overcloudrc

This will create an `overcloudrc` file in the current user's home directory
which can be sourced to set up the client environment for the overcloud.


Redeploying the Overcloud
-------------------------

The overcloud can be redeployed when desired.

#. First, delete any existing Overcloud::

    heat stack-delete overcloud

#. Confirm the Overcloud has deleted. It may take a few minutes to delete::

    # This command should show no stack once the Delete has completed
    heat stack-list

#. Although not required, discovery can be rerun. Reset the state file and then rediscover nodes::

    sudo cp /usr/libexec/os-apply-config/templates/etc/edeploy/state /etc/edeploy/state
    instack-ironic-deployment --discover-nodes

#. Deploy the Overcloud again::

    instack-deploy-overcloud
