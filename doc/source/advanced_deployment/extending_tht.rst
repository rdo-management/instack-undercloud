Extending the TripleO Heat Templates
====================================

The TripleO Heat templates provide the framework on which a
cloud may be configured and deployed. While a great deal of customization
can be achieved using the template parameters, there are situations
in which new templates are needed to accomplish certain functionality.

For example, the default behavior of the templates is to deploy the
overcloud using a flat networking scheme. More
:doc:`complex network configurations <network_isolation>` can be
defined by extending the default templates with more additional templates.
Another example of where extending the templates is needed is to support
configuring vendor-specific hardware, such as a network switch or
storage driver.

Extension Model
---------------

In most cases, new functionality can be added without altering the TripleO
Heat templates themselves. The new templates are tied into the existing
framework through the use of environment files.

.. note::

    More information on writing
    `Heat templates <http://docs.openstack.org/developer/heat/template_guide/hot_guide.html>`_
    and the use of `environment files <http://docs.openstack.org/developer/heat/template_guide/environment.html>`_
    can be found in the Heat `upstream documentation <http://docs.openstack.org/developer/heat/template_guide/index.html>`_.

The entry point to deploying a cloud is the ``overcloud-without-mergepy.yaml``
template. This template defines the overall structure of the cloud and
references all of the other templates necessary to configure particular
aspects. For example, the ``controller-puppet.yaml`` template is responsible
for configuration specific to controller nodes.

Each individual piece of the TripleO Heat templates is a Heat *resource*.
For example, the following are all examples of individual resources found
in the templates:

 * The group of nodes deployed as the cloud controllers
 * The configuration passed to an individual node
 * The root password of the installed MySQL instance
 * The allocation of a virtual IP from Neutron

Each resource is given a specific *type* when it is defined. For example,
the MySQL password is defined as the ``OS::Heat::RandomString`` type.
leveraging Heat's innate ability to generate a string. Many other resources
utilize built-in types as well, such as a collection of nodes being defined
as a ``OS::Heat::ResourceGroup`` or a virtual IP defined as
an ``OS::Neutron::Port``.

The TripleO Heat templates use a number of custom resource types. For example,
the ``OS::TripleO::Network`` type encapsulates all of the different networks
created when deploying with isolated networks.

Each type corresponds to an indivdual Heat template, often referred to as a
*nested stack*. The type name is mapped to a template to fulfill that type
through the *resource registry*. Resource registry entries are added to
*environment* files. The default environment file is
``overcloud-resource-registry-puppet.yaml``.

Going back to the network definition example, the overcloud template creates
a resource to describe all of the desired networks::

 resources:
   ...
   Networks:
     type: OS::TripleO::Network
   ...

To determine the actual template that will fulfill the
``OS::TripleO::Network`` type, the ``resource_registry`` section of the
default environment file is checked::

  resource_registry:
    ...
    OS::TripleO::Network: network/networks.yaml
    ...

When Heat creates the network resource, it will create a nested stack using
the ``network/networks.yaml`` template (which itself has nested stacks
defining the specifics of each network to create).

Multiple environment files may be specified on a stack creation. If a
resource registry entry is found in multiple files, the last value will be
used. This is the primary means for extending the TripleO Heat templates,
by providing extra environment files that override one or more of the
resource type entries.

Hooks
^^^^^

While any resource type may be changed, the typical usage will be to leverage
one of the existing hooks provided by the TripleO Heat templates. These hooks
are resources in the templates that execute at a particular time during the
deployment. By default, they do nothing. When the hook resource type is
overridden, it provides a way of inserting custom Heat template code into
the deployment process without modifying the TripleO Heat templates themselves.

The list of available hooks can be found in
``overcloud-resource-registry-puppet.yaml``. Again, any resource type may be
overridden in an environment file, however care must be taken when doing so
as fundamental functionality may be lost.

Custom Configuration
^^^^^^^^^^^^^^^^^^^^

While it is not a formal interface definition, Heat is very specific about
how a template is called. Each parameter in the template must have a value
specified, either explicitly or through the default in the parameter
definition. Additionally, *only* parameters defined by the template may be
passed into it.

As such, custom templates that are used to replace existing resource types
must honor the same inputs (``parameters`` in the template) and outputs
as the existing resource type. The TripleO Heat templates will create the
resource with expectations on the resource type's inputs and outputs. If
a resource type is changed to point to a custom template, that template
must honor those inputs and outputs.

The easiest way to determine that interface is to look at the default
template that fulfills a given resource type. For example, the
``OS::TripleO::NodeExtraConfigPost`` resource is, by default, mapped to
``extraconfig/post_deploy/default.yaml``. That template is defined as
accepting a parameter named ``servers`` as its only input. Any template that
will be mapped to the ``OS::TripleO::NodeExtraConfigPost`` type must
define a parameter named ``servers`` in order for Heat to accept the
templates.

Generally speaking, these inputs and outputs will represent the least common
denominator in terms of how to configure that resource. There are times,
however, when custom values are necessary. Again, the goal is to not edit
the TripleO Heat templates themselves, so the approach is not to edit the
resource creation in the overcloud template and pass in the extra data.

Instead, the approach is as follows:

 * Define parameters in the template, making sure to specify a default value
   for all non-standard parameters (in other words, those parameters that are
   not passed by default during the resource creation).
 * Specify values for those parameters under the ``parameter_defaults``
   section of the environment file.

Keep in mind that parameters set in this way are global to the entire stack,
not just the custom template. As such, it is suggested to namespace the
parameter names to prevent conflicts with other custom templates.
