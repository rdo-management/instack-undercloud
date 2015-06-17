Scaling overcloud nodes
=======================

Add nodes
---------
If you want to increase resource capacity of a running overcloud, you can start
more servers of a selected role:

  ::

      openstack overcloud scale stack -r role_name-role_version -n number plan stack

Example of increasing number of compute nodes to 20 using plan 'overcloud' and
heat stack 'overcloud':

  ::

      openstack overcloud scale stack -r Compute-1 -n 2 overcloud overcloud

.. note:: Both role names and role versions can be listed with command:

  ::

      tuskar role-list


Remove nodes
------------
Nodes can be removed from an overcloud by:

  ::

      openstack overcloud node delete --stack stack --plan plan <list of nova instance IDs>

.. note:: List of nova instance IDs can be listed with command:

  ::

      nova list
