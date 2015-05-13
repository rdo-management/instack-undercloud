Quintupleo Environment Setup
================================

instack-undercloud can be deployed in an OpenStack environment which is set up
to behave like a baremetal environment.

Minimum System Requirements
---------------------------

This setup is aimed at a Juno or later OpenStack host cloud which has the
Heat orchestration service available. Neutron is currently assumed for the
networking. This cloud requires applying patches which are not appropriate
for a production cloud.

.. warning::
    It is currently a requirement that this cloud has patches applied which
    are not appropriate for a production cloud.

By default, this setup creates 5 nova servers, 3 consisting of 4GB of memory
and 40GB of disk space on each; one to be used for the deployment of the
undercloud and two for the overcloud. Additionally each overcloud server
requires a corresponding small server to handle BMC IPMI requests.

If you want to increase the scaling of one or more overcloud nodes, you will
need to ensure you cloud has the necessary capacity.

Preparing the Environment
-------------------------

Patching the OpenStack Host
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following patching needs to be performed on each compute node which might
host an undercloud or overcloud server. Assuming a Kilo cloud, run the
following and follow the instructions in README.md:

::

    git clone https://github.com/steveb/quintupleo.git
    cat quintupleo/patches/kilo/README.md

Preparing Images and Flavors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following commands require sourcing admin credentials for the host
OpenStack.

#. Baremetal servers need an empty image for initial boot:

::

    qemu-img create -f qcow2 empty.qcow2 40G
    glance image-create --name empty --disk-format qcow2 --container-format bare < empty.qcow2

#. The undercloud server is booted with a base RHEL 7.1 x86_64 or CentOS 7 x86_64
   image. The BMC server is known to work with CentOS 7, so this is required
   even with a RHEL undercloud.

::

    wget http://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud-1503.qcow2
    glance image-create --name CentOS-7-x86_64-GenericCloud-1503 \
        --disk-format qcow2 --container-format bare \
        < CentOS-7-x86_64-GenericCloud-1503.qcow2
    # optionally download a RHEL image if creating a RHEL undercloud
    glance image-create --name rhel-guest-image-7.1-20150224.0.x86_64 \
        --disk-format qcow2 --container-format bare \
        < rhel-guest-image-7.1-20150224.0.x86_64.qcow2

#. Baremetal servers need a special flavor to indicate that PXE boot should be
   attempted:

::

    nova flavor-create baremetal_flavor 333 4096 50 2
    nova flavor-key baremetal_flavor set libvirt:pxe-first=1
    nova flavor-show baremetal_flavor

#. BMC servers can run in a flavor such as m1.small, but this may consume too much
   resource on resource-constrained clouds (such as a single node development
   environment) so you may wish to create a dedicated flavor for these.

::

    nova flavor-create bmc_flavor 334 1024 20 1

Launch Up Baremetal, BMC and Undercloud Stack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# Create the stack which brings up the Baremetal, BMC and Undercloud servers.

::

    git clone https://github.com/steveb/quintupleo.git
    cd quintupleo
    cp quintupleo-env-example.yaml quintupleo-env.yaml
    # edit quintupleo-env.yaml to match your OpenStack environment and credentials
    heat stack-create -e quintupleo-env.yaml -f quintupleo.yaml quintupleo

.. note::
    Cloud images provide a non-root user with sudo access. RHEL 7.1 has user
    ``cloud-user`` and CentOS 7 has user ``centos``. This user should be used
    when running undercloud commands.

#. Wait until the stack is in a CREATE_COMPLETE state.::

    heat stack-show quintupleo

#. Get the undercloud address.::

    UNDERCLOUD_IP=`heat output-show --format raw quintupleo undercloud_host`
    echo $UNDERCLOUD_IP

#. Run the ``build-nodes-json`` script and upload the generated json file to the
   undercloud..::

    ./build-nodes-json
    scp nodes.json cloud-user@$UNDERCLOUD_IP:instackenv.json

#. SSH into the undercloud.::

    ssh cloud-user@$UNDERCLOUD_IP

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
