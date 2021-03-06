#!/usr/bin/python
#
# Copyright (c) 2013 NORDUnet A/S
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#     2. Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.
#     3. Neither the name of the NORDUnet nor the names of its
#        contributors may be used to endorse or promote products derived
#        from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Author : Fredrik Thulin <fredrik@thulin.net>
#

"""
Test password hashing.
"""

import os
import sys
import unittest
import pkg_resources
from pprint import pprint, pformat

import ndnkdf
import vccs_auth

from common import FakeCredentialStore

from vccs_auth.vccs_authbackend import VCCSLogger


class TestPasswordHashing(unittest.TestCase):

    def setUp(self):
        debug = False
        datadir = pkg_resources.resource_filename(__name__, 'data')
        self.config_file = os.path.join(datadir, 'test_config.ini')
        self.config = vccs_auth.config.VCCSAuthConfig(self.config_file, debug)
        self.credstore = FakeCredentialStore()
        self.kdf = ndnkdf.NDNKDF(self.config.nettle_path)
        self.keys = {0x2000: str('2000' * 16).decode('hex'),
                     }
        self.hasher = vccs_auth.hasher.VCCSSoftHasher(self.keys, vccs_auth.hasher.NoOpLock())
        self.logger = VCCSLogger('test_authbackend', syslog=False)

    def test_password_hash_1(self):
        """
        Test a password hashing operation.
        """
        # this request matches the examples/example-json output
        # salt matching examples/example-json
        # vccs_client.VCCSPasswordFactor('plaintext', credential_id=4711, salt='$2a$08$Ahy51oCM6Vg6d.1ScOPxse').to_dict()
        req = {'credential_id': 4711,
               'H1': '227ALNnVn0y1IuhmbsjmlsCHDLIJ5xq',
               'type': 'password'}
        factor = vccs_auth.password.from_factor(req, 'auth', 'ft@example.net', self.credstore, self.config)
        self.assertTrue(factor.authenticate(self.hasher, self.kdf, self.logger))
