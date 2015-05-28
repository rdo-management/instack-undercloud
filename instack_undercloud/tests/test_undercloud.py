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
import io
import os
import StringIO
import subprocess

import fixtures
import mock
from novaclient import exceptions
from oslo.config import fixture as config_fixture
from oslotest import base
from oslotest import mockpatch

from instack_undercloud import undercloud


undercloud._configure_logging(undercloud.DEFAULT_LOG_LEVEL, None)


class TestUndercloud(base.BaseTestCase):
    @mock.patch('instack_undercloud.undercloud._configure_logging')
    @mock.patch('instack_undercloud.undercloud._check_hostname')
    @mock.patch('instack_undercloud.undercloud._run_command')
    @mock.patch('instack_undercloud.undercloud._configure_ssh_keys')
    @mock.patch('instack_undercloud.undercloud._run_orc')
    @mock.patch('instack_undercloud.undercloud._run_instack')
    @mock.patch('instack_undercloud.undercloud._generate_environment')
    @mock.patch('instack_undercloud.undercloud._load_config')
    def test_install(self, mock_load_config, mock_generate_environment,
                     mock_run_instack, mock_run_orc, mock_configure_ssh_keys,
                     mock_run_command, mock_check_hostname,
                     mock_configure_logging):
        fake_env = mock.MagicMock()
        mock_generate_environment.return_value = fake_env
        undercloud.install('.')
        mock_generate_environment.assert_called_with('.')
        mock_run_instack.assert_called_with(fake_env)
        mock_run_orc.assert_called_with(fake_env)
        mock_run_command.assert_called_with(
            ['sudo', 'rm', '-f', '/tmp/svc-map-services'], None, 'rm')

    def test_generate_password(self):
        first = undercloud._generate_password()
        second = undercloud._generate_password()
        self.assertNotEqual(first, second)

    def test_extract_from_stackrc(self):
        with open(os.path.expanduser('~/stackrc'), 'w') as f:
            f.write('OS_USERNAME=aturing\n')
            f.write('OS_AUTH_URL=http://bletchley:5000/v2.0\n')
        self.assertEqual('aturing',
                         undercloud._extract_from_stackrc('OS_USERNAME'))
        self.assertEqual('http://bletchley:5000/v2.0',
                         undercloud._extract_from_stackrc('OS_AUTH_URL'))


class TestCheckHostname(base.BaseTestCase):
    @mock.patch('instack_undercloud.undercloud._run_command')
    def test_correct(self, mock_run_command):
        mock_run_command.side_effect = ['test-hostname', 'test-hostname']
        self.useFixture(fixtures.EnvironmentVariable('HOSTNAME',
                                                     'test-hostname'))
        fake_hosts = io.StringIO(u'127.0.0.1 test-hostname\n')
        with mock.patch('instack_undercloud.undercloud.open',
                        return_value=fake_hosts, create=True):
            undercloud._check_hostname()

    @mock.patch('instack_undercloud.undercloud._run_command')
    def test_static_transient_mismatch(self, mock_run_command):
        mock_run_command.side_effect = ['test-hostname', 'other-hostname']
        self.useFixture(fixtures.EnvironmentVariable('HOSTNAME',
                                                     'test-hostname'))
        fake_hosts = io.StringIO(u'127.0.0.1 test-hostname\n')
        with mock.patch('instack_undercloud.undercloud.open',
                        return_value=fake_hosts, create=True):
            self.assertRaises(RuntimeError, undercloud._check_hostname)

    @mock.patch('instack_undercloud.undercloud._run_command')
    def test_missing_entry(self, mock_run_command):
        mock_run_command.side_effect = ['test-hostname', 'test-hostname']
        self.useFixture(fixtures.EnvironmentVariable('HOSTNAME',
                                                     'test-hostname'))
        fake_hosts = io.StringIO(u'127.0.0.1 other-hostname\n')
        with mock.patch('instack_undercloud.undercloud.open',
                        return_value=fake_hosts, create=True):
            self.assertRaises(RuntimeError, undercloud._check_hostname)

    @mock.patch('instack_undercloud.undercloud._run_command')
    def test_no_substring_match(self, mock_run_command):
        mock_run_command.side_effect = ['test-hostname', 'test-hostname']
        self.useFixture(fixtures.EnvironmentVariable('HOSTNAME',
                                                     'test-hostname'))
        fake_hosts = io.StringIO(u'127.0.0.1 test-hostname-bad\n')
        with mock.patch('instack_undercloud.undercloud.open',
                        return_value=fake_hosts, create=True):
            self.assertRaises(RuntimeError, undercloud._check_hostname)

    @mock.patch('instack_undercloud.undercloud._run_command')
    def test_commented(self, mock_run_command):
        mock_run_command.side_effect = ['test-hostname', 'test-hostname']
        self.useFixture(fixtures.EnvironmentVariable('HOSTNAME',
                                                     'test-hostname'))
        fake_hosts = io.StringIO(u""" #127.0.0.1 test-hostname\n
                                     127.0.0.1 other-hostname\n""")
        with mock.patch('instack_undercloud.undercloud.open',
                        return_value=fake_hosts, create=True):
            self.assertRaises(RuntimeError, undercloud._check_hostname)


