Ready-State (BIOS, RAID)
========================

Start with matching the nodes to profiles as described in
:doc:`profile_matching`.

Define the target BIOS and RAID configuration
---------------------------------------------

To define the target BIOS and RAID configuration for a deployment profile, you
need to create a ``.cmdb`` file in ``/etc/ahc-tools/edeploy``. An example for
``control.cmdb``::

    [
     {
      'bios_settings': {},
      'logical_disks': [
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
      ]
     }
    ]

Match deployment profiles
-------------------------

Then trigger the BIOS and RAID configuration based on the deployment profile::

    instack-ironic-deployment --configure-nodes
