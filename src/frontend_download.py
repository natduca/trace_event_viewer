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
import tempfile
import re
import shlex
import subprocess
import urllib


class FrontendDownload(object):
  def __init__(self, base_url, rev, persist = True):
    self.persist = persist
    self.base_url = base_url
    # create a directory hierarchy to do tests in
    self.data_dir = os.path.realpath(os.path.join(tempfile.gettempdir(), 'trace_event_frontend'))
    if not persist:
      if os.path.exists(self.data_dir):
        self.rm_rf(self.data_dir)
    
    shared_url = self.url_to('chrome/browser/resources/shared/')
    self.shared_path = self.path_to('shared')
    gpu_internals_url = self.url_to('chrome/browser/resources/gpu_internals/')
    self.gpu_internals_path = self.path_to('gpu_internals')

    self.svn_update(shared_url, rev, self.shared_path)
    self.svn_update(gpu_internals_url, rev, self.gpu_internals_path)

    shim_dir = os.path.join(os.path.dirname(__file__), "../shim")
    for ent in os.listdir(shim_dir):
      full_ent = os.path.join(shim_dir, ent)
      assert os.path.exists(full_ent)
      self.cp(full_ent, self.data_dir)

    es5shim_dir = os.path.join(os.path.dirname(__file__), "../third_party/es5-shim/")
    assert os.path.exists(es5shim_dir)
    self.cp(os.path.join(es5shim_dir, "es5-shim.js"), self.data_dir)
    
  def verify_checkout(self):
    """Makes sure that key files are present."""
    required = [
      'shared/js/cr.js',
      'gpu_internals/timeline.js'
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
        if self.svn_getrev(dest) == rev:
          logging.debug('copy of %s is up-to-date')
          return
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
    logging.debug('checking out %s at %s' % (url, rev))
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
    if isinstance(cmd,str):
      args = shlex.split(cmd)
    else:
      args = cmd
    proc = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = proc.communicate()[0]
    return (proc.returncode, output)

  def url_to(self, subpath):
    return urllib.basejoin(self.base_url, subpath)

  def path_to(self, subpath):
    return os.path.join(self.data_dir, subpath)

  def cp(self, src, dst):
    ret,msg = self.system2('/bin/cp -f %s %s' % (src, self.path_to(dst)))
    if ret != 0:
      print msg
    assert ret == 0

  def write1(self, dirname):
    f = open(os.path.join(self.data_dir, dirname), 'w')
    f.write('1\n')
    f.close()

  def close(self):
    if not self.persist and os.path.exists(self.data_dir):
      self.rm_rf(self.data_dir)
    self.data_dir = None

  def rm_rf(self, dirname):
    assert os.path.exists(dirname)
    self.system('rm -rf -- %s' % dirname)

