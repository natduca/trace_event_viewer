## Copyright 2011 Google Inc.
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
import deps
import urllib
import urllib2
import unittest

class DepsTest(unittest.TestCase):
  def test_svn_base_on_head(self):
    self.test_svn_base_and_rev(rev='HEAD')

  def test_svn_base_and_rev(self, rev=None):
    if rev == None:
      rev = deps.CHROME_SVN_REV
    if rev == 'HEAD':
      base = deps.CHROME_SVN_BASE
    else:
      base = deps.CHROME_SVN_BASE.replace("/svn/", "/svn/!svn/bc/%s/" % rev)

    self.assertTrue(base.endswith('/'))
    urllib2.urlopen(base).read()
    u1 = urllib.basejoin(base, 'chrome/browser/resources/shared/js/cr.js')
    u2 = urllib.basejoin(base, 'chrome/browser/resources/gpu_internals/timeline.js')
    urllib2.urlopen(u1).read()
    urllib2.urlopen(u2).read()


