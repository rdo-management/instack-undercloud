Configuring Network Isolation
=============================

Introduction
------------

RDO-Manager provides configuration of isolated overcloud networks. Using
this approach it is possible to host traffic for specific types of network
traffic (tenants, storage, API/RPC, etc.) in isolated networks. This allows
for assigning network traffic to specific network interfaces or bonds. Using
bonds provides fault tolerance, and may provide load sharing, depending on the
bonding protocols used. When isolated networks are configured, the OpenStack
services will be configured to use the isolated networks. If no isolated
networks are configured, all services run on the provisioning network.


Workflow
--------

The procedure for enabling network isolation is this:
1. Create network environment file (/home/stack/network-environment.yaml)
2. Edit IP subnets and VLANs to match local environment
3. Make a copy of the sample network interface configurations
7. Edit the network interface configurations to match local environment
8. Deploy overcloud with -e parameters to include network isolation

The following steps will walk through the elements that need to be added to
the network-environment.yaml to enable network isolation. The final step
will deploy the overcloud with network isolation and a custom environment.

Create Network Environment File
-------------------------------
The environment file will describe the network environment and will point to
the network interface configuration files to use for the overcloud nodes.
The subnets that will be used for the isolated networks need to be defined,
along with the IP address ranges that should be used for IP assignment. These
values should be customized for the local environment.

.. note::
  The resource_registry section of the network-environment.yaml contains
  pointers to the network interface configurations for the deployed roles.
  These files must exist at the path referenced here, and the following
  steps will create these files.

Example::

  resource_registry:
    OS::TripleO::BlockStorage::Net::SoftwareConfig: /home/stack/nic-configs/cinder-storage.yaml
    OS::TripleO::Compute::Net::SoftwareConfig: /home/stack/nic-configs/compute.yaml
    OS::TripleO::Controller::Net::SoftwareConfig: /home/stack/nic-configs/controller.yaml
    OS::TripleO::ObjectStorage::Net::SoftwareConfig: /home/stack/nic-configs/swift-storage.yaml
    OS::TripleO::CephStorage::Net::SoftwareConfig: /home/stack/nic-configs/ceph-storage.yaml

  parameter_defaults:
    # Customize the IP subnets to match the local environment
    InternalApiNetCidr: 172.17.0.0/24
    StorageNetCidr: 172.18.0.0/24
    StorageMgmtNetCidr: 172.19.0.0/24
    TenantNetCidr: 172.16.0.0/24
    ExternalNetCidr: 10.1.2.0/24
    InternalApiAllocationPools: [{'start': '172.17.0.10', 'end': '172.17.0.200'}]
    StorageAllocationPools: [{'start': '172.18.0.10', 'end': '172.18.0.200'}]
    StorageMgmtAllocationPools: [{'start': '172.19.0.10', 'end': '172.19.0.200'}]
    TenantAllocationPools: [{'start': '172.16.0.10', 'end': '172.16.0.200'}]
    # Use an External allocation pool which will leave room for floating IPs
    ExternalAllocationPools: [{'start': '10.1.2.10', 'end': '10.1.2.50'}]
    InternalApiNetworkVlanID: 201
    StorageNetworkVlanID: 202
    StorageMgmtNetworkVlanID: 203
    TenantNetworkVlanID: 204
    ExternalNetworkVlanID: 100
    # Customize bonding options if required
    BondInterfaceOvsOptions:
        "bond_mode=balance-tcp lacp=active other-config:lacp-fallback-ab=true"

Creating Custom Interface Templates
-----------------------------------

In order to configure the network interfaces on each node, the network
interface templates may need to be customized.

Start by copying the configurations from one of the example directories. The
first example copies the templates which include network bonding. The second
example copies the templates which use a single network interface with
multiple VLANs (this configuration is mostly intended for testing).

To copy the bonded example interface configurations, run::

    $ cp -r /usr/share/openstack-tripleo-heat-templates/network/config/bond-with-vlans ~/nic-configs

To copy the single NIC with VLANs example interface configurations, run::

    $ cp -r /usr/share/openstack-tripleo-heat-templates/network/config/single-nic-vlans ~/nic-configs

Customizing the Interface Templates
-----------------------------------
Depending on the physical
The following example configures a bond on interfaces 3 and 4 of a system
with 4 interfaces. This example is based on the controller template from the
bond-with-vlans sample templates, but the bond has been placed on nic3 and nic4
instead of nic2 and nic3. The other roles will have a similar configuration,
but will have only a subset of the networks attached.

.. note::
  The nic1, nic2... abstraction considers only network interfaces which are
  connected to an Ethernet switch. If interfaces 1 and 4 are the only
  interfaces which are plugged in, they will be referred to as nic1 and nic2.