class TestGenerateEnvironment(base.BaseTestCase):
    def setUp(self):
        super(TestGenerateEnvironment, self).setUp()
        # Things that need to always be mocked out, but that the tests
        # don't want to care about.
        self.useFixture(mockpatch.Patch(
            'instack_undercloud.undercloud._write_password_file'))
        self.useFixture(mockpatch.Patch(
            'instack_undercloud.undercloud._load_config'))
        mock_isdir = mockpatch.Patch('os.path.isdir')
        self.useFixture(mock_isdir)
        mock_isdir.mock.return_value = False
        # Some tests do care about this, but they can override the default
        # return value, and then the tests that don't care can ignore it.
        self.mock_distro = mockpatch.Patch('platform.linux_distribution')
        self.useFixture(self.mock_distro)
        self.mock_distro.mock.return_value = [
            'Red Hat Enterprise Linux Server 7.1']

    @mock.patch('socket.gethostname')
    def test_hostname_set(self, mock_gethostname):
        fake_hostname = 'crazy-test-hostname-!@#$%12345'
        mock_gethostname.return_value = fake_hostname
        env = undercloud._generate_environment('.')
        self.assertEqual(fake_hostname, env['HOSTNAME'])

    def test_elements_path_input(self):
        test_path = '/test/elements/path'
        self.useFixture(fixtures.EnvironmentVariable('ELEMENTS_PATH',
                                                     test_path))
        env = undercloud._generate_environment('.')
        self.assertEqual(test_path, env['ELEMENTS_PATH'])

    def test_default_elements_path(self):
        env = undercloud._generate_environment('.')
        test_path = ('%s:%s:/usr/share/tripleo-image-elements:'
                     '/usr/share/diskimage-builder/elements' %
                     (os.path.join(os.getcwd(), 'tripleo-puppet-elements',
                                   'elements'),
                      './elements'))
        self.assertEqual(test_path, env['ELEMENTS_PATH'])

    def test_rhel7_distro(self):
        self.useFixture(fixtures.EnvironmentVariable('NODE_DIST', None))
        env = undercloud._generate_environment('.')
        self.assertEqual('rhel7', env['NODE_DIST'])
        self.assertEqual('./json-files/rhel-7-undercloud-packages.json',
                         env['JSONFILE'])
        self.assertEqual('disable', env['REG_METHOD'])
        self.assertEqual('1', env['REG_HALT_UNREGISTER'])

    def test_centos7_distro(self):
        self.useFixture(fixtures.EnvironmentVariable('NODE_DIST', None))
        self.mock_distro.mock.return_value = ['CentOS Linux release 7.1']
        env = undercloud._generate_environment('.')
        self.assertEqual('centos7', env['NODE_DIST'])
        self.assertEqual('./json-files/centos-7-undercloud-packages.json',
                         env['JSONFILE'])

    def test_fedora_distro(self):
        self.useFixture(fixtures.EnvironmentVariable('NODE_DIST', None))
        self.mock_distro.mock.return_value = ['Fedora Infinity + 1']
        self.assertRaises(RuntimeError, undercloud._generate_environment, '.')

    def test_other_distro(self):
        self.useFixture(fixtures.EnvironmentVariable('NODE_DIST', None))
        self.mock_distro.mock.return_value = ['Gentoo']
        self.assertRaises(RuntimeError, undercloud._generate_environment, '.')

    def test_opts_in_env(self):
        env = undercloud._generate_environment('.')
        # Just spot check, we don't want to replicate the entire opt list here
        self.assertEqual(env['DEPLOYMENT_MODE'], 'poc')
        self.assertEqual(env['DISCOVERY_RUNBENCH'], '0')
        self.assertEqual('192.0.2.1/24', env['PUBLIC_INTERFACE_IP'])
        self.assertEqual('192.0.2.1', env['LOCAL_IP'])

    def test_answers_file_support(self):
        with open(undercloud.PATHS.ANSWERS_PATH, 'w') as f:
            f.write('DEPLOYMENT_MODE=scale\n')
        env = undercloud._generate_environment('.')
        self.assertEqual('scale', env['DEPLOYMENT_MODE'])


