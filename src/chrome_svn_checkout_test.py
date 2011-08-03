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
import unittest
import deps
from chrome_svn_checkout import ChromeSVNCheckout

class ChromeSVNCheckoutTest(unittest.TestCase):
  def test_download(self):
    fe = ChromeSVNCheckout(deps.CHROME_SVN_BASE, deps.CHROME_SVN_REV)
    rev = fe.svn_getrev(fe.shared_path)
    if type(deps.CHROME_SVN_REV) == int:
      self.assertEquals(rev, deps.CHROME_SVN_REV)
    fe.close()
