Deploying Manila in the Overcloud
=================================

This guide assumes that your undercloud is already installed and ready to
deploy an overcloud with Manila enabled.

Deploying the Overcloud
-----------------------
.. note::

    The :doc:`template_deploy` doc has a more detailed explanation of the
    following steps.

1. Copy the Manila driver-specific configuration file to your home directory:

  - Generic driver:

    sudo cp /usr/share/openstack-tripleo-heat-templates/environments/manila-generic.config.yaml ~

  - NetApp driver:

    sudo cp /usr/share/openstack-tripleo-heat-templates/environments/manila-netapp.config.yaml ~

2. Edit the permissions (user is typically ``stack``):

    sudo chown $USER ~/manila-*-config.yaml
    sudo chmod 755 ~/manila-*-config.yaml

3. Edit the parameters in this file to fit your requirements.

.. note::

    If you're using the generic driver, ensure that the service image details
    in this file correspond to the service image you intend to load.

4. Continue following the TripleO instructions for deploying an overcloud.
Before entering the command to deploy the overcloud, add the environment
file that you just configured as an argument:

    openstack undercloud install --templates -e ~/manila-netapp-config.yaml

5. Wait for the completion of the overcloud deployment process.


Creating the Share
------------------

.. note::

    The following steps will refer to running commands as an admin user or a
    tenant user. Sourcing the ``overcloudrc`` file will authenticate you as
    the admin user. You can then create a tenant user and use environment
    files to switch between them.

1. Upload a service image:

.. note::

    This step is only required for the generic driver.

  - Download a Manila service image to be used for share servers.
  - Upload this service image to Glance so that Manila can use it [tenant]:
         glance image-create --name manila-service-image --disk-format qcow2 --container-format bare --file manila_service_image.qcow2

2. Create a share network to host the shares:

  - List the networks and subnets [tenant]:

    neutron net-list && neutron subnet-list

  - Create a share network (typically using the private ``default-net``
  net/subnet) [tenant]:

    manila share-network-create --neutron-net-id [net] --neutron-subnet-id [subnet]

  - Take a note of the ID of this new share network.

3. Create a new share type [admin]:

    manila type-create [name] [yes/no]

  - The boolean value is for specifying if the driver handles share servers.

4. Create the share [admin]:

    manila create --share-network [share net ID] --share-type [type name] [nfs/cifs] [size of share]


Accessing the Share
-------------------

1. To access the share, create a new VM (or choose an existing one on the
network). Ensure that the VM is created with the same Neutron network that was
used to create the share network.

    nova boot --image [image ID] --flavor [flavor ID] --nic net-id=[network ID] [name]

2. Allow access to the VM you just created:
    manila access-allow [share ID] ip [IP address of VM]

3. Run ``manila list`` and ensure that the share is available and note the
export location.

4. Log into the VM:
    ssh [user]@[IP]

.. note::

    You may need to configure Neutron security rules to access the
    VM. That is not in the scope of this document, so it will not be covered
    here.

5. In the VM, execute:
    sudo mount [export location] [folder to mount to]

6. Ensure the share is mounted by looking at the bottom of the output of the
``mount`` command.

7. That's it - you're ready to start using Manila!

