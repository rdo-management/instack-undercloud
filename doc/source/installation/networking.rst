Configuring Networking
======================

Introduction
------------

This document outlines the configuration of isolated overcloud networks. Using
this approach it is possible to host traffic for specific types of network
traffic (tenants, storage, API/RPC, etc.) in isolated networks. This allows
for assigning network traffic to specific network interfaces or bonds. Using
bonds provides fault tolerance, and may provide load sharing, depending on the
bonding protocols used. When isolated networks are configured, the OpenStack
services will be configured to use the isolated networks. If no isolated
networks are configured, all services run on the Provisioning network.

Internally, IP address management is done with Neutron. In this document we
describe how to use an environment file to create networks, and assign
static IP addresses to multiple network interfaces on each machine deployed
to host the Overcloud.

Workflow
--------

The procedure for enabling network isolation is this:
1. Create network environment file (/home/stack/network_env.yaml)
2. Add parameter_defaults section below to network_env.yaml
3. Add resource_registry section below to network_env.yaml
4. Edit IP subnets in network_env.yaml to match local environment
5. export OVERCLOUD_EXTRA = "-e /home/stack/network_env.yaml $OVERCLOUD_EXTRA"
6. Make a copy of the TripleO Heat templates in network/config/bond-with-vlans
7. Edit the NIC config templates
8. Deploy overcloud

The following steps will walk through the elements that need to be added to
the network_env.yaml to enable network isolation.

Customizing Network CIDR
------------------------
The subnets that will be used for the isolated networks need to be defined,
along with the IP address ranges that should be used for IP assignment. These
values should be customized for the local environment.

Example::

  parameter_defaults:

    ExternalNetCidr: 10.0.0.0/24
    InternalApiNetCidr: 172.17.0.0/24
    StorageNetCidr: 172.18.0.0/24
    StorageNetCidr: 172.19.0.0/24
    TenantNetCidr: 172.16.0.0/24
    InternalApiAllocationPools: [{'start': '172.17.0.10', 'end': '172.17.0.250'}]
    StorageAllocationPools: [{'start': '172.18.0.10', 'end': '172.18.0.250'}]
    StorageMgmtAllocationPools: [{'start': '172.19.0.10', 'end': '172.19.0.250'}]
    TenantAllocationPools: [{'start': '172.16.0.10', 'end': '172.16.0.250'}]
    ExternalAllocationPools: [{'start': '10.0.0.10', 'end': '10.0.0.250'}]
Network configuration resource registry in network_env.yaml
-----------------------------------------------------------

To enable isolated networks to be created, each network definition file
needs to be referenced in the environment file. The ports that get created
correspond to the IP addresses that get created on the isolated networks.
The network interface configurations also will need to be customized,
so we will create references to custom templates.

Example::

  resource_registry:

    # TripleO network architecture
    OS::TripleO::Network: network/networks.yaml
    OS::TripleO::Network::External: network/external.yaml
    OS::TripleO::Network::InternalApi: network/internal_api.yaml
    OS::TripleO::Network::Storage: network/storage.yaml
    OS::TripleO::Network::StorageMgmt: network/storage_mgmt.yaml
    OS::TripleO::Network::Tenant: network/tenant.yaml
    # Port assignments for the controller role
    OS::TripleO::Controller::Ports::ExternalPort: ../network/ports/external.yaml
    OS::TripleO::Controller::Ports::InternalApiPort: ../network/ports/internal_api.yaml
    OS::TripleO::Controller::Ports::StoragePort: ../network/ports/storage.yaml
    OS::TripleO::Controller::Ports::StorageMgmtPort: ../network/ports/storage_mgmt.yaml
    OS::TripleO::Controller::Ports::TenantPort: ../network/ports/tenant.yaml

    # Port assignments for the compute role
    OS::TripleO::Compute::Ports::InternalApiPort: ../network/ports/internal_api.yaml
    OS::TripleO::Compute::Ports::StoragePort: ../network/ports/storage.yaml
    OS::TripleO::Compute::Ports::TenantPort: ../network/ports/tenant.yaml

    # Port assignments for the ceph storage role
    OS::TripleO::CephStorage::Ports::StoragePort: ../network/ports/storage.yaml
    OS::TripleO::CephStorage::Ports::StorageMgmtPort: ../network/ports/storage_mgmt.yaml

    # Port assignments for the swift storage role
    OS::TripleO::SwiftStorage::Ports::InternalApiPort: ../network/ports/internal_api.yaml
    OS::TripleO::SwiftStorage::Ports::StoragePort: ../network/ports/storage.yaml
    OS::TripleO::SwiftStorage::Ports::StorageMgmtPort: ../network/ports/storage_mgmt.yaml

    # Port assignments for the block storage role
    OS::TripleO::BlockStorage::Ports::InternalApiPort: ../network/ports/internal_api.yaml
    OS::TripleO::BlockStorage::Ports::StoragePort: ../network/ports/storage.yaml
    OS::TripleO::BlockStorage::Ports::StorageMgmtPort: ../network/ports/storage_mgmt.yaml

    # Port assignments for service virtual IPs for the controller role
    OS::TripleO::Controller::Ports::RedisVipPort: network/ports/vip.yaml

    # Network interface configurations should be in network/config/custom
    OS::TripleO::BlockStorage::Net::SoftwareConfig: ../network/config/custom/cinder-storage.yaml
    OS::TripleO::Compute::Net::SoftwareConfig: ../network/config/custom/compute.yaml
    OS::TripleO::Controller::Net::SoftwareConfig: ../network/config/custom/controller.yaml
    OS::TripleO::ObjectStorage::Net::SoftwareConfig: ../network/config/custom/swift-storage.yaml
    OS::TripleO::CephStorage::Net::SoftwareConfig: ../network/config/custom/ceph-storage.yaml
Creating Custom Interface Templates
-----------------------------------

In order to configure the network interfaces on each node, the network
interface templates will need to be customized.

Start by copying the configurations from one of the existing directories. The
first example copies the templates which include network bonding. The second
example copies the templates which use a single network interface with
multiple VLANs (this configuration is intended for testing).

Example::

  $ cp /usr/share/openstack-tripleo-heat-templates/network/config/
  $ cp -r bond-with-vlans custom
or

Example::

  $ cp /usr/share/openstack-tripleo-heat-templates/network/config/
  $ cp -r single-nic-with-vlans custom
Customizing the Interface Templates
-----------------------------------
The following example configures a bond on interfaces 3 and 4 of a system
with 4 interfaces. This example is based on the controller template from the
bond-with-vlans sample templates. The other roles will have a similar
configuration, but will have fewer networks attached.

Example::

  heat_template_version: 2016-04-30

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
can be overridden:

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
