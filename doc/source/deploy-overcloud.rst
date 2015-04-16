Deploying the Overcloud
=======================

All the commands on this page require that the appropriate stackrc file has
been sourced into the environment::

    source stackrc


Register and Introspect Nodes
-----------------------------

Import nodes.json file in order to register multiple nodes at once::

    # instackenv.json file format is not supported at the moment, let's generate valid structure
    jq '.nodes' instackenv.json > nodes.json

    # Register multiple nodes
    openstack baremetal import --json nodes.json

.. note::
   It's not recommended to delete nodes and/or rerun this command after
   you have proceeded to the next steps. Particularly, if you start discovery
   and then re-register nodes, you won't be able to retry discovery until
   the previous one times out (1 hour by default). If you are having issues
   with nodes after registration, please follow :ref:`node_reg_problems`.


Add extra parameters needed for local booting a node when deploying.::

    # Requirements: "bm-deploy-kernel" and "bm-deploy-ramdisk" images are required to be in Glance
    # You can check with `openstack image list`

    openstack baremetal configure boot


.. admonition:: Ceph
   :class: ceph-tag

   When deploying Ceph, you will need to configure the ``edeploy`` plugin so
   that it will assign the ``ceph-storage`` profile to at least one system. To
   do so, you need to **prepend** the following ``('ceph-storage', '1')`` into
   the list of profiles defined in ``/etc/edeploy/state``, before initiating the
   nodes discovery. [#]_

   Example contents of ``/etc/edeploy/state``::

       [('ceph-storage', '1'), ('control', '1'), ('compute', '*')]


Start introspection process of all nodes::

    openstack baremetal introspection all start

After few minutes you can start checking for introspection status::

    openstack baremetal introspection all status


.. note:: **Introspection has to finish without errors.**
   The process can take up to 5 minutes for VM / 15 minutes for baremetal. If
   the process takes longer, see :ref:`discovery_problems`.


Check what profiles were matched for the introspected nodes::

    instack-ironic-deployment --show-profile



Ready-state configuration
-------------------------

.. admonition:: Baremetal
   :class: baremetal-tag

   Some hardware has additional setup available, using its vendor-specific management
   interface.  See the :doc:`/vendor-specific` for details.


Deploy Nodes
------------

Create the necessary flavors::

    instack-ironic-deployment --setup-flavors

.. admonition:: Baremetal
   :class: baremetal-tag

   Copy the sample overcloudrc file and edit to reflect your environment. Then source this file::

      cp /usr/share/instack-undercloud/deploy-baremetal-overcloudrc ~/deploy-overcloudrc
      source deploy-overcloudrc

Deploy the overcloud (default of 1 compute and 1 control):

.. admonition:: Ceph
   :class: ceph-tag

   When deploying Ceph, specify the number of Ceph OSD nodes to be deployed
   with::

       export CEPHSTORAGESCALE=1

::

    instack-deploy-overcloud --tuskar


Work with the Overcloud
-----------------------

``instack-deploy-overcloud`` generates an overcloudrc file appropriate for
interacting with the deployed overcloud in the current user's home directory.
To use it, simply source the file::

    source ~/overcloudrc

To return to working with the undercloud, source the stackrc file again::

    source ~/stackrc


Redeploy the Overcloud
----------------------

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

    instack-deploy-overcloud --tuskar

.. rubric:: Footnotes

.. [#]  In the ``('ceph-storage', '1')`` setting, 1 represents the number of
        systems to be tagged with such a profile as opposed to a boolean
        value.
