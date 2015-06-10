# Copyright 2015 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import ConfigParser
import copy
import errno
import getpass
import hashlib
import logging
import os
import platform
import socket
import StringIO
import subprocess
import uuid

from novaclient import client as novaclient
from novaclient import exceptions
from oslo_config import cfg
import six


CONF_PATH = os.path.expanduser('~/undercloud.conf')
# NOTE(bnemec): Deprecated
ANSWERS_PATH = os.path.expanduser('~/instack.answers')
PASSWORD_PATH = os.path.expanduser('~/undercloud-passwords.conf')
LOG_FILE = os.path.expanduser('~/.instack/install-undercloud.log')
DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
try:
    os.makedirs(os.path.dirname(LOG_FILE))
except OSError as e:
    if e.errno != errno.EEXIST:
        raise
logging.basicConfig(filename=LOG_FILE,
                    format=DEFAULT_LOG_FORMAT,
                    level=DEFAULT_LOG_LEVEL)
LOG = logging.getLogger(__name__)
LOG.addHandler(logging.StreamHandler())
CONF = cfg.CONF
COMPLETION_MESSAGE = """
#############################################################################
instack-install-undercloud complete.

The file containing this installation's passwords is at
%(password_path)s.

There is also a stackrc file at %(stackrc_path)s.

These files are needed to interact with the OpenStack services, and should be
secured.

#############################################################################
"""


# When adding new options to the lists below, make sure to regenerate the
# sample config by running "tox -e genconfig" in the project root.
_opts = [
    cfg.StrOpt('deployment_mode',
               default='poc',
               choices=['poc', 'scale'],
               help=('Deployment mode for this undercloud.  "poc" will allow '
                     'deployment of a single role to heterogenous hardware. '
                     '"scale" will allow deployment of a single role only to '
                     'homogenous hardware.'
                     )
               ),
    cfg.StrOpt('image_path',
               default='.',
               help=('Local file path to the necessary images. The path '
                     'should be a directory readable by the current user '
                     'that contains the full set of images.'),
               ),
    cfg.StrOpt('local_ip',
               default='192.0.2.1/24',
               help=('IP information for the interface on the Undercloud '
                     'that will be handling the PXE boots and DHCP for '
                     'Overcloud instances.  The IP portion of the value will '
                     'be assigned to the network interface defined by '
                     'local_interface, with the netmask defined by the '
                     'prefix portion of the value.')
               ),
    cfg.StrOpt('undercloud_public_vip',
               default='192.0.2.2',
               help=('Virtual IP address to use for the public endpoints of '
                     'Undercloud services.')
               ),
    cfg.StrOpt('undercloud_admin_vip',
               default='192.0.2.3',
               help=('Virtual IP address to use for the admin endpoints of '
                     'Undercloud services.')
               ),
    cfg.StrOpt('undercloud_service_certificate',
               help=('Certificate file to use for OpenStack service SSL '
                     'connections.')
               ),
    cfg.StrOpt('local_interface',
               default='eth1',
               help=('Network interface on the Undercloud that will be '
                     'handling the PXE boots and DHCP for Overcloud '
                     'instances.')
               ),
    cfg.StrOpt('masquerade_network',
               default='192.0.2.0/24',
               help=('Network that will be masqueraded for external access, '
                     'if required.')
               ),
    cfg.StrOpt('dhcp_start',
               default='192.0.2.5',
               help=('Start of DHCP allocation range for PXE and DHCP of '
                     'Overcloud instances.')
               ),
    cfg.StrOpt('dhcp_end',
               default='192.0.2.24',
               help=('End of DHCP allocation range for PXE and DHCP of '
                     'Overcloud instances.')
               ),
    cfg.StrOpt('network_cidr',
               default='192.0.2.0/24',
               help=('Network CIDR for the Neutron-managed network for '
                     'Overcloud instances.')
               ),
    cfg.StrOpt('network_gateway',
               default='192.0.2.1',
               help=('Network gateway for the Neutron-managed network for '
                     'Overcloud instances.')
               ),
    cfg.StrOpt('discovery_interface',
               default='br-ctlplane',
               help=('Network interface on which discovery dnsmasq will '
                     'listen.  If in doubt, use the default value.')
               ),
    cfg.StrOpt('discovery_iprange',
               default='192.0.2.100,192.0.2.120',
               help=('Temporary IP range that will be given to nodes during '
                     'the discovery process.  Should not overlap with the '
                     'range defined by dhcp_start and dhcp_end, but should '
                     'be in the same network.')
               ),
    cfg.BoolOpt('discovery_runbench',
                default=False,
                help='Whether to run benchmarks when discovering nodes.'
                ),
    cfg.BoolOpt('undercloud_debug',
                default=True,
                help=('Whether to enable the debug log level for Undercloud '
                      'OpenStack services.')
                ),
]

