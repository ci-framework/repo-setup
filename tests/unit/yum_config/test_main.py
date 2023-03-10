#   Copyright 2021 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import ddt
import sys
import unittest
from unittest import mock

from . import fakes
from . import mock_modules  # noqa: F401
import repo_setup.yum_config.__main__ as main
import repo_setup.yum_config.compose_repos as repos
import repo_setup.yum_config.constants as const
import repo_setup.yum_config.dnf_manager as dnf_mgr
import repo_setup.yum_config.utils as utils
import repo_setup.yum_config.yum_config as yum_cfg


class TestYumConfigBase(unittest.TestCase):
    """Base test class for yum config module."""

    def mock_object(self, obj, attr, new_attr=None):
        if not new_attr:
            new_attr = mock.Mock()

        patcher = mock.patch.object(obj, attr, new_attr)
        patcher.start()
        # stop patcher at the end of the test
        self.addCleanup(patcher.stop)

        return new_attr


@ddt.ddt
class TestYumConfigMain(TestYumConfigBase):
    """Test class for main method operations."""
    def setUp(self):
        super(TestYumConfigMain, self).setUp()
        self.mock_object(utils, 'get_distro_info',
                         mock.Mock(return_value=("centos", "8", None)))

    def test_main_repo(self):
        sys.argv[1:] = ['repo', '--name', 'fake_repo', '--enable',
                        '--set-opts', 'key1=value1', 'key2=value2',
                        '--config-file-path', fakes.FAKE_FILE_PATH,
                        '--down-url', fakes.FAKE_REPO_DOWN_URL]

        yum_repo_obj = mock.Mock()
        mock_update_section = self.mock_object(yum_repo_obj,
                                               'add_or_update_section')
        mock_yum_repo_obj = self.mock_object(
            yum_cfg, 'YumRepoConfig',
            mock.Mock(return_value=yum_repo_obj))

        main.main()
        expected_dict = {'key1': 'value1', 'key2': 'value2'}

        mock_yum_repo_obj.assert_called_once_with(dir_path=const.YUM_REPO_DIR,
                                                  environment_file=None)
        mock_update_section.assert_called_once_with(
            'fake_repo', set_dict=expected_dict,
            file_path=fakes.FAKE_FILE_PATH, enabled=True,
            from_url=fakes.FAKE_REPO_DOWN_URL)

    def test_main_repo_from_url(self):
        sys.argv[1:] = ['repo', '--enable',
                        '--set-opts', 'key1=value1', 'key2=value2',
                        '--config-file-path', fakes.FAKE_FILE_PATH,
                        '--down-url', fakes.FAKE_REPO_DOWN_URL]

        yum_repo_obj = mock.Mock()
        mock_update_all_sections = self.mock_object(
            yum_repo_obj, 'add_or_update_all_sections_from_url')
        mock_yum_repo_obj = self.mock_object(
            yum_cfg, 'YumRepoConfig',
            mock.Mock(return_value=yum_repo_obj))

        main.main()
        expected_dict = {'key1': 'value1', 'key2': 'value2'}

        mock_yum_repo_obj.assert_called_once_with(dir_path=const.YUM_REPO_DIR,
                                                  environment_file=None)
        mock_update_all_sections.assert_called_once_with(
            fakes.FAKE_REPO_DOWN_URL, file_path=fakes.FAKE_FILE_PATH,
            set_dict=expected_dict, enabled=True)

    @ddt.data('enable', 'disable', 'reset', 'install', 'remove')
    def test_main_module(self, operation):
        sys.argv[1:] = ['module', operation, 'fake_module', '--stream',
                        'fake_stream', '--profile', 'fake_profile']

        mock_dnf_mod = mock.Mock()
        mock_op = self.mock_object(mock_dnf_mod, operation + '_module')
        mock_dnf_mod_obj = self.mock_object(
            dnf_mgr, 'DnfModuleManager',
            mock.Mock(return_value=mock_dnf_mod))

        main.main()

        mock_dnf_mod_obj.assert_called_once()
        mock_op.assert_called_once_with(
            'fake_module', stream='fake_stream', profile='fake_profile')

    def test_main_global_conf(self):
        sys.argv[1:] = ['global', '--set-opts', 'key1=value1', 'key2=value2']
        yum_global_obj = mock.Mock()
        mock_update_section = self.mock_object(
            yum_global_obj, 'update_section')
        mock_yum_global_obj = self.mock_object(
            yum_cfg, 'YumGlobalConfig',
            mock.Mock(return_value=yum_global_obj))

        main.main()
        expected_dict = {'key1': 'value1', 'key2': 'value2'}

        mock_yum_global_obj.assert_called_once_with(file_path=None,
                                                    environment_file=None)
        mock_update_section.assert_called_once_with('main', expected_dict)

    def test_main_no_command(self):
        sys.argv[1:] = []
        with self.assertRaises(SystemExit) as command:
            main.main()

        self.assertEqual(2, command.exception.code)

    @ddt.data('repo')
    def test_main_repo_mod_without_name(self, command):
        sys.argv[1:] = [command, '--set-opts', 'key1=value1',
                        '--config-dir-path', '/tmp']

        with self.assertRaises(SystemExit) as command:
            main.main()

        self.assertEqual(2, command.exception.code)

    def test_main_repo_without_name_and_url(self):
        sys.argv[1:] = ['repo', '--enable',
                        '--set-opts', 'key1=value1', 'key2=value2',
                        '--config-file-path', fakes.FAKE_FILE_PATH,
                        '--config-dir-path', '/tmp']

        with self.assertRaises(SystemExit) as command:
            main.main()

        self.assertEqual(2, command.exception.code)

    @ddt.data('key:value', 'value', 'key value')
    def test_main_invalid_options_format(self, option):
        sys.argv[1:] = ['global', '--set-opts', option]

        with self.assertRaises(SystemExit) as command:
            main.main()

        self.assertEqual(2, command.exception.code)

    def test_main_enable_compose_repos(self):
        sys.argv[1:] = [
            'enable-compose-repos', '--compose-url', fakes.FAKE_COMPOSE_URL,
            '--release', const.COMPOSE_REPOS_RELEASES[0],
            '--variants', 'fake_variant',
            '--disable-repos', fakes.FAKE_REPO_PATH,
            '--arch', const.COMPOSE_REPOS_SUPPORTED_ARCHS[0],
        ]
        repos_obj = mock.Mock()
        mock_yum_global_obj = self.mock_object(
            repos, 'YumComposeRepoConfig',
            mock.Mock(return_value=repos_obj))
        mock_enable_composes = self.mock_object(
            repos_obj, 'enable_compose_repos')
        mock_update_all = self.mock_object(
            repos_obj, 'update_all_sections')
        self.mock_object(yum_cfg, 'validated_file_path',
                         mock.Mock(return_value=True))

        main.main()

        mock_yum_global_obj.assert_called_once_with(
            fakes.FAKE_COMPOSE_URL,
            const.COMPOSE_REPOS_RELEASES[0],
            dir_path=const.YUM_REPO_DIR,
            arch=const.COMPOSE_REPOS_SUPPORTED_ARCHS[0],
            environment_file=None)
        mock_enable_composes.assert_called_once_with(
            variants=['fake_variant'], override_repos=False)
        mock_update_all.assert_called_once_with(
            fakes.FAKE_REPO_PATH, enabled=False
        )

    def test_main_invalid_release_for_dnf_module(self):
        self.mock_object(utils, 'get_distro_info',
                         mock.Mock(return_value=("centos", "7", None)))
        sys.argv[1:] = ['module', 'enable', 'fake_module']

        with self.assertRaises(SystemExit) as command:
            main.main()

        self.assertEqual(2, command.exception.code)
