Installing the Undercloud
==========================

#. Log in to your machine (baremetal or VM) where you want to install the
   undercloud as a non-root user (such as the stack user)::

       ssh <non-root-user>@<rdo-manager-machine>

   .. note::
      If you don't have a non-root user created yet, log in as root and create
      one with following commands::

          sudo useradd stack
          sudo passwd stack  # specify a password

          echo "stack ALL=(root) NOPASSWD:ALL" | sudo tee -a /etc/sudoers.d/stack
          sudo chmod 0440 /etc/sudoers.d/stack

          su - stack

   .. admonition:: Baremetal
      :class: baremetal

      Ensure that there is a FQDN hostname set and that the $HOSTNAME environment
      variable matches that value.

      Use ``hostnamectl`` to set a hostname if needed::

          sudo hostnamectl set-hostname myhost.mydomain
          sudo hostnamectl set-hostname --transient myhost.mydomain
          export HOSTNAME=myhost.mydomain

      An entry for the system's FQDN hostname is also needed in /etc/hosts. For
      example, if the system is named *myhost.mydomain*, /etc/hosts should have
      an entry like::

         127.0.0.1   myhost.mydomain


#. Enable needed repositories:

   .. only:: internal

      .. admonition:: RHEL
         :class: rhel

          Enable rhos-release::

              sudo yum install -y http://rhos-release.virt.bos.redhat.com/repos/rhos-release/rhos-release-latest.noarch.rpm
              sudo rhos-release 6

              # We need openwsman-python from the optional repo
              sudo yum install -y yum-utils
              sudo yum-config-manager --enable rhelosp-rhel-7-server-opt

   ::

       # Enable repo priorities
       sudo yum install -y yum-plugin-priorities

       # Enable RDO Kilo
       sudo yum install -y https://rdoproject.org/repos/openstack-kilo/rdo-release-kilo.rpm

       # Enable RDO Manager Trunk
       sudo curl -o /etc/yum.repos.d/rdo-management-trunk.repo http://trunk-mgt.rdoproject.org/centos-kilo/current-passed-ci/delorean-rdo-management.repo


#. Install the unified CLI (also installs instack-undercloud as a dependency)::

    sudo yum install -y python-rdomanager-oscplugin


#. Run the script to install the undercloud:

  .. admonition:: Baremetal
     :class: baremetal

     Copy in the sample answers file and edit it to reflect your environment::

        cp /usr/share/instack-undercloud/instack.answers.sample ~/instack.answers


  Install the undercloud::

      openstack undercloud install


Once the install script has run to completion, you should take note of the
files ``/root/stackrc`` and ``/root/tripleo-undercloud-passwords``. Both of
these files will be needed to interact with the installed undercloud. Copy them
to the home directory for easier use later::

    sudo cp /root/tripleo-undercloud-passwords .
    sudo chown $USER: tripleo-undercloud-passwords
    sudo cp /root/stackrc .
    sudo chown $USER: stackrc
