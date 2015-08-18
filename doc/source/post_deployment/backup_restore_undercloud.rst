Backing up and Restoring your Undercloud
========================================

Backing up your Undercloud
--------------------------

In order to backup your undercloud you need to make sure the following items are backed up

* All MariaDB databases on the undercloud node
* MariaDB configuration file on undercloud (so we can restore databases accurately)
* All glance image data in /var/lib/glance/images
* All swift data in /srv/node
* All data in stack users home directory

The following commands can be used to perform a backup of all data from the undercloud node::

  mysqldump --opt --all-databases > /root/undercloud-all-databases.sql
  tar -czf undercloud-backup-`date +%F`.tar.gz undercloud-all-databases.sql /etc/my.cnf.d/server.cnf /var/lib/glance/images /srv/node /home/stack

Restoring a backup of your Undercloud on a Fresh Machine
--------------------------------------------------------
The following restore process assumes you are recovering from a failed undercloud node where you have to reinstall it from scratch.
It assumes that the hardware layout is the same, and the hostname and undercloud settings of the machine will be the same as well.
Once the machine is installed and is in a clean state, re-enable all the subscriptions/repositories needed to install and run RDO Manager

Then install mariadb server with::

  yum install -y mariadb-server

Now restore the MariaDB configuration file and database backup, then start the MariaDB server and load the backup in::

  tar -xzC / -f undercloud-backup-$DATE.tar.gz etc/my.cnf.d/server.cnf /root/undercloud-all-databases.sql
  # Edit /etc/my.cnf.d/server.cnf and comment out 'bind-address'
  systemctl start mariadb
  cat /root/undercloud-all-databases.sql | mysql
  # Now we need to clean out some old permissions to be recreated
  for i in ceilometer glance heat ironic keystone neutron nova tuskar;do mysql -e "drop user $i";done
  mysql -e 'flush privileges'

Now create the stack user and restore the stack users home directory::

  sudo useradd stack
  sudo passwd stack  # specify a password

  echo "stack ALL=(root) NOPASSWD:ALL" | sudo tee -a /etc/sudoers.d/stack
  sudo chmod 0440 /etc/sudoers.d/stack

Next restore the stack users home directory::

  tar -xzC / -f undercloud-backup-$DATE.tar.gz home/stack

We have to now install the swift and glance base packages, and then restore their data::

  yum install -y openstack-glance openstack-swift
  tar -xzC / -f undercloud-backup-$DATE.tar.gz srv/node var/lib/glance/images
  # Confirm data is owned by correct user
  chown -R swift: /srv/node
  chown -R glance: /var/lib/glance/images

Finally we rerun the undercloud installation from the stack user, making sure to run it in the stack user home dir::

  su - stack
  sudo yum install -y python-rdomanager-oscplugin
  # Double check hostname is correctly set in /etc/hosts
  openstack install undercloud
