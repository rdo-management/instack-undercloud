Getting Started with RDO-Manager
================================

With these few steps you will be able to simply deploy RDO to your environment
using our POC defaults in few steps.


Prepare Your Environment
------------------------

#. Make sure you have your environemnt ready and undercloud running:

   * :doc:`../environments/environments`
   * :doc:`../install-undercloud`

#. Log into your undercloud (instack) virtual machine as non-root user::

    ssh root@<rdo-manager-machine>

    su - stack

#. In order to use CLI commands you need to source needed passwords::

    source stackrc


Get Images
----------

..
    You can simply download and use provided overcloud images to get started::

        sudo yum install -y wget
        wget --no-verbose --no-parent --recursive --level=1 --no-directories --reject 'index.html*' -P ./images/ http://fedorapeople.org/...

    .. note:: If you happen to need to build overcloud images, please follow these
       steps: :ref:`building_images`


At the moment we have to build images manually, please follow:

* :ref:`building_images`

.. _post_building_images:


Register Nodes
--------------

Register nodes for your deployment with Ironic::

    instack-ironic-deployment --nodes-json instackenv.json --register-nodes

.. note::
   It's not recommended to delete nodes and/or rerun this command after
   you have proceeded to the next steps. Particularly, if you start discovery
   and then re-register nodes, you won't be able to retry discovery until
   the previous one times out (1 hour by default). If you are having issues
   with nodes after registration, please follow
   :ref:`node_registration_problems`.


Introspect Nodes
----------------

Introspect hardware attributes of nodes::

    instack-ironic-deployment --discover-nodes

.. note:: **Introspection has to finish without errors.**
   The process can take up to 5 minutes for VM / 15 minutes for baremetal. If
   the process takes longer, see :ref:`introspection_problems`.


Create Flavors
--------------

Create the necessary flavors::

    instack-ironic-deployment --setup-flavors


Deploy Overcloud
-----------------

.. admonition:: Baremetal
   :class: baremetal

   Copy the sample overcloudrc file and edit to reflect your environment. Then source this file::

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


Post-Deployment
---------------

Testing Overcloud
^^^^^^^^^^^^^^^^^

Trigger Instack testing script::

    instack-test-overcloud


Working with Overcloud
^^^^^^^^^^^^^^^^^^^^^^

``instack-deploy-overcloud`` generates an overcloudrc file appropriate for
interacting with the deployed overcloud in the current user's home directory.
To use it, simply source the file::

    source ~/overcloudrc

To return to working with the undercloud, source the stackrc file again::

    source ~/stackrc


Redeploying Overcloud
^^^^^^^^^^^^^^^^^^^^^

The overcloud can be redeployed when desired.

#. First, delete any existing Overcloud::

    heat stack-delete overcloud

#. Confirm the Overcloud has deleted. It may take a few minutes to delete::

    # This command should show no stack once the Delete has completed
    heat stack-list

#. Although not required, introspection can be rerun::

    instack-ironic-deployment --discover-nodes

#. Deploy the Overcloud again::

    instack-deploy-overcloud --tuskar