class TestWritePasswordFile(base.BaseTestCase):
    def test_normal(self):
        answers_parser = mock.Mock()
        answers_parser.has_option.return_value = False
        instack_env = {}
        undercloud._write_password_file(answers_parser, instack_env)
        test_parser = ConfigParser.ConfigParser()
        test_parser.read(undercloud.PATHS.PASSWORD_PATH)
        self.assertTrue(test_parser.has_option('auth',
                                               'undercloud_db_password'))
        self.assertIn('UNDERCLOUD_DB_PASSWORD', instack_env)
        self.assertEqual(32,
                         len(instack_env['UNDERCLOUD_HEAT_ENCRYPTION_KEY']))

    def test_value_set(self):
        answers_parser = mock.Mock()
        answers_parser.has_option.return_value = False
        instack_env = {}
        conf = config_fixture.Config()
        self.useFixture(conf)
        conf.config(undercloud_db_password='test', group='auth')
        undercloud._write_password_file(answers_parser, instack_env)
        test_parser = ConfigParser.ConfigParser()
        test_parser.read(undercloud.PATHS.PASSWORD_PATH)
        self.assertEqual(test_parser.get('auth', 'undercloud_db_password'),
                         'test')
        self.assertEqual(instack_env['UNDERCLOUD_DB_PASSWORD'], 'test')

    def test_answers(self):
        answers_parser = ConfigParser.ConfigParser()
        fake_answers = StringIO.StringIO()
        fake_answers.write('[answers]\nUNDERCLOUD_DB_PASSWORD=foo\n')
        fake_answers.seek(0)
        answers_parser.readfp(fake_answers)
        instack_env = {}
        undercloud._write_password_file(answers_parser, instack_env)
        test_parser = ConfigParser.ConfigParser()
        test_parser.read(undercloud.PATHS.PASSWORD_PATH)
        self.assertEqual(test_parser.get('auth', 'undercloud_db_password'),
                         'foo')
        self.assertEqual(instack_env['UNDERCLOUD_DB_PASSWORD'], 'foo')


class TestRunCommand(base.BaseTestCase):
    def test_run_command(self):
        output = undercloud._run_command(['echo', 'foo'])
        self.assertEqual('foo\n', output)

    def test_run_live_command(self):
        undercloud._run_live_command(['echo', 'bar'])
        self.assertIn('bar\n', self.logger.output)

    @mock.patch('subprocess.check_output')
    def test_run_command_fails(self, mock_check_output):
        fake_exc = subprocess.CalledProcessError(1, 'nothing', 'fake failure')
        mock_check_output.side_effect = fake_exc
        self.assertRaises(subprocess.CalledProcessError,
                          undercloud._run_command, ['nothing'])
        self.assertIn('nothing failed', self.logger.output)
        self.assertIn('fake failure', self.logger.output)

    @mock.patch('subprocess.check_output')
    def test_run_command_fails_with_name(self, mock_check_output):
        fake_exc = subprocess.CalledProcessError(1, 'nothing', 'fake failure')
        mock_check_output.side_effect = fake_exc
        self.assertRaises(subprocess.CalledProcessError,
                          undercloud._run_command, ['nothing'],
                          name='fake_name')
        self.assertIn('fake_name failed', self.logger.output)
        self.assertIn('fake failure', self.logger.output)

    def test_run_live_command_fails(self):
        exc = self.assertRaises(RuntimeError, undercloud._run_live_command,
                                ['ls', '/nonexistent/path'])
        self.assertIn('ls failed', str(exc))
        self.assertIn('ls', self.logger.output)

    def test_run_live_command_fails_name(self):
        exc = self.assertRaises(RuntimeError, undercloud._run_live_command,
                                ['ls', '/nonexistent/path'],
                                name='fake_name')
        self.assertIn('fake_name failed', str(exc))

    def test_run_command_env(self):
        env = {'FOO': 'foo'}
        output = undercloud._run_command(['env'], env)
        self.assertIn('FOO=foo', output)

    def test_run_live_command_env(self):
        env = {'BAR': 'bar'}
        undercloud._run_live_command(['env'], env)
        self.assertIn('BAR=bar', self.logger.output)


