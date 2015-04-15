Frequently Asked Questions
==========================

Where are the logs?
~~~~~~~~~~~~~~~~~~~

Some logs are stored in *journald*, but most as text files in ``/var/log``.
Stored in *journald* are logs for Ironic and ironic-discoverd. Note that
Ironic has 2 units: ``openstack-ironic-api`` and
``openstack-ironic-conductor``. Similarly, ironic-discoverd has
``openstack-ironic-discoverd`` and ``openstack-ironic-discoverd-dnsmasq``.
So for example to get all ironic-discoverd logs use::

    $ sudo journalctl -u openstack-ironic-discoverd -u openstack-ironic-discoverd-dnsmasq

Discovery hangs and times out
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ironic-discoverd times out discovery process after some time (defaulting to 1
hour) if it never gets response from the discovery ramdisk.  This can be
a sign of a bug in the discovery ramdisk, but usually it happens due to
environment misconfiguration, particularly BIOS boot settings. Please refer to
`ironic-discoverd troubleshooting documentation`_ for information on how to
detect and fix such problems.

How to stop discovery?
~~~~~~~~~~~~~~~~~~~~~~

Currently ironic-discoverd does not provide means for stopping discovery. The
recommended path is to wait until it times out. Changing ``timeout`` setting
in ``/etc/ironic-discoverd/discoverd.conf`` may be used to reduce this timeout
from 1 hour (which usually too much, especially on virtual environment).

If you do need to stop discovery **for all nodes** right now, do the
following for each node::

    $ ironic node-set-power-state UUID off

then remove ironic-discoverd cache and restart it::

    $ rm /var/lib/ironic-discoverd/discoverd.sqlite
    $ sudo systemctl restart openstack-ironic-discoverd


.. _ironic-discoverd troubleshooting documentation: https://github.com/stackforge/ironic-discoverd#troubleshooting
