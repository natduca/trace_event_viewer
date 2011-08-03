# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import tempfile
import os
import shlex
import subprocess
import unittest
import frontend_resources
from frontend_daemon_host import FrontendDaemonHost

class FrontendDaemonHostTest(unittest.TestCase):
  def path_to(self, subpath):
    return os.path.join(self.test_data_dir, subpath)

  def system(self, cmd):
    return self.system2(cmd)[0]

  def system2(self, cmd):
    if isinstance(cmd,basestring):
      args = shlex.split(cmd)
    else:
      args = cmd
    proc = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = proc.communicate()[0]
    return (proc.returncode, output)

  def rm_rf(self, dirname):
    assert os.path.exists(dirname)
    self.system('rm -rf -- %s' % dirname)

  def write1(self, file):
    f = open(os.path.join(self.test_data_dir, file), 'w')
    f.write('1\n')
    f.close()

  def setUp(self):
    self.host = None
    self.test_data_dir = os.path.realpath(os.path.join(tempfile.gettempdir(), 'frontend_daemon_host_test'))
    if os.path.exists(self.test_data_dir):
      self.rm_rf(self.test_data_dir)
    os.makedirs(self.test_data_dir)
    self.write1('index.html')
    self.host = FrontendDaemonHost(12345, {"/" : self.test_data_dir})

  def test_host(self):
    x = self.host.urlread("/index.html")
    self.assertEquals('1\n', x)

  def tearDown(self):
    if self.host:
      self.host.close()
