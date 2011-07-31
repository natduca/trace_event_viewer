// Copyright 2011 Google Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

if (!window["chrome"]) {
  window.chrome = {
    /** Called by gpu_internals/ code to interact with the world
     * outside of javascript. This shim forwards these messages
     * via frontend_daemon.py to chrome_handlers.py
     * @param {string} msg The message being sent to chrome_handlers.
     * @param {Array=} opt_args An array of optional arguments to send to the handler.
     */
    __send: function(msg, opt_args) {
    }
  };
}
