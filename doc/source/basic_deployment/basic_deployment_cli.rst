Basic Deployment (CLI)
======================

With these few steps you will be able to simply deploy RDO to your environment
using our defaults in a few steps.


Prepare Your Environment
------------------------

#. Make sure you have your environment ready and undercloud running:

   * :doc:`../environments/environments`
   * :doc:`../installation/installing`

#. Log into your undercloud (instack) virtual machine as non-root user::

    ssh root@<rdo-manager-machine>

    su - stack

#. In order to use CLI commands easily you need to source needed environment
   variables::

    source stackrc


Get Images
----------

.. note::

       If you already have images built, perhaps from a previous installation of
       RDO Manager, you can simply copy those image files into your regular user's
       home directory and skip this section.

       If you do this, be aware that sometimes newer versions of RDO Manager do not
       work with older images, so if the deployment fails it may be necessary to
       delete the older images and restart the process from this step.

       The image files required are::

           deploy-ramdisk-ironic.initramfs
           deploy-ramdisk-ironic.kernel
           discovery-ramdisk.initramfs
           discovery-ramdisk.kernel
           overcloud-full.initrd
           overcloud-full.qcow2
           overcloud-full.vmlinuz

Images must be built prior to doing a deployment. A discovery ramdisk,
deployment ramdisk, and openstack-full image can all be built using
instack-undercloud.

It's recommended to build images on the installed undercloud directly since all
the dependencies are already present.

The following steps can be used to build images. They should be run as the same
non-root user that was used to install the undercloud.


#. Choose image operating system:

   The built images will automatically have the same base OS as the
   running undercloud. To choose a different OS use one of the following
   commands (make sure you have your OS specific content visible):

   .. admonition:: CentOS
      :class: centos

      ::

          export NODE_DIST=centos7

   .. admonition:: RHEL
      :class: rhel

      ::

          export NODE_DIST=rhel7


#. Build the required images:

   .. only:: internal

      .. admonition:: RHEL
         :class: rhel

         Download the RHEL 7.1 cloud image or copy it over from a different location,
         and define the needed environment variable for RHEL 7.1 prior to running
         ``openstack overcloud image build --all``::

             IMAGE=http://download.devel.redhat.com/brewroot/packages/rhel-guest-image/7.1/20150224.0/images/rhel-guest-image-7.1-20150224.0.x86_64.qcow2
             curl -O $IMAGE
             export DIB_LOCAL_IMAGE=`basename $IMAGE`
             # Enable RHOS
             export USE_DELOREAN_TRUNK=0
             export RHOS=1
             export DIB_YUM_REPO_CONF="/etc/yum.repos.d/rhos-release-7-director-rhel-7.1.repo /etc/yum.repos.d/rhos-release-7-rhel-7.1.repo"

   .. only:: external

    .. admonition:: RHEL
       :class: rhel

       Download the RHEL 7.1 cloud image or copy it over from a different location,
       for example:
       https://access.redhat.com/downloads/content/69/ver=/rhel---7/7.1/x86_64/product-downloads,
       and define the needed environment variables for RHEL 7.1 prior to running
       ``openstack overcloud image build --all``::

            export DIB_LOCAL_IMAGE=rhel-guest-image-7.1-20150224.0.x86_64.qcow2

    .. admonition:: RHEL Portal Registration
       :class: portal

       To register the image builds to the Red Hat Portal define the following variables::

              export REG_METHOD=portal
              export REG_USER="[your username]"
              export REG_PASSWORD="[your password]"
              # Find this with `sudo subscription-manager list --available`
              export REG_POOL_ID="[pool id]"
              export REG_REPOS="rhel-7-server-rpms rhel-7-server-extras-rpms rhel-ha-for-rhel-7-server-rpms \
                  rhel-7-server-optional-rpms rhel-7-server-openstack-6.0-rpms"

    .. admonition:: RHEL Satellite Registration
       :class: satellite

       To register the image builds to a Satellite define the following
       variables. Only using an activation key is supported when registering to
       Satellite, username/password is not supported for security reasons. The
       activation key must enable the repos shown::

              export REG_METHOD=satellite
              # REG_SAT_URL should be in the format of:
              # http://<satellite-hostname>
              export REG_SAT_URL="[satellite url]"
              export REG_ORG="[satellite org]"
              # Activation key must enable these repos:
              # rhel-7-server-rpms
              # rhel-7-server-optional-rpms
              # rhel-7-server-extras-rpms
              # rhel-7-server-openstack-6.0-rpms
              export REG_ACTIVATION_KEY="[activation key]"

 .. note ::
    By default, images are built with the latest RDO-Manager Trunk repo which has passed CI. If you need to manually test packages before CI has passed, you can use:

    ::

      export DELOREAN_TRUNK_MGT_REPO="http://trunk-mgt.rdoproject.org/centos-kilo/current"

 ::

   openstack overcloud image build --all


 .. note::
    This script will build **overcloud-full** images (\*.qcow2, \*.initrd,
    \*.vmlinuz), **deploy-ramdisk-ironic** images (\*.initramfs, \*.kernel),
    **discovery-ramdisk** images (\*.initramfs, \*.kernel) and **testing**
    fedora-user.qcow2 (which is always Fedora based).


