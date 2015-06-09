RDO-Manager Introduction
========================

RDO-Manager is an OpenStack Deployment & Management tool for RDO. It is based on
`OpenStack TripleO <https://wiki.openstack.org/wiki/TripleO>`_ project and its
philosophy is inspired by `SpinalStack <http://spinal-stack.readthedocs.org/en/
latest/>`_.

The TripleO architecture is based around using OpenStack services to deploy and
manage your OpenStack environment.  Key concepts are the "undercloud" which is
the node containing your deployment and management services, and the
"overcloud" which is the deployed cloud configured over multiple nodes.

.. image:: ../_images/UndercloudOvercloudOverview.svg

RDO manager provides semi-automated configuration of your undercloud
environment, after which it is possible to deploy an overcloud containing your
desired number of overcloud resource nodes using either UI or CLI interfaces.

Overcloud resource nodes are categorized by role:

Controller
    The Controller nodes contain the core OpenStack API services, RPC broker, Pacemaker/Corosync for HA, and the Ceph Monitor service.  The minimum number of Controller nodes is 1.

Compute
    The Compute nodes contain the nova hypervisor components (nova-compute, KVM) and can be scaled out to add compute capacity to your cloud.  The minimum number of Compute nodes is 1.

BlockStorage
    The BlockStorage nodes are optional and provide LVM based cinder storage that can be scaled independently of the Controller role.

CephStorage
    The CephStorage nodes are optional and provides Ceph OSD nodes which can be scaled independently of the Controller role.  By default when CephStorage nodes are deployed RDO-Manager configures Nova, Glance and Cinder to be backed by Ceph.

SwiftStorage
    The SwiftStorage nodes are optional and provide Swift Object storage, which can scaled independently of the Controller role.

Useful links:

* `RDO-Manager Home Page <http://rdoproject.org/RDO-Manager>`_

* `RDO-Manager Repositories <http://github.com/rdo-management>`_

* `TripleO Documentation <http://docs.openstack.org/developer/tripleo-incubator/README.html>`_.

* :doc:`components`


.. toctree::
   :hidden:

   Architecture <architecture>
   Components <components>
