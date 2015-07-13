Additional node configuration
=============================

It is possible to enable additional configuration during one of the
following deployment phases:

* firstboot - run once config (performed by cloud-init)

Firstboot extra configuration
-----------------------------

Firstboot configuration is performed on all nodes on initial deployment.
Any configuration possible via cloud-init may be performed at this point,
either by providing cloud-config yaml or specifying arbitrary additional
scripts.

The heat templates used for deployment provide the `OS::TripleO::NodeUserData`
resource as the interface to enable this configuration, a basic example of its
usage is provided below:

First create a template containing one or more configuration resources::

    mkdir firstboot
    cat > firstboot/one_two.yaml << EOF
    heat_template_version: 2014-10-16

    resources:
      userdata:
        type: OS::Heat::MultipartMime
        properties:
          parts:
          - config: {get_resource: one_config}
          - config: {get_resource: two_config}

      one_config:
        type: OS::Heat::SoftwareConfig
        properties:
          config: |
            #!/bin/bash
            echo "one" > /tmp/one

      two_config:
        type: OS::Heat::SoftwareConfig
        properties:
          config: |
            #!/bin/bash
            echo "two" > /tmp/two

    outputs:
      OS::stack_id:
        value: {get_resource: userdata}
    EOF

.. note::

    The stack must expose an `OS::stack_id` output which references an
    OS::Heat::MultipartMime resource.

This template is then mapped to the `OS::TripleO::NodeUserData` resource type
via a heat environment file::

    cat > userdata_env.yaml << EOF
    resource_registry:
        OS::TripleO::NodeUserData: firstboot/one_two.yaml
    EOF

You may then deploy your overcloud referencing the additional environment file::

    openstack overcloud deploy --templates -e userdata_env.yaml

.. note::

    OS::TripleO::NodeUserData is only applied on initial node deployment,
    not on any subsequent stack update, because cloud-init only processes the
    nova user-data once, on first boot.

For a more complete example, which creates an additional user then configures
SSH keys by accessing the nova metadata server, see
/usr/share/openstack-tripleo-heat-templates/firstboot/userdata_example.yaml.
