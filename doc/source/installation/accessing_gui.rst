Accessing the GUI
=================

Part of the Undercloud installation is also Tuskar-UI which you can use to drive
the deployment. It runs on the Undercloud machine on ``http://localhost/dashboard``


Example of how to access Tuskar-UI:

Considering that Tuskar-UI runs in a Undercloud VM and virt host is a remote host
machine, to acces the UI in the browser, follow these steps:

#. On host machine create ssh tunnel from undercloud vm to virt host::

    ssh -g -L 8080:127.0.0.1:80 root@<undercloud_vm_ip>

#. On Undercloud VM edit ``/etc/openstack-dashboard/local_settings`` and add virt host ``hostname`` to ``ALLOWED_HOSTS`` array

#. Restart Apache::

    systemctl restart httpd

#. Allow port ``8080`` on host machine::

    firewall-cmd --permanent --zone=public --add-port=8080/tcp

#. Navigate to ``http://<virt_host_hostname>:8080/dashboard`` in the browser
