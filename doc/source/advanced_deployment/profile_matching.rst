Advanced Profile Matching
=========================

Here are additional setup steps to take advantage of the advanced profile
matching and the AHC features.

Enable advanced profile matching
--------------------------------

* Install the ahc-tools package::

    sudo yum install -y ahc-tools

* Add the credentials for Ironic and Swift to the
  **/etc/ahc-tools/ahc-tools.conf** file.
  These will be the same credentials that ironic-discoverd uses,
  and can be copied from **/etc/ironic-discoverd/discoverd.conf**.
  Alternatively, you can use admin user name and password as found in
  **stackrc** file.

  Example::

    [ironic]
    os_auth_url = http://192.0.2.1:5000/v2.0
    os_username = <USER>
    os_password = <PASSWORD>
    os_tenant_name = <TENANT>

    [swift]
    os_auth_url = http://192.0.2.1:5000/v2.0
    os_username = <USER>
    os_password = <PASSWORD>
    os_tenant_name = <TENANT>

Accessing additional introspection data
---------------------------------------

Every introspection run (as described in
:doc:`../basic_deployment/basic_deployment`) collects a lot of additional
facts about the hardware and puts them as JSON in Swift. Swift container name
is ``ironic-inspector`` and can be modified in
**/etc/ironic-discoverd/discoverd.conf**. Swift object name is stored under
``hardware_swift_object`` key in Ironic node extra field.

Matching rules
--------------

These matching rules will determine what profile gets assigned to each node.

Open the **/etc/ahc-tools/edeploy/control.specs** file.
By default it will look close to this

  ::

      [
       ('disk', '$disk', 'size', 'gt(4)'),
       ('network', '$eth', 'ipv4', 'network(192.0.2.0/24)'),
       ('memory', 'total', 'size', 'ge(4294967296)'),
      ]

These rules match on the data collected during introspection.
Note that disk size is in GiB, while memory size is in KiB.

There is a set of helper functions to make matching more flexible.

* network() : the network interface shall be in the specified network
* gt(), ge(), lt(), le() : greater than (or equal), lower than (or equal)
* in() : the item to match shall be in a specified set
* regexp() : match a regular expression
* or(), and(), not(): boolean functions. or() and and() take 2 parameters
  and not() one parameter.

There are also placeholders, *$disk* and *$eth* in the above example.
These will store the value in that place for later use.

* For example if we had a "fact" from discovery::

    ('disk', 'sda', 'size', '40')

This would match the first rule in the above control.specs file,
and we would store ``"disk": "sda"``.

Create flavors to use advanced matching
---------------------------------------

In order to use the profiles assigned to the Ironic nodes, Nova needs to have
flavors that have the property "capabilities:profile" set to the intended profile.

For example, with just the compute and control profiles:

* Create the flavors

  ::

    openstack flavor create --id auto --ram 4096 --disk 40 --vcpus 1 control
    openstack flavor create --id auto --ram 4096 --disk 40 --vcpus 1 compute

.. note::

  The values for ram, disk, and vcpus should be set to a minimal lower bound,
  as Nova will still check that the Ironic nodes have at least this much
  even if we set lower properties in the **.specs** files.

* Assign the properties

  ::

    openstack flavor set --property "cpu_arch"="x86_64" --property "capabilities:boot_option"="local" --property "capabilities:profile"="compute" compute
    openstack flavor set --property "cpu_arch"="x86_64" --property "capabilities:boot_option"="local" --property "capabilities:profile"="control" control


Use the flavors to deploy
-------------------------

By default, all nodes are deployed to the **baremetal** flavor.
The RDO-Manager CLI has options to support more advanced role matching.

Continuing with the example with only a control and compute profile:

* Get the Tuskar plan id

  ::

    tuskar plan-list

* Deploy the overcloud

  ::

    openstack overcloud deploy --control-flavor control --compute-flavor compute --plan-uuid <UUID from above>


Use the flavors to scale
-------------------------

The process to scale an overcloud that uses our advanced profiles is the same
as the process used when we only have the **baremetal** flavor.

.. note::

  The original overcloud must have been deployed as above in order to scale
  using advanced profiles, as the flavor to role mapping happens then.

* Update the **/etc/ahc-tools/edeploy/state** file to match the number
  of nodes we want to match to each role.

* Run `sudo ahc-match` to match available nodes to the defined roles.

* Scale the overcloud (example below adds two more nodes to the compute role)

  ::

    openstack overcloud scale stack overcloud overcloud -r Compute-1 -n 2

