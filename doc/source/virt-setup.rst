Virtual Environment Setup
=========================

instack-undercloud can be deployed in a virtual environment using virtual
machines instead of actual baremetal. One baremetal machine is still needed to
act as the host for the virtual machines.

instack-undercloud contains the necessary tooling to create and configure the
environment.

Minimum System Requirements
---------------------------

This setup creates 5 virtual machines consisting of 4GB of memory and 40GB of
disk space on each. The virtual machine disk files are thinly provisioned and
will not take up the full 40GB initially.

The minimum system requirements for the virtual host machine are:

* A baremetal machine with virtualization hardware extenstions enabled.
  Nested KVM is **not** supported.
* At least (1) quad core CPU
* 12GB free memory
* 120GB disk space [#]_

If you want to increase the scaling of one or more overcloud nodes, you will
need to ensure you have enough memory and disk space.

Preparing the Host Machine
--------------------------

#. Install RHEL 7.1 Server x86_64.
#. Make sure sshd service is installed and running.
#. The user performing all of the installation steps on the virt host needs to
   have sudo enabled. You can use an existing user or use the following commands
   to create a new user called stack with password-less sudo enabled. Do not run
   the rest of the steps in this guide as root.

    * Example commands to create a user::

        sudo useradd stack
        sudo passwd stack  # specify a password
        echo "stack ALL=(root) NOPASSWD:ALL" | sudo tee -a /etc/sudoers.d/stack
        sudo chmod 0440 /etc/sudoers.d/stack

#. Make sure you are logged in as the non-root user you intend to use.
#. Download and execute the instack-undercloud setup script::

    curl https://raw.githubusercontent.com/rdo-management/instack-undercloud/master/scripts/instack-setup-host-rhel7 | bash -x

#. Install instack-undercloud::

    sudo yum install -y instack-undercloud

#. Download the RHEL 7.1 cloud image or copy it over from a different
   location, and define the needed environment variables for RHEL 7.1::

    curl -O http://download.devel.redhat.com/brewroot/packages/rhel-guest-image/7.1/20150203.1/images/rhel-guest-image-7.1-20150203.1.x86_64.qcow2
    export DIB_LOCAL_IMAGE=rhel-guest-image-7.1-20150203.1.x86_64.qcow2
    export DIB_YUM_REPO_CONF=/etc/yum.repos.d/rhos-release-6-rhel-7.1.repo

#. Run the script to setup your virtual environment::

    instack-virt-setup

When the script has completed successfully it will output the IP address of the
instack vm that has now been installed with a base OS.

Running ``sudo virsh list --all`` [#]_ will show you now have one virtual machine called
*instack* and 4 called *baremetal[0-3]*.

You can ssh to the instack vm as the root user::

        ssh root@<instack-vm-ip>

The vm contains a ``stack`` user to be used for installing the undercloud. You
can ``su - stack`` to switch to the stack user account.

Continue with `Installing the Undercloud`_

.. _`Installing the Undercloud`: :ref:`install_undercloud`

.. rubric:: Footnotes

.. [#]  Note that some default partitioning scheme will most likely not provide
    enough space to the partition containing the default path for libvirt image
    storage (/var/lib/libvirt/images). The easiest fix is to customize the
    partition layout at the time of install to provide at least 200 GB of space for
    that path.

.. [#]  The libvirt virtual machines have been defined under the system
    instance (qemu:///system). The user account executing these instructions
    gets added to the libvirtd group which grants passwordless access to
    the system instance. It does however require logging into a new shell (or
    desktop environment session if wanting to use virt-manager) before this
    change will be fully applied. To avoid having to re-login, you can use
    ``sudo virsh``.
