Ready-State (BIOS, RAID)
========================

Match deployment profiles
-------------------------
Before doing the ready-state configuration, we first must match the nodes to profiles.

  ::

      sudo yum install -y ahc-tools
      sudo -E ahc-match

.. note:: By default, ahc-match must be run as root. If we want to use the tool as a non-root user, we need to pass a config file with a user-writable lock file and user-writable edeploy config dir.


Ready-state configuration
-------------------------

Configure BIOS based on the deployment profile::

    instack-ironic-deployment --configure-bios

.. note:: The BIOS changes will be applied during the first boot.

Create root RAID volume based on the deployment profile::

    instack-ironic-deployment --configure-root-raid-volume

.. note:: The nodes will be restarted and RAID configuration will happen during
   the first boot.

Discover root block device::

    sudo -E ahc-match

Create non-root RAID volumes based on the deployment profile::

    instack-ironic-deployment --configure-nonroot-raid-volumes

.. note:: The nodes will be restarted and RAID configuration will happen during
   the first boot.
