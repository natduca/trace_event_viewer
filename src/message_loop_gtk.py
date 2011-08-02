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
import glib
import gtk
import sys

_is_main_loop_running = False
_current_main_loop_instance = 0
_raise_exception_after_quit = False

def init_main_loop():
  pass

def post_task(cb, *args):
  init_main_loop()
  main_loop_instance_at_post = _current_main_loop_instance
  def on_run():
    # timeouts that were enqueued when the mainloop exited should not run
    if _current_main_loop_instance == main_loop_instance_at_post:
      cb(*args)
  glib.timeout_add(0, on_run)

def post_delayed_task(cb, delay, *args):
  init_main_loop()
  main_loop_instance_at_post = _current_main_loop_instance
  def on_run():
    # timeouts that were enqueued when the mainloop exited should not run
    if _current_main_loop_instance == main_loop_instance_at_post:
      cb(*args)
  timeout_ms = int(delay * 1000)
  glib.timeout_add(timeout_ms, on_run)

def _on_exception_while_in_main_loop(type, value, tb):
  message = 'Uncaught exception:\n'
  message += ''.join(traceback.format_exception(type, value, tb))
  print message
  quit_main_loop()

def is_main_loop_running():
  return _is_main_loop_running

def run_main_loop():
  global _current_main_loop_instance
  global _is_main_loop_running
  init_main_loop()

  try:
    _is_main_loop_running = True
    gtk.main()
  finally:
    _is_main_loop_running = False
    _current_main_loop_instance += 1

  global _raise_exception_after_quit
  if _raise_exception_after_quit:
    _raise_exception_after_quit = False
    raise Exception("An exception occured while running main loop.")


def quit_main_loop(quit_with_exception):
  global _raise_exception_after_quit
  if quit_with_exception:
    _raise_exception_after_quit = True
  def do_cleanup():
    for w in gtk.window_list_toplevels():
      w.destroy()
    post_task(do_quit)
  def do_quit():
    gtk.main_quit()
  post_task(do_cleanup)
