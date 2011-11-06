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
  function _ChromeShim() {
    this._pending_sends = [];
    document.addEventListener('DOMContentLoaded', function() {
            this.send('__chrome_shim_loaded');
        }.bind(this));
  }

  _ChromeShim.prototype = {

    __proto__: Object.prototype,

    /** Called by tracing/ code to interact with the world
     * outside of javascript. This shim forwards these messages
     * via frontend_daemon.py to chrome_handlers.py
     * @param {string} msg The message being sent to chrome_handlers.
     * @param {Array=} opt_args An array of optional arguments to send to the handler.
     */
    send: function(msg, opt_args) {
      this._pending_sends.push({msg: msg,
                                args: opt_args ? opt_args : []});
    },

    get_pending_sends: function() {
      ret = JSON.stringify(this._pending_sends);
      this._pending_sends = []
      return ret
    }
  };

  window.chrome = new _ChromeShim();

  if (!window.console)
    window.console = {}

//  if (!window.console.log)
  window.console.log = function() {
    var z = [];
    for (var i = 0; i < arguments.length; ++i)
      z.push(arguments[i].toString());
    chrome.send('console.log', [z.join(" ")]);
  };
}