Upload Images
-------------

Load the images into the undercloud Glance::

    openstack overcloud image upload


Register Nodes
--------------

Register nodes for your deployment with Ironic::

    openstack baremetal import --json instackenv.json

.. note::
   It's not recommended to delete nodes and/or rerun this command after
   you have proceeded to the next steps. Particularly, if you start introspection
   and then re-register nodes, you won't be able to retry introspection until
   the previous one times out (1 hour by default). If you are having issues
   with nodes after registration, please follow
   :ref:`node_registration_problems`.

Assign kernel and ramdisk to nodes::

    openstack baremetal configure boot


Introspect Nodes
----------------

Introspect hardware attributes of nodes::

    openstack baremetal introspection bulk start

.. note:: **Introspection has to finish without errors.**
   The process can take up to 5 minutes for VM / 15 minutes for baremetal. If
   the process takes longer, see :ref:`introspection_problems`.


Create Flavors
--------------

Create the necessary flavor::

    openstack flavor create --id auto --ram 4096 --disk 40 --vcpus 1 baremetal
    openstack flavor set --property "cpu_arch"="x86_64" --property "capabilities:boot_option"="local" baremetal


Deploy the Overcloud
--------------------

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

#. To get the deployment plan UUID (plan name is "overcloud"), run::

    openstack management plan list

#. Deploy the overcloud:

   By default 1 compute and 1 control node will be deployed, with networking
   configured for the virtual environment.  To customize this, see the output of::

        openstack help overcloud deploy

   .. admonition:: Ceph
      :class: ceph

      When deploying Ceph, specify the number of Ceph OSD nodes to be deployed
      by passing::

          --ceph-storage-scale <number of nodes>

      to the deploy command below.

      By default when Ceph is enabled the Cinder LVM back-end is disabled. This
      behavior may be changed by also passing::

          --cinder-lvm

   ::

      openstack overcloud deploy --plan-uuid "[uuid]"



Post-Deployment
---------------


Access the Overcloud
^^^^^^^^^^^^^^^^^^^^

``openstack overcloud deploy`` generates an overcloudrc file appropriate for
interacting with the deployed overcloud in the current user's home directory.
To use it, simply source the file::

    source ~/overcloudrc

To return to working with the undercloud, source the stackrc file again::

    source ~/stackrc


Validate the Overcloud
^^^^^^^^^^^^^^^^^^^^^^
To verify the Overcloud by running Tempest::

    openstack overcloud validate --overcloud-auth-url $OS_AUTH_URL \
                                 --overcloud-admin-password $OS_PASSWORD

.. note:: The full Tempest test suite might take hours to run on a single CPU.

To run only a part of the Tempest test suite (eg. tests with ``smoke`` tag)::

    openstack overcloud validate --overcloud-auth-url $OS_AUTH_URL \
                                 --overcloud-admin-password $OS_PASSWORD \
                                 --tempest-args smoke


Redeploy the Overcloud
^^^^^^^^^^^^^^^^^^^^^^

The overcloud can be redeployed when desired.

#. First, delete any existing Overcloud::

    heat stack-delete overcloud

#. Confirm the Overcloud has deleted. It may take a few minutes to delete::

    # This command should show no stack once the Delete has completed
    heat stack-list

#. Although not required, introspection can be rerun::

    openstack baremetal introspection bulk start

#. Deploy the Overcloud again::

    openstack overcloud deploy --plan-uuid "[uuid]"
