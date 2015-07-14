Introspection
=============

This expands on the information in the
:doc:`../basic_deployment/basic_deployment` section.

Data Flow
---------

This section describes what actually happens during the `Introspect Nodes`_
step.

* For each node **ironic-discoverd**:

  * validates node power credentials, current power and provisioning states,
  * allows firewall access to PXE boot service for the nodes,
  * issues reboot command for the nodes, so that they boot the ramdisk.

* The ramdisk collects the required information and posts it back to
  **ironic-discoverd**.

* On receiving data from the ramdisk, **ironic-discoverd**:

  * validates received data,
  * finds the node in Ironic database using it's BMC address (MAC address in
    case of SSH driver),
  * fills missing node properties with received data and creates missing ports.

Plugins
-------

**ironic-discoverd** heavily relies on plugins for data processing. Even the
standard functionality is largely based on plugins. Set ``processing_hooks``
option in the configuration file to change the set of plugins to be run on
introspection data. Note that order does matter in this option.

These are plugins that are enabled by default and should not be disabled,
unless you understand what you're doing:

``ramdisk_error``
    reports error, if error field is set by the ramdisk, also optionally
    stores logs from logs field.
``scheduler``
    validates and updates basic hardware scheduling properties: CPU number and
    architecture, memory and disk size.
``validate_interfaces``
    validates network interfaces information.
``root_device_hint``
    gathers block devices from ramdisk and exposes root device in multiple
    runs.
``extra_hardware``
    stores the value of the 'data' key returned by the ramdisk as a JSON
    encoded string in a Swift object.

Refer to the upstream `CONTRIBUTING.rst`_ for information on how to write your
own plugin.

Further Reading
---------------

More comprehensive documentation can be found `upstream`_.

.. note::

    The ironic-discoverd project has been renamed upstream to ironic-inspector.

.. _Introspect Nodes: ../basic_deployment/basic_deployment.html#introspect-nodes
.. _CONTRIBUTING.rst: https://github.com/openstack/ironic-inspector/blob/master/CONTRIBUTING.rst
.. _upstream: https://github.com/openstack/ironic-inspector/blob/master/README.rst