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
#
#
from __future__ import absolute_import, division, print_function


__metaclass__ = type


class Base(Exception):
    """Base Exception class."""


class YumConfigNotFound(Base):
    """A configuration file was not found in the provided file path."""

    def __init__(self, error_msg):
        super(YumConfigNotFound, self).__init__(error_msg)


class YumConfigPermissionDenied(Base):
    """THh user has no permission to modify the configuration file."""

    def __init__(self, error_msg):
        super(YumConfigPermissionDenied, self).__init__(error_msg)


class YumConfigFileParseError(Base):
    """Encountered an error while parsing the configuration file."""

    def __init__(self, error_msg):
        super(YumConfigFileParseError, self).__init__(error_msg)


class YumConfigInvalidSection(Base):
    """The configuration file does not have the requested section.

    This exception is raised when the expected section in the configuration
    file does not exist and the class will not create a new one.
    """

    def __init__(self, error_msg):
        super(YumConfigInvalidSection, self).__init__(error_msg)


class YumConfigInvalidOption(Base):
    """One or more options are not valid for this configuration file."""

    def __init__(self, error_msg):
        super(YumConfigInvalidOption, self).__init__(error_msg)


class YumConfigComposeError(Base):
    """An error occurred while configuring CentOS compose repos."""

    def __init__(self, error_msg):
        super(YumConfigComposeError, self).__init__(error_msg)


class YumConfigUrlError(Base):
    """An error occurred while fetching repo from the url."""

    def __init__(self, error_msg):
        super(YumConfigUrlError, self).__init__(error_msg)
