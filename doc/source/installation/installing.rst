Installing RDO-Manager (undercloud)
===================================

#. Log in to your machine (baremetal or VM) where you want to install RDO-Manager
   as a non-root user (such as the stack user)::

    ssh <non-root-user>@<rdo-manager-machine>

   .. note::
      If you don't have any user created yet, log as root and create one with
      following commands::

          sudo useradd stack
          sudo passwd stack  # specify a password

          echo "stack ALL=(root) NOPASSWD:ALL" | sudo tee -a /etc/sudoers.d/stack
          sudo chmod 0440 /etc/sudoers.d/stack

          su - stack


   .. note::
      Ensure that there is an entry for the system's full hostname in /etc/
      hosts. For example, if the system is named *myhost.mydomain*, /etc/hosts
      should have an entry like::

          127.0.0.1   myhost.mydomain


#. Download and execute the instack-undercloud setup script which will enable
   needed repositories for you:

   .. only:: internal

      .. admonition:: RHEL
         :class: rhel-tag

          Enable rhos-release::

              export RUN_RHOS_RELEASE=1

   ::

       curl https://raw.githubusercontent.com/rdo-management/instack-undercloud/master/scripts/instack-setup-host | bash -x


#. Install unified CLI (installs also instack-undercloud as a dependency)::

    sudo yum install -y python-rdomanager-oscplugin


#. Run script to install the undercloud:


  Copy in the sample answers file and edit it to reflect your environment (keep
  defaults if you used instack-virt-setup)::

      cp /usr/share/instack-undercloud/instack.answers.sample ~/instack.answers


  Install the RDO-Manager::

      openstack undercloud install


Once the install script has run to completion, you should take note of the
files ``/root/stackrc`` and ``/root/tripleo-undercloud-passwords``. Both these
files will be needed to interact with the installed undercloud. Copy them to
the home directory for easier use later::

    sudo cp /root/tripleo-undercloud-passwords .
    sudo cp /root/stackrc .
