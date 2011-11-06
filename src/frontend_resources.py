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
import os
import sys
import tempfile

class FrontendResources():
  def __init__(self, chrome_dir=None):
    if chrome_dir:
      self.chrome_checkout = None
      self.chrome_dir = chrome_dir
    else:
      self.chrome_checkout = chrome_svn_checkout.ChromeSVNCheckout(deps.CHROME_SVN_BASE, deps.CHROME_SVN_REV)
      self.chrome_dir = self.chrome_checkout.data_dir

    self.data_dir = tempfile.mkdtemp()

    # make sure we can find es5 shim
    self.es5shim_dir = os.path.join(os.path.dirname(__file__), "../third_party/es5-shim/")
    if not os.path.exists(self.es5shim_dir):
      raise Exception("ES5 shim missing. You probably forgot to do git submodule update --init")
    if not os.path.exists(os.path.join(self.es5shim_dir, 'es5-shim.js')):
      raise Exception("third_party/es5-shim/es5-shim.js is missing. Is that submodule messed up?")

    # make sure we can find index.html/index.js
    self.src_dir = os.path.dirname(sys.modules[__name__].__file__)
    required = [
        'index.js',
        'index.html',
        'chrome_shim.js',
        'webkit_shim.js']
    missing = set(required)
    for ent in os.listdir(self.src_dir):
      if ent in missing:
        missing.remove(ent)
    if len(missing):
      raise Exception("Couldn't find %s in %s", (", ".join(missing), src_dir))

  @property
  def dir_mappings(self):
    return {
        "/src" : self.src_dir,
        "/chrome" : self.chrome_dir,
        "/es5-shim" : self.es5shim_dir,
        "/data": self.data_dir,
        }

  def close(self):
    if self.chrome_checkout:
      self.chrome_checkout.close()
    if self.data_dir:
      for e in os.dir(self.data_dir):
        p = os.path.join(self.data_dir, e)
        os.remove(p)
      os.rmdir(self.data_dir)
