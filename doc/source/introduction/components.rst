.. _projects_list:

Components
===========

.. contents::
   :depth: 2

This section contains a list of components that RDO-Manager uses. The components
are organized in categories, and include a basic description, useful links, and
contribution information.

[Category Name]
---------------

[Component Name]
^^^^^^^^^^^^^^^^
This is short description what the project is about and how RDO-Manager uses
this project. Three sentences max.

**How to contribute**

* Instructions to prepare development environment. Should be mostly pointing to
  upstream docs. If upstream docs doesn't exist, please, create one. Add tips
  how to test the feature in RDO-Manager + other useful information.


**Useful links**

* Upstream Project:  `link <#>`_
* Bugs: `link <#>`_
* Blueprints:  `link <#>`_

For an example component with all the necessary information, see `ironic`_.


Shared Libraries
----------------
diskimage-builder
^^^^^^^^^^^^^^^^^
TBD


dib-utils
^^^^^^^^^
TBD


os-\*-config
^^^^^^^^^^^^
TBD

tripleo-image-elements
^^^^^^^^^^^^^^^^^^^^^^
TBD


Installer
---------

instack
^^^^^^^
TBD


instack-undercloud
^^^^^^^^^^^^^^^^^^
TBD


tripleo-incubator
^^^^^^^^^^^^^^^^^
TBD


Node Management
---------------
ironic
^^^^^^

Ironic project is responsible for provisioning and managing bare metal
instances.

For testing purposes Ironic can also be used for provisioning and managing
virtual machines which act as bare metal nodes via special driver ``pxe_ssh``.

**How to contribute**

Ironic uses `tox <https://tox.readthedocs.org/en/latest/>`_ to manage the
development environment, see `OpenStack's documentation
<http://docs.openstack.org/developer/ironic/dev/contributing.html>`_,
`developer guidelines
<https://wiki.openstack.org/wiki/Ironic/Developer_guidelines>`_
and `OpenStack developer's guide
<http://docs.openstack.org/developer/openstack-projects.html>`_ for details.

**Useful links**

* Upstream Project: http://docs.openstack.org/developer/ironic/index.html
* Bugs: https://bugs.launchpad.net/ironic
* Blueprints: https://blueprints.launchpad.net/ironic

  * `Specs process <https://wiki.openstack.org/wiki/Ironic/Specs_Process>`_
    should be followed for suggesting new features.
  * Approved Specs: http://specs.openstack.org/openstack/ironic-specs/


ironic-discoverd
^^^^^^^^^^^^^^^^

ironic-discoverd project is responsible for discovery of hardware properties
for newly enrolled nodes (see also ironic_). Ironic uses drivers to hide
hardware details behind a common API.

**How to contribute**

ironic-discoverd uses `tox <https://tox.readthedocs.org/en/latest/>`_ to manage
the development environment, see `upstream documentation
<https://github.com/stackforge/ironic-discoverd/blob/master/CONTRIBUTING.rst>`_
for details.

**Useful links**

* Upstream Project: https://github.com/stackforge/ironic-discoverd
* PyPI: https://pypi.python.org/pypi/ironic-discoverd
* Bugs: https://bugs.launchpad.net/ironic-discoverd
* Blueprints: https://blueprints.launchpad.net/ironic-discoverd


Networking
----------
neutron
^^^^^^^
TBD

?
^
TBD


Deployment Planning
-------------------
tuskar
^^^^^^
TBD

python-tuskarclient
^^^^^^^^^^^^^^^^^^^
TBD



Deployment & Orchestration
--------------------------
heat
^^^^
TBD

heat-templates
^^^^^^^^^^^^^^
TBD

tripleo-heat-templates
^^^^^^^^^^^^^^^^^^^^^^
TBD

nova
^^^^
TBD

puppet-\*
^^^^^^^^^
TBD

tripleo-puppet-elements
^^^^^^^^^^^^^^^^^^^^^^^
TBD


User Interfaces
---------------
tuskar-ui
^^^^^^^^^
TBD

tuskar-ui-extras
^^^^^^^^^^^^^^^^
TBD

python-rdomanager-oscplugin
^^^^^^^^^^^^^^^^^^^^^^^^^^^
TBD
