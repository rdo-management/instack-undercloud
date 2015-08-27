Troubleshooting openstack undercloud install on Baremetal servers
=================================================================

* If the openstack undercloud install command fails with the following
  error:
      Error: curl -k --noproxy localhost --retry 30 --retry-delay 6 -f 
      -L -o /var/lib/rabbitmq/rabbitmqadmin 
       http://guest:guest@localhost:15672/cli/rabbitmqadmin 
       returned 7 instead of one of [0]
      Error: /Stage[main]/Rabbitmq::Install::Rabbitmqadmin/Staging
      ::File[rabbitmqadmin]/Exec[/var/lib/rabbitmq/rabbitmqadmin]/returns:
       change from notrun to 0 failed: curl -k --noproxy localhost 
      --retry 30 --retry-delay 6 -f -L -o /var/lib/rabbitmq/rabbitmqadmin 
      http://guest:guest@localhost:15672/cli/rabbitmqadmin returned 7 
      instead of one of [0]
  RabbitMq is typically listening on the interface br-ctlplane0 which
  has IP address 192.0.2.1. You can do ps-ef | grep rabbit and look
  for which IP address it is listening on. This IP address needs to
  be mapped to localhost in the /etc/hosts file

* If the openstack undercloud install command fails with error:
     Cannot ssh root@192.0.2.1 during keystone init
  Check if the root user has ssh access by looking at the
  /etc/ssh/sshd_config file.

* If the openstack undercloud install command fails with error:
     Eth1 cannot be found
  Make sure that the interfaces on the servers are labeled as
  eth0 and eth1




