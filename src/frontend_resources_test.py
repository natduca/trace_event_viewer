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
import chrome_svn_checkout
import deps
import unittest

from frontend_resources import FrontendResources

class FrontendResourcesTest(unittest.TestCase):
  def test_fe_with_dir(self):
    chrome_checkout = chrome_svn_checkout.ChromeSVNCheckout(deps.CHROME_SVN_BASE, deps.CHROME_SVN_REV)
    self.fe = FrontendResources(chrome_checkout.data_dir)
    assert len(self.fe.dir_mappings) != 0

  def test_fe_with_checkout(self):
    self.fe = FrontendResources()
    assert len(self.fe.dir_mappings) != 0

  def cleanUp(self):
    if self.fe:
      self.fe.close()