class TestRunTools(base.BaseTestCase):
    @mock.patch('instack_undercloud.undercloud._run_live_command')
    def test_run_instack(self, mock_run):
        instack_env = {'ELEMENTS_PATH': '.', 'JSONFILE': 'file.json'}
        args = ['sudo', '-E', 'instack', '-p', '.', '-j', 'file.json']
        undercloud._run_instack(instack_env)
        mock_run.assert_called_with(args, instack_env, 'instack')

    @mock.patch('instack_undercloud.undercloud._run_live_command')
    def test_run_os_refresh_config(self, mock_run):
        instack_env = {}
        args = ['sudo', 'os-refresh-config']
        undercloud._run_orc(instack_env)
        mock_run.assert_called_with(args, instack_env, 'os-refresh-config')


@mock.patch('instack_undercloud.undercloud._run_command')
class TestConfigureSshKeys(base.BaseTestCase):
    def test_ensure_user_identity(self, mock_run):
        id_path = os.path.expanduser('~/.ssh/id_rsa')
        undercloud._ensure_user_identity(id_path)
        mock_run.assert_called_with(['ssh-keygen', '-t', 'rsa', '-N', '',
                                    '-f', id_path])

    def _create_test_id(self):
        id_path = os.path.expanduser('~/.ssh/id_rsa')
        os.makedirs(os.path.expanduser('~/.ssh'))
        with open(id_path, 'w') as id_rsa:
            id_rsa.write('test private\n')
        with open(id_path + '.pub', 'w') as id_pub:
            id_pub.write('test public\n')
        return id_path

    def test_ensure_user_identity_exists(self, mock_run):
        id_path = self._create_test_id()
        undercloud._ensure_user_identity(id_path)
        self.assertFalse(mock_run.called)

    def _test_configure_ssh_keys(self, mock_eui, mock_extract, mock_client,
                                 mock_run, exists=True):
        id_path = self._create_test_id()
        mock_run.side_effect = [None, None, '3nigma']
        mock_extract.side_effect = ['aturing', 'http://bletchley:5000/v2.0',
                                    'hut8']
        mock_client_instance = mock.Mock()
        mock_client.return_value = mock_client_instance
        if not exists:
            get = mock_client_instance.keypairs.get
            get.side_effect = exceptions.NotFound('test')
        undercloud._configure_ssh_keys()
        mock_eui.assert_called_with(id_path)
        mock_client.assert_called_with(2, 'aturing', '3nigma', 'hut8',
                                       'http://bletchley:5000/v2.0')
        mock_client_instance.keypairs.get.assert_called_with('default')
        if not exists:
            mock_client_instance.keypairs.create.assert_called_with(
                'default', 'test public')

    @mock.patch('novaclient.client.Client', autospec=True)
    @mock.patch('instack_undercloud.undercloud._extract_from_stackrc')
    @mock.patch('instack_undercloud.undercloud._ensure_user_identity')
    def test_configure_ssh_keys_exists(self, mock_eui, mock_extract,
                                       mock_client, mock_run):
        self._test_configure_ssh_keys(mock_eui, mock_extract, mock_client,
                                      mock_run)

    @mock.patch('novaclient.client.Client', autospec=True)
    @mock.patch('instack_undercloud.undercloud._extract_from_stackrc')
    @mock.patch('instack_undercloud.undercloud._ensure_user_identity')
    def test_configure_ssh_keys_missing(self, mock_eui, mock_extract,
                                        mock_client, mock_run):
        self._test_configure_ssh_keys(mock_eui, mock_extract, mock_client,
                                      mock_run, False)
