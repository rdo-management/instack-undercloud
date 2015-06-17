Scaling Out Overcloud Roles
===========================
If you want to increase resource capacity of a running overcloud, you can start
more servers of a selected role. The following command will update overcloud
plan in Tuskar with new role count and then it will trigger heat stack update
with updated templates of overcloud plan.


  ::

      openstack overcloud scale stack -r role_name-role_version -n number plan stack

Example of increasing count of compute nodes to 5 using plan 'overcloud' and
heat stack 'overcloud':

  ::

      openstack overcloud scale stack -r Compute-1 -n 5 overcloud overcloud

.. note:: Both role names and role versions can be listed with command:

  ::

      tuskar role-list

.. note:: Scaling out assumes that newely added nodes has already been
          registered in ironic.
