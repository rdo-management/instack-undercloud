Ready-State (BIOS, RAID)
========================

Define the target BIOS and RAID configuration
---------------------------------------------
To define the target BIOS and RAID configuration for a deployment profile, you
need to create a ``.cmdb`` file in ``/etc/edeploy``. An example for
``control.cmdb``::

    [{'bios_settings': {'ProcVirtualization': 'Disabled'}
      'logical_disks': (
            {'controller': 'RAID.Integrated.1-1',
             'size_gb': 50,
             'raid_level': '1',
             'number_of_physical_disks': 2,
             'disk_type': 'hdd',
             'interface_type': 'sas',
             'volume_name': 'root_volume',
             'is_root_volume': True},
            {'controller': 'RAID.Integrated.1-1',
             'size_gb': 100,
             'physical_disks': [
                'Disk.Bay.0:Enclosure.Internal.0-1:RAID.Integrated.1-1',
                'Disk.Bay.1:Enclosure.Internal.0-1:RAID.Integrated.1-1',
                'Disk.Bay.2:Enclosure.Internal.0-1:RAID.Integrated.1-1']
             'raid_level': '5',
             'volume_name': 'data_volume1'}
         )
    }]

Match deployment profiles
-------------------------
Before doing the ready-state configuration, we first must match the nodes to profiles.

  ::

      sudo yum install -y ahc-tools
      sudo -E ahc-match

Ready-state configuration
-------------------------

Trigger the BIOS and RAID configuration based on the deployment profile::

    instack-ironic-deployment --configure-nodes
