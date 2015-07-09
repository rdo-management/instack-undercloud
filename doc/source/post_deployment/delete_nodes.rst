.. _delete_nodes:

Deleting Overcloud Nodes
========================

You can delete specific nodes from an overcloud with command::

    openstack overcloud node delete --stack $STACK --plan $PLAN_UUID <list of nova instance IDs>

This command updates number of nodes in tuskar plan and then updates heat stack
with updated numbers and list of resource IDs (which represent nodes) to be
deleted.

.. note::
   List of nova instance IDs can be listed with command::

       nova list

Deleting nodes without using Tuskar
-----------------------------------
If the overcloud was deployed from heat templates directly without using
a tuskar plan then you can delete specific nodes by passing them in an
extra heat environment file. First create the environment file which
contains nodes to be deleted, for example to delete first compute node
the file should look like this::

   parameters:
     ComputeRemovalPolicies:
         [{'resource_list': ['0']}]

And then re-deploy the overcloud with updated number of nodes and the extra
environment file::

   openstack overcloud deploy  --use-tripleo-heat-templates --compute-scale <number> -e <path to extra yaml file>
