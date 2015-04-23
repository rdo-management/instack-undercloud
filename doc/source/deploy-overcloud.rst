Deploying the Overcloud
=======================

All the commands on this page require that the appropriate stackrc file has
been sourced into the environment::

    source stackrc

Registering Nodes
-----------------

Register nodes for your deployment with Ironic::

    instack-ironic-deployment --nodes-json instackenv.json --register-nodes

.. admonition:: Quintupleo
   :class: quintupleo

   Running ``nova list`` on the host cloud will show that the baremetal nodes
   will be in Status ``SHUTOFF`` after nodes are registered. This indicates
   that the BMC nodes are working as expected.

.. note::
   It's not recommended to delete nodes and/or rerun this command after
   you have proceeded to the next steps. Particularly, if you start discovery
   and then re-register nodes, you won't be able to retry discovery until
   the previous one times out (1 hour by default). If you are having issues
   with nodes after registration, please follow
   :ref:`node_registration_problems`.

Introspecting Nodes
-------------------

Introspect hardware attributes of nodes::

    instack-ironic-deployment --discover-nodes

.. note:: **Introspection has to finish without errors.**
   The process can take up to 5 minutes for VM / 15 minutes for baremetal. If
   the process takes longer, see :ref:`introspection_problems`.

.. admonition:: Quintupleo
   :class: quintupleo

   Horizon in the host OpenStack can be used to view the console of the
   baremetal nodes to see the progress of booting the discovery images.



Ready-state configuration
-------------------------

.. admonition:: Baremetal
   :class: baremetal

   Some hardware has additional setup available, using its vendor-specific management
   interface.  See the :doc:`/vendor-specific` for details.

Deploying Nodes
---------------

Create the necessary flavors::

    instack-ironic-deployment --setup-flavors

.. admonition:: Baremetal
   :class: baremetal

   Copy the sample overcloudrc file and edit to reflect your environment. Then source this file::

      cp /usr/share/instack-undercloud/deploy-baremetal-overcloudrc ~/deploy-overcloudrc
      source deploy-overcloudrc

.. admonition:: Quintupleo
   :class: quintupleo-tag

   Copy the sample overcloudrc file then source it::

      cp /usr/share/instack-undercloud/deploy-baremetal-overcloudrc ~/deploy-overcloudrc
      source deploy-overcloudrc

Deploy the overcloud (default of 1 compute and 1 control):

.. admonition:: RHEL Satellite Registration
   :class: satellite

   To register the Overcloud nodes to a Satellite define the following
   variables. Only using an activation key is supported when registering to
   Satellite, username/password is not supported for security reasons. The
   activation key must enable the repos shown::

          export REG_METHOD=satellite
          # REG_SAT_URL should be in the format of:
          # http://<satellite-hostname>
          export REG_SAT_URL="[satellite url]"
          export REG_ORG="[satellite org]"
          export REG_ACTIVATION_KEY="[activation key]"
          # Activation key must enable these repos:
          # rhel-7-server-rpms
          # rhel-7-server-optional-rpms
          # rhel-7-server-extras-rpms
          # rhel-7-server-openstack-6.0-rpms

.. admonition:: Ceph
   :class: ceph

   When deploying Ceph, specify the number of Ceph OSD nodes to be deployed
   with::

       export CEPHSTORAGESCALE=1

   By default when Ceph is enabled the Cinder iSCSI back-end is disabled. This
   behavior may be changed by setting the environment variable::

       export CINDER_ISCSI=1

::

    instack-deploy-overcloud --tuskar

Working with the Overcloud
--------------------------

``instack-deploy-overcloud`` generates an overcloudrc file appropriate for
interacting with the deployed overcloud in the current user's home directory.
To use it, simply source the file::

    source ~/overcloudrc

To return to working with the undercloud, source the stackrc file again::

    source ~/stackrc

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

    instack-deploy-overcloud --tuskar
