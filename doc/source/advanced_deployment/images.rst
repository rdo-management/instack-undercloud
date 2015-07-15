Provisioning Images
===================

Provisioning images contain the software to be installed on overcloud nodes.
In order to perform an overcloud deployment, provisioning images must be first
obtained (either by building them on the undercloud, or downloading them from
an external source). The images then need to be uploaded into the undercloud
Glance. Finally, before deployment is run, each role needs to assocated with a
provisioning image.

Operations for manipulating provisioning images
-----------------------------------------------

* Build images::

    openstack overcloud image build

  Use this command to build provisioning images. To see all the related
  options, run::

    openstack help overcloud image build

  Example::

    openstack overcloud image build --all

  The above command will build all the necessary images for a basic overcloud
  deployment.


* Upload images::

    openstack overcloud image upload

  Use this command to load images into the undercloud Glance. To see all the
  related options, run::

    openstack help overcloud image upload

  Example::

    openstack overcloud image upload

  The above command will upload all the images found in the current directory
  into the undercloud Glance.


* Other operations on Glance images::

    openstack image list
    openstack image create
    openstack image show
    openstack image delete
    etc.

  To get a full list of supported commands, run::

    openstack help image

