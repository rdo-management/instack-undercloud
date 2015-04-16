RDO-Manager Introduction
========================

.. _OpenStack TripleO: https://wiki.openstack.org/wiki/TripleO


.. toctree::
   :maxdepth: 1

   Overview <overview>
   Architecture <architecture>
   Components <components>

RDO-Manager is an OpenStack Deployment & Management tool for RDO. It combines
the best from the `OpenStack TripleO`_
and `SpinalStack <http://spinal-stack.readthedocs.org/en/latest/>`_ projects.

RDO-Manager Pages: http://rdoproject.org/RDO-Manager

RDO-Manager Repositories: http://github.com/rdo-management


Documentation Conventions
-------------------------

Some steps in the following instructions only apply to certain environments,
such as deployments to real baremetal and deployments using RHEL.  These
steps are marked as follows:

.. admonition:: RHEL
   :class: rhel-tag

   Step that should only be run when using RHEL

.. admonition:: CentOS
   :class: centos-tag

   Step that should only be run when using CentOS


.. admonition:: Baremetal
   :class: baremetal-tag

   Step that should only be run when deploying to baremetal

.. admonition:: Virt
   :class: virt-tag

   Step that should only be run when deploying to virtual machines

.. admonition:: Ceph
   :class: ceph-tag

   Step that should only be run when deploying Ceph for use by the Overcloud

Any such steps should *not* be run if the target environment does not match
the section marking.
