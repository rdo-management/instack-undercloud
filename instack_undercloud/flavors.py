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


class _FlavorNotFound(Exception):
    pass


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
        self._all_flavors = self._nova.flavors.list()

    def _find_flavor(self, name):
        """Find a flavor by name"""
        matching_flavors = [i for i in self._all_flavors if i.name == name]
        if len(matching_flavors) == 0:
            raise _FlavorNotFound('No matching flavor found')
        if len(matching_flavors) > 1:
            LOG.warning('Multiple flavor matches for %s found.', name)
        return matching_flavors[0]

    def _ensure_flavor(self, name, ram, vcpus, disk, profile):
        """Ensure the requested flavor exists

        Creates the flavor if necessary, and sets the appropriate flavor keys
        on it.
        """
        try:
            flavor = self._find_flavor(name)
            LOG.info('%s flavor already exists.', name)
        except _FlavorNotFound:
            flavor = self._nova.flavors.create(name, ram, vcpus, disk)
            LOG.info('Created flavor %s.', name)

        keys = {'cpu_arch': 'x86_64', 'profile': profile}
        flavor.set_keys(keys)
        LOG.info('Set keys on flavor %s to %s', name, keys)

    def ensure(self):
        """Register the required flavors with Nova"""
        self._ensure_flavor('baremetal_control',
                            _CONTROL_DEFAULT_RAM,
                            _CONTROL_DEFAULT_VCPUS,
                            _CONTROL_DEFAULT_DISK,
                            'control')
        self._ensure_flavor('baremetal_compute',
                            _COMPUTE_DEFAULT_RAM,
                            _COMPUTE_DEFAULT_VCPUS,
                            _COMPUTE_DEFAULT_DISK,
                            'compute')
        self._ensure_flavor('baremetal_ceph-storage',
                            _CEPH_DEFAULT_RAM,
                            _CEPH_DEFAULT_VCPUS,
                            _CEPH_DEFAULT_DISK,
                            'ceph-storage')


if __name__ == '__main__':
    LOG.warn('Calling this module directly is deprecated.')
    LOG.warn('It should be called from openstackclient.')
    flavors = TripleOFlavors()
    flavors.ensure()
