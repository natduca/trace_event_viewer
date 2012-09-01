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
import logging
import re
import shlex
import subprocess
import sys
import urllib

class TraceViewerSVNCheckout(object):
  def __init__(self, trace_viewer_svn_url, rev, persist = True):
    self.persist = persist
    self.trace_viewer_svn_url = trace_viewer_svn_url

    # Create a directory hierarchy to do tests in.
    trace_dir = os.path.abspath(os.path.join(os.path.dirname(sys.modules[__name__].__file__), '..'))
    assert os.path.exists(trace_dir)

    third_party_dir = os.path.join(trace_dir, 'third_party')
    self.trace_viewer_checkout_path = os.path.join(third_party_dir, 'trace-viewer')
    if not persist:
      if os.path.exists(self.trace_viewer_checkout_path):
        self.rm_rf(self.trace_viewer_checkout_path)

    self.svn_update(trace_viewer_svn_url, rev, self.trace_viewer_checkout_path)

    ok,err = self.verify_checkout()
    if not ok:
      raise Exception, err

  def verify_checkout(self):
    """Makes sure that key files are present."""
    required = [
      'build/generate_standalone_timeline_view.py',
      'src/timeline_view.js'
      ]
    missing = []
    for r in required:
      if not os.path.exists(self.path_to(r)):
        missing.append(r)
    if len(missing):
      return (False, "Missing files: %s" % ", ".join(missing))
    return (True, "OK")

  def svn_update(self, url, rev, dest):
    oldcwd = os.getcwd()
    try:
      if os.path.exists(dest) and os.path.isdir(dest):
        os.chdir(dest)
        # svn_getrev returns -1 if an update might work and
        # -2 if an update is hopeless and a clobber needs to happen.
        cur_rev = self.svn_getrev(dest)
        if cur_rev == rev:
          logging.debug('copy of %s is up-to-date' % url)
          return
        if cur_rev == -1:
          logging.debug('updating copy of %s to %s' % (url, rev))
          ret,msg = self.system2(['svn', 'update', '-r', str(rev)])
          if ret == 0:
            return
          logging.warning(msg)
        logging.debug('  updating falied, clobbering and checking out')
      self.rm_rf(dest)
      self.svn_checkout(url, rev, dest)
    finally:
      os.chdir(oldcwd)

  def svn_checkout(self, url, rev, dest):
    print 'Checking out %s at %s' % (url, rev)
    ret,res = self.system2(['svn', 'checkout', url, '-r', str(rev), dest])
    if ret != 0:
      raise Exception, res

  def svn_getrev(self, dest):
    oldcwd = os.getcwd()
    try:
      if not os.path.exists(dest):
        return -1
      if not os.path.isdir(os.path.join(dest, ".svn")):
        return -1
      os.chdir(dest)

      logging.debug('checking clean at %s' % (dest))
      ret,res = self.system2(['svn', 'status', '.'])
      if res != "":
        logging.debug('tree dirty, no sane revision')
        return -2

      logging.debug('checking rev at %s' % (dest))
      ret,res = self.system2(['svn', 'info', '.'])
      m = re.search("Revision: (\d+)", res)
      if ret == 0 and m:
        return int(m.group(1))
      else:
        return -1
    finally:
      os.chdir(oldcwd)

  def system(self, cmd):
    return self.system2(cmd)[0]

  def system2(self, cmd):
    if isinstance(cmd,basestring):
      args = shlex.split(cmd)
    else:
      args = cmd
    proc = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE)
    output = proc.communicate()[0]
    return (proc.returncode, output)

  def path_to(self, subpath):
    return os.path.join(self.trace_viewer_checkout_path, subpath)

  def close(self):
    if not self.persist and os.path.exists(self.trace_viewer_checkout_path):
      self.rm_rf(self.trace_viewer_checkout_path)
    self.trace_viewer_checkout_path = None

  def rm_rf(self, dirname):
    if not os.path.exists(dirname):
      return
    self.system('rm -rf -- %s' % dirname)