# Passwords, tokens, hashes
_auth_opts = [
    cfg.StrOpt('undercloud_db_password',
               help=('Password used for MySQL databases. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_admin_token',
               help=('Keystone admin token. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_admin_password',
               help=('Keystone admin password. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_glance_password',
               help=('Glance service password. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_heat_password',
               help=('Heat service password. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_neutron_password',
               help=('Neutron service password. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_nova_password',
               help=('Nova service password. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_ironic_password',
               help=('Ironic service password. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_tuskar_password',
               help=('Tuskar service password. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_ceilometer_password',
               help=('Ceilometer service password. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_ceilometer_metering_secret',
               help=('Ceilometer metering secret. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_ceilometer_snmpd_user',
               help=('Ceilometer snmpd user. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_ceilometer_snmpd_password',
               help=('Ceilometer snmpd password. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_swift_password',
               help=('Swift service password. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_rabbit_cookie',
               help=('Rabbitmq cookie. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_rabbit_password',
               default='guest',
               help='Rabbitmq password.'
               ),
    cfg.StrOpt('undercloud_rabbit_username',
               default='guest',
               help='Rabbitmq username.'
               ),
    cfg.StrOpt('undercloud_heat_stack_domain_admin_password',
               help=('Heat stack domain admin password. '
                     'If left unset, one will be automatically generated.')
               ),
    cfg.StrOpt('undercloud_swift_hash_suffix',
               help=('Swift hash suffix. '
                     'If left unset, one will be automatically generated.')
               ),
]
CONF.register_opts(_opts)
CONF.register_opts(_auth_opts, group='auth')


def list_opts():
    return [(None, copy.deepcopy(_opts)),
            ('auth', copy.deepcopy(_auth_opts)),
            ]


def _load_config():
    conf_params = []
    if os.path.isfile(PASSWORD_PATH):
        conf_params += ['--config-file', PASSWORD_PATH]
    if os.path.isfile(CONF_PATH):
        conf_params += ['--config-file', CONF_PATH]
    CONF(conf_params)


def _run_command(args, env=None, name=None):
    """Run the command defined by args and return its output

    :param args: List of arguments for the command to be run.
    :param env: Dict defining the environment variables. Pass None to use
        the current environment.
    :param name: User-friendly name for the command being run. A value of
        None will cause args[0] to be used.
    """
    if name is None:
        name = args[0]
    try:
        return subprocess.check_output(args,
                                       stderr=subprocess.STDOUT,
                                       env=env)
    except subprocess.CalledProcessError as e:
        LOG.error('%s failed: %s', name, e.output)
        raise


def _run_live_command(args, env=None, name=None):
    """Run the command defined by args and log its output

    Takes the same arguments as _run_command, but runs the process
    asynchronously so the output can be logged while the process is still
    running.
    """
    process = subprocess.Popen(args, env=env,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    while True:
        line = process.stdout.readline()
        if line:
            LOG.info(line.rstrip())
        if line == '' and process.poll() is not None:
            break
    if process.returncode != 0:
        raise RuntimeError('%s failed. See log for details.', name)


def _check_hostname():
    """Check system hostname configuration

    Rabbit requires a pretty specific hostname configuration.  This attempts
    to verify the configuration is correct before continuing with
    installation.
    """
    LOG.info('Checking for a FQDN hostname...')
    args = ['sudo', 'hostnamectl', '--static']
    detected_static_hostname = _run_command(args, name='hostnamectl').rstrip()
    LOG.info('Static hostname detected as %s', detected_static_hostname)
    args = ['sudo', 'hostnamectl', '--transient']
    detected_transient_hostname = _run_command(args,
                                               name='hostnamectl').rstrip()
    LOG.info('Transient hostname detected as %s', detected_transient_hostname)
    if detected_static_hostname != detected_transient_hostname:
        LOG.error('Static hostname "%s" does not match transient hostname '
                  '"%s".', detected_static_hostname,
                  detected_transient_hostname)
        LOG.error('Use hostnamectl to set matching hostnames.')
        raise RuntimeError('Static and transient hostnames do not match')
    with open('/etc/hosts') as hosts_file:
        for line in hosts_file:
            if (not line.lstrip().startswith('#') and
                    detected_static_hostname in line.split()):
                break
        else:
            LOG.error('Static hostname not set in /etc/hosts.')
            LOG.error('Please add a line to /etc/hosts for the static '
                      'hostname.')
            raise RuntimeError('Static hostname not set in /etc/hosts')


def _generate_password():
    """Create a random password

    Copied from rdomanager-oscplugin.  This should eventually live in
    tripleo-common.
    """
    uuid_str = six.text_type(uuid.uuid1()).encode("UTF-8")
    return hashlib.sha1(uuid_str).hexdigest()


def _generate_environment(instack_root):
    """Generate an environment dict for instack

    The returned dict will have the necessary values for use as the env
    parameter when calling instack via the subprocess module.

    :param instack_root: The path containing the instack-undercloud elements
        and json files.
    """
    instack_env = os.environ
    # Rabbit uses HOSTNAME, so we need to make sure it's right
    instack_env['HOSTNAME'] = socket.gethostname()

    # Find the paths we need
    json_file_dir = '/usr/share/instack-undercloud/json-files'
    if not os.path.isdir(json_file_dir):
        json_file_dir = os.path.join(instack_root, 'json-files')
    instack_undercloud_elements = '/usr/share/instack-undercloud'
    if not os.path.isdir(instack_undercloud_elements):
        instack_undercloud_elements = os.path.join(instack_root, 'elements')
    tripleo_puppet_elements = '/usr/share/tripleo-puppet-elements'
    if not os.path.isdir(tripleo_puppet_elements):
        tripleo_puppet_elements = os.path.join(os.getcwd(),
                                               'tripleo-puppet-elements',
                                               'elements')
    if 'ELEMENTS_PATH' in os.environ:
        instack_env['ELEMENTS_PATH'] = os.environ['ELEMENTS_PATH']
    else:
        instack_env['ELEMENTS_PATH'] = (
            '%s:%s:'
            '/usr/share/tripleo-image-elements:'
            '/usr/share/diskimage-builder/elements'
        ) % (tripleo_puppet_elements, instack_undercloud_elements)

    # Distro-specific values
    distro = platform.linux_distribution()[0]
    if distro.startswith('Red Hat Enterprise Linux'):
        instack_env['NODE_DIST'] = os.environ.get('NODE_DIST') or 'rhel7'
        instack_env['JSONFILE'] = (
            os.environ.get('JSONFILE') or
            os.path.join(json_file_dir, 'rhel-7-undercloud-packages.json')
        )
        instack_env['REG_METHOD'] = 'disable'
        instack_env['REG_HALT_UNREGISTER'] = '1'
    elif distro.startswith('CentOS'):
        instack_env['NODE_DIST'] = os.environ.get('NODE_DIST') or 'centos7'
        instack_env['JSONFILE'] = (
            os.environ.get('JSONFILE') or
            os.path.join(json_file_dir, 'centos-7-undercloud-packages.json')
        )
    elif distro.startswith('Fedora'):
        instack_env['NODE_DIST'] = os.environ.get('NODE_DIST') or 'fedora'
        raise Exception('Fedora is not currently supported')
    else:
        raise Exception('%s is not supported' % distro)

    # Do some fiddling to retain answers file support for now
    answers_parser = ConfigParser.ConfigParser()
    if os.path.isfile(ANSWERS_PATH):
        config_answers = StringIO.StringIO()
        config_answers.write('[answers]\n')
        with open(ANSWERS_PATH) as f:
            config_answers.write(f.read())
        config_answers.seek(0)
        answers_parser.readfp(config_answers)

    # Convert conf opts to env values
    for opt in _opts:
        env_name = opt.name.upper()
        if answers_parser.has_option('answers', env_name):
            LOG.warning('Using value for %s from instack.answers. This '
                        'behavior is deprecated.  undercloud.conf should '
                        'now be used for configuration.', env_name)
            instack_env[env_name] = answers_parser.get('answers', env_name)
        else:
            instack_env[env_name] = six.text_type(CONF[opt.name])
    # Opts that needs extra processing
    if instack_env['DISCOVERY_RUNBENCH'] not in ['0', '1']:
        instack_env['DISCOVERY_RUNBENCH'] = ('1' if CONF.discovery_runbench
                                             else '0')
    instack_env['PUBLIC_INTERFACE_IP'] = instack_env['LOCAL_IP']
    instack_env['LOCAL_IP'] = instack_env['LOCAL_IP'].split('/')[0]
    with open(PASSWORD_PATH, 'w') as password_file:
        password_file.write('[auth]\n')
        for opt in _auth_opts:
            env_name = opt.name.upper()
            if answers_parser.has_option('answers', env_name):
                LOG.warning('Using value for %s from instack.answers. This '
                            'behavior is deprecated.  undercloud.conf should '
                            'now be used for configuration.', env_name)
                value = answers_parser.get('answers', env_name)
            else:
                value = CONF.auth[opt.name]
            if not value:
                value = _generate_password()
                LOG.info('Generated new password for %s', opt.name)
            instack_env[env_name] = value
            password_file.write('%s=%s\n' % (opt.name, value))

    return instack_env


def _run_instack(instack_env):
    args = ['sudo', '-E', 'instack', '-p', instack_env['ELEMENTS_PATH'],
            '-j', instack_env['JSONFILE'],
            ]
    LOG.info('Running instack')
    _run_live_command(args, instack_env, 'instack')
    LOG.info('Instack completed successfully')


def _run_orc(instack_env):
    args = ['sudo', 'os-refresh-config']
    LOG.info('Running os-refresh-config')
    _run_live_command(args, instack_env, 'os-refresh-config')
    LOG.info('os-refresh-config completed successfully')


def _extract_from_stackrc(name):
    """Extract authentication values from stackrc

    :param name: The value to be extracted.  For example: OS_USERNAME or
        OS_AUTH_URL.
    """
    with open(os.path.expanduser('~/stackrc')) as f:
        for line in f:
            if name in line:
                parts = line.split('=')
                return parts[1].rstrip()


def _configure_ssh_keys():
    """Configure default ssh keypair in Nova

    Generates a new ssh key for the current user if one does not already
    exist, then uploads that to Nova as the 'default' keypair.
    """
    id_path = os.path.expanduser('~/.ssh/id_rsa')
    if not os.path.isfile(id_path):
        args = ['ssh-keygen', '-t', 'rsa', '-N', '', '-f', id_path]
        _run_command(args)
        LOG.info('Generated new ssh key in ~/.ssh/id_rsa')

    args = ['sudo', 'cp', '/root/stackrc', os.path.expanduser('~')]
    _run_command(args, name='Copy stackrc')
    args = ['sudo', 'chown', getpass.getuser() + ':',
            os.path.expanduser('~/stackrc')]
    _run_command(args, name='Chown stackrc')
    password = _run_command(['hiera', 'admin_password']).rstrip()
    user = _extract_from_stackrc('OS_USERNAME')
    auth_url = _extract_from_stackrc('OS_AUTH_URL')
    tenant = _extract_from_stackrc('OS_TENANT')
    os_cacert = _extract_from_stackrc('OS_CACERT')
    nova = novaclient.Client(2, user, password, tenant, auth_url,
                             cacert=os_cacert)
    try:
        nova.keypairs.get('default')
    except exceptions.NotFound:
        with open(id_path + '.pub') as pubkey:
            nova.keypairs.create('default', pubkey.read().rstrip())


def install(instack_root):
    """Install the undercloud

    :param instack_root: The path containing the instack-undercloud elements
        and json files.
    """
    LOG.info('Logging to %s', LOG_FILE)
    _load_config()
    _check_hostname()
    instack_env = _generate_environment(instack_root)
    _run_instack(instack_env)
    # NOTE(bnemec): I removed the conditional running of os-refresh-config.
    # To my knowledge it wasn't really being used anymore, and if we do still
    # need it, it should be reimplemented as a client parameter instead of
    # an input env var.
    # TODO(bnemec): Do we still need INSTACK_ROOT?
    instack_env['INSTACK_ROOT'] = os.environ.get('INSTACK_ROOT') or ''
    _run_orc(instack_env)
    _configure_ssh_keys()
    _run_command(['sudo', 'rm', '-f', '/tmp/svc-map-services'], None, 'rm')
    LOG.info(COMPLETION_MESSAGE, {'password_path': PASSWORD_PATH,
             'stackrc_path': os.path.expanduser('~/stackrc')})
