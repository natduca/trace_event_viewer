/* Copyright (c) 2012 The Chromium Authors. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the LICENSE file.
 */
'use strict';

(function() {
  function $(sel) {
    return document.querySelector(sel);
  }

  function assert(bool) {
    if (bool)
      return;
    throw new Error("Expected true");
  }

  chromeapp.addEventListener('launch', init);

  function init(launch_event) {
    var num_args = launch_event.args[0]


    chrome.app.window.current().onClosed.addListener(onClosed);
    chrome.app.window.current().focus();

    load(num_args);
  }

  function load(num_args) {
    // Load all the assets.
    var remaining = num_args
    var hadErrors = false;
    var traces = [];
    for (var i = 0; i < num_args; i++) {
      traces.push(undefined);
      chromeapp.sendEvent('load_nth_arg',
                          {index: i},
                          traceLoaded, traceDidntLoad);
    }

    function traceLoaded(args) {
      var index = args.index;
      traces[index] = args.trace;
      remaining--;
      maybeFinishLoad();
    }

    function traceDidntLoad() {
      remaining--;
      hadErrors = true;
      maybeFinishLoad();
    }

    function maybeFinishLoad() {
      if (remaining != 0)
        return;

      if (hadErrors) {
        chromeapp.print('Had errors during loading. Cannot continue.');
        chromeapp.exit(1);
      }

      var doneEl = document.createElement('div');
      doneEl.textContent = 'done loading';
      document.body.insertBefore(doneEl, document.body.firstChild);
    }
  }

  function onClosed() {
    chromeapp.exit(1);
  }

})();
