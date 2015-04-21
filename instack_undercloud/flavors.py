# Copyright 2015 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import os

from novaclient import client as novaclient
from os_cloud_config import flavors

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


# TODO(bnemec): These need to be overridable somehow
_CONTROL_DEFAULT_RAM = 4096
_CONTROL_DEFAULT_VCPUS = 1
_CONTROL_DEFAULT_DISK = 40
_COMPUTE_DEFAULT_RAM = 4096
_COMPUTE_DEFAULT_VCPUS = 1
_COMPUTE_DEFAULT_DISK = 40
_CEPH_DEFAULT_RAM = 4096
_CEPH_DEFAULT_VCPUS = 1
_CEPH_DEFAULT_DISK = 40


class TripleOFlavors(object):
    """Manages the flavors needed for a TripleO deployment"""
    def __init__(self):
        super(TripleOFlavors, self).__init__()
        # TODO(bnemec): Authentication details or a valid novaclient instance
        # should probably be passed in instead of read from the env.
        username = os.environ.get('OS_USERNAME')
        password = os.environ.get('OS_PASSWORD')
        tenant = os.environ.get('OS_TENANT_NAME')
        auth_url = os.environ.get('OS_AUTH_URL')
        cacert = os.environ.get('OS_CACERT')
        if not username or not password or not tenant or not auth_url:
            raise RuntimeError('Source an appropriate rc file first')

        self._nova = novaclient.Client(2, username, password, tenant,
                                      auth_url, cacert=cacert)

    def ensure(self):
        """Register the required flavors with Nova"""
        required_flavors = []
        baremetal_control = {'name': 'baremetal_control',
                             'memory': _CONTROL_DEFAULT_RAM,
                             'cpu': _CONTROL_DEFAULT_VCPUS,
                             'disk': _CONTROL_DEFAULT_DISK,
                             'extra_specs': {'profile': 'control'},
                             'arch': 'x86_64',
                             'ephemeral': 0,
                             }
        required_flavors.append(baremetal_control)
        baremetal_compute = {'name': 'baremetal_compute',
                             'memory': _COMPUTE_DEFAULT_RAM,
                             'cpu': _COMPUTE_DEFAULT_VCPUS,
                             'disk': _COMPUTE_DEFAULT_DISK,
                             'extra_specs': {'profile': 'compute'},
                             'arch': 'x86_64',
                             'ephemeral': 0,
                             }
        required_flavors.append(baremetal_compute)
        baremetal_ceph = {'name': 'baremetal_ceph-storage',
                          'memory': _CEPH_DEFAULT_RAM,
                          'cpu': _CEPH_DEFAULT_VCPUS,
                          'disk': _CEPH_DEFAULT_DISK,
                          'extra_specs': {'profile': 'ceph-storage'},
                          'arch': 'x86_64',
                          'ephemeral': 0,
                          }
        required_flavors.append(baremetal_ceph)
        flavors.create_flavors_from_list(self._nova, required_flavors,
                                         '', '')
        LOG.info('Finished configuring flavors: %s', required_flavors)


if __name__ == '__main__':
    LOG.warn('Calling this module directly is deprecated.')
    LOG.warn('It should be called from openstackclient.')
    tripleo_flavors = TripleOFlavors()
    tripleo_flavors.ensure()