Example::

  heat_template_version: 2015-04-30

  description: >
    Software Config to drive os-net-config with 2 bonded nics on a bridge
    with a VLANs attached for the controller role.

  parameters:
    ExternalIpSubnet:
      default: ''
      description: IP address/subnet on the external network
      type: string
    InternalApiIpSubnet:
      default: ''
      description: IP address/subnet on the internal API network
      type: string
    StorageIpSubnet:
      default: ''
      description: IP address/subnet on the storage network
      type: string
    StorageMgmtIpSubnet:
      default: ''
      description: IP address/subnet on the storage mgmt network
      type: string
    TenantIpSubnet:
      default: ''
      description: IP address/subnet on the tenant network
      type: string
    BondInterfaceOvsOptions:
      default: ''
      description: The ovs_options string for the bond interface. Set things like
                   lacp=active and/or bond_mode=balance-slb using this option.
      type: string
    ExternalNetworkVlanID:
      default: 10
      description: Vlan ID for the external network traffic.
      type: number
    InternalApiNetworkVlanID:
      default: 20
      description: Vlan ID for the internal_api network traffic.
      type: number
    StorageNetworkVlanID:
      default: 30
      description: Vlan ID for the storage network traffic.
      type: number
    StorageMgmtNetworkVlanID:
      default: 40
      description: Vlan ID for the storage mgmt network traffic.
      type: number
    TenantNetworkVlanID:
      default: 50
      description: Vlan ID for the tenant network traffic.
      type: number

  resources:
    OsNetConfigImpl:
      type: OS::Heat::StructuredConfig
      properties:
        group: os-apply-config
        config:
          os_net_config:
            network_config:
              -
                type: ovs_bridge
                name: {get_input: bridge_name}
                members:
                  -
                    type: ovs_bond
                    name: bond1
                    ovs_options: {get_param: BondInterfaceOvsOptions}
                    members:
                      -
                        type: interface
                        name: nic3
                        primary: true
                      -
                        type: interface
                        name: nic4
                  -
                    type: vlan
                    device: bond1
                    vlan_id: {get_param: ExternalNetworkVlanID}
                    addresses:
                    -
                      ip_netmask: {get_param: ExternalIpSubnet}
                  -
                    type: vlan
                    device: bond1
                    vlan_id: {get_param: InternalApiNetworkVlanID}
                    addresses:
                    -
                      ip_netmask: {get_param: InternalApiIpSubnet}
                  -
                    type: vlan
                    device: bond1
                    vlan_id: {get_param: StorageNetworkVlanID}
                    addresses:
                    -
                      ip_netmask: {get_param: StorageIpSubnet}
                  -
                    type: vlan
                    device: bond1
                    vlan_id: {get_param: StorageMgmtNetworkVlanID}
                    addresses:
                    -
                      ip_netmask: {get_param: StorageMgmtIpSubnet}
                  -
                    type: vlan
                    device: bond1
                    vlan_id: {get_param: TenantNetworkVlanID}
                    addresses:
                    -
                      ip_netmask: {get_param: TenantIpSubnet}

  outputs:
    OS::stack_id:
      description: The OsNetConfigImpl resource.
      value: {get_resource: OsNetConfigImpl}

Assinging OpenStack Services to Isolated Networks
-------------------------------------------------

.. note::
  The services will be assigned to the networks according to the ServiceNetMap
  in overcloud-without-mergepy.yaml. Unless these defaults need to be
  overridden, the ServiceNetMap does not need to be defined in the
  environment file.

Each OpenStack service is assigned to a network in the resource registry. The
service will be bound to the host IP within the named network on each host.
A service can be assigned to an alternate network by overriding the service to
network map in an environment file. The defaults should generally work, but
can be overridden.

Example::

  parameters:

    ServiceNetMap:
      NeutronTenantNetwork: tenant
      CeilometerApiNetwork: internal_api
      MongoDbNetwork: internal_api
      CinderApiNetwork: internal_api
      CinderIscsiNetwork: storage
      GlanceApiNetwork: storage
      GlanceRegistryNetwork: internal_api
      KeystoneAdminApiNetwork: internal_api
      KeystonePublicApiNetwork: internal_api
      NeutronApiNetwork: internal_api
      HeatApiNetwork: internal_api
      NovaApiNetwork: internal_api
      NovaMetadataNetwork: internal_api
      NovaVncProxyNetwork: internal_api
      SwiftMgmtNetwork: storage_mgmt
      SwiftProxyNetwork: storage
      HorizonNetwork: internal_api
      MemcachedNetwork: internal_api
      RabbitMqNetwork: internal_api
      RedisNetwork: internal_api
      MysqlNetwork: internal_api
      CephClusterNetwork: storage_mgmt
      CephPublicNetwork: storage

.. note::
  Although the OpenStack services are divided among these 5 named networks,
  the number of actual physical networks may differ. For instance, if a given
  deployment had no separate storage network, the tenant network could be
  used for both VM connectivity and storage. ServiceNetMap determines which
  networks are used for which services.

Deploying the Overcloud With Network Isolation
----------------------------------------------
To get the deployment plan UUID (plan name is "overcloud"), run::

    openstack management plan list

To deploy with network isolation and include the network environment file, use
the -e parameters with the "openstack overcloud deploy" command::

    openstack overcloud deploy -e /home/stack/network-environment.yaml \
    -e /usr/share/openstack-tripleo-heat-templates/environments/network-isolation.yaml \
    --plan-uuid "[uuid]" <other_parameters>
