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
import browser
import logging
import message_loop
import sys
import gtk
import webkit

class BrowserGtk(gtk.Window, browser.BrowserBase):
  def __init__(self):
    message_loop.init_main_loop()
    gtk.Window.__init__(self)
    browser.BrowserBase.__init__(self)

    self.set_size_request(browser.default_size[0], browser.default_size[1])

    vbox = gtk.VBox()
    vbox.show()
    self._webview  = webkit.WebView()
    self._webview.show()

    self._debug_ctrl = gtk.Entry()
    self._debug_ctrl.connect('key_press_event', self._on_debug_keypress)
    if browser.debug_mode:
      self._debug_ctrl.show()

    # OK, this bit of magic is because the gtk webkit's execute_script
    # method does not actually return the script value. But, calling execute_script
    # does synchronously trigger a title-changed callback. So we make all
    # execute_script calls change the title to the result of the script,
    # then trap the title-changed callback, and return the last-seen title.
    # The title version number is a sanity check we use to ensure that the title
    # did actually change during the execute script routine, and also provides us
    # insulation in case the page itself changes the title.
    self._title = None
    self._title_version = 0
    self._webview_connected_signals = [
        self._webview.connect('title-changed', self.on_title_changed),
        self._webview.connect('console-message', self.on_console_message),
        self._webview.connect('load-finished', self.on_load_finished),
        ]
    self._loaded = False

    vbox.pack_start(self._webview, True, True)
    vbox.pack_start(self._debug_ctrl, False, True)
    self.add(vbox)


  def _on_debug_keypress(self, entry, event):
    keyname = gtk.gdk.keyval_name(event.keyval)
    if keyname == 'Return':
      cmd = self._debug_ctrl.get_text()
      self._debug_ctrl.set_text("")
      if cmd.startswith("*"):
        try:
          res = eval(cmd[1:],None,{
              "v": self._webview,
              "w": self,
              "message_loop": message_loop
              })
        except:
          import traceback
          res = traceback.format_exc()
        print "PY> %s\n%s" % (cmd, res)

      else:
        res = self.run_javascript(cmd)
        print "> %s\n%s" % (cmd, res)


  def load_url(self, url):
    if (self.flags() & gtk.REALIZED) == 0:
      message_loop.post_delayed_task(self.load_url, 0.5, url)
    else:
      logging.debug("Load begin of %s" % url);
      self._webview.load_uri(url)

  def on_load_finished(self, *args):
    logging.debug("Load finished");
    self._loaded = True

  def run_javascript(self, script, require_loaded = True):
    if (self.flags() & gtk.REALIZED) == 0:
      return None
    if require_loaded and self._loaded == False:
      return None
    # this wraps the script in an eval, then a try-catch, and then tostrings the result in a null/undef-safe way
    # when you dont do this, it takes down WxPython completely.
    script = script.replace('"', '\\"')
    # reset the title first, then run the script inside an eval, inside a catch, inside a function.
    cmd = """document.title = 'asdfasdfasdfasdfasdf'; document.title = (function() { var t = (((function() { try { return eval("%s;"); } catch(ex) { return ex; } })())); if (t === null) return 'null'; if (t === undefined) return 'undefined'; return t.toString(); })();""" % script
    prev_title_version = self._title_version
    self._webview.execute_script(cmd) # this will change the title twice
    if self._title_version != prev_title_version + 2:
      logging.warn('run_javascript failed for %s', script)
      return None
    return self._title

  def on_title_changed(self, widget, frame, title):
    self._title = title
    self._title_version += 1

  def on_console_message(self, a, b, c, d):
    logging.debug("console: %s %s %s %s" % (a, b, c, d))
    return True

  def close(self):
    self.destroy()

  def destroy(self):
    for i in self._webview_connected_signals:
      self._webview.disconnect(i)
    self._webview.get_parent().remove(self._webview)
    self._webview.destroy()
    gtk.Window.destroy(self)

  def show(self):
    gtk.Window.show(self)

"""Alias for BrowserWx"""
Browser = BrowserGtk
