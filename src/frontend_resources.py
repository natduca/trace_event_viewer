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
import os
import shutil
import sys
import tempfile

import deps
import trace_viewer_svn_checkout

class FrontendResources():
  def __init__(self, tev_dir=None):
    if tev_dir:
      self.tev_checkout = None
      self.tev_dir = tev_dir
    else:
      self.tev_checkout = trace_viewer_svn_checkout.TraceViewerSVNCheckout(deps.TRACE_VIEWER_SVN_URL, deps.TRACE_VIEWER_SVN_REV)
      self.tev_dir = self.tev_checkout.trace_viewer_checkout_path

    self.data_dir = tempfile.mkdtemp()
    self.trace_viewer_build_dir = tempfile.mkdtemp()
    self.generate_standalone_timeline_view()

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

  def generate_standalone_timeline_view(self):
    try:
      sys.path.append(self.tev_dir)
      import build.generate_standalone_timeline_view as generator
      with open(os.path.join(self.trace_viewer_build_dir,
                             "timeline_view.js"), 'w') as f:
        f.write(generator.generate_js())

      with open(os.path.join(self.trace_viewer_build_dir,
                             "timeline_view.css"), 'w') as f:
        f.write(generator.generate_css())

    finally:
      sys.path.remove(self.tev_dir)

  @property
  def dir_mappings(self):
    return {
        "/src" : self.src_dir,
        "/es5-shim" : self.es5shim_dir,
        "/data": self.data_dir,
        "/trace-viewer": self.tev_dir,
        "/trace-viewer-build": self.trace_viewer_build_dir,
        }

  def close(self):
    if self.tev_checkout:
      self.tev_checkout.close()
    if self.data_dir:
      shutil.rmtree(self.data_dir)
      self.data_dir = None
    if self.trace_viewer_build_dir:
      shutil.rmtree(self.trace_viewer_build_dir)
      self.trace_viewer_build_dir = None
