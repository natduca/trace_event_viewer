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

  function ChromeStorageToLocalStorageAdapter() {
    this.items_ = {}
  }
  ChromeStorageToLocalStorageAdapter.prototype = {
    __proto__: Object.prototype,

    init: function(init_done_callback) {
      this.flushPending_ = false;

      chrome.storage.local.get(null, function(items) {
        this.items_ = items;
        init_done_callback();
      }.bind(this));
    },
    setNeedsFlush_: function() {
      if (this.flushPending_)
        return;
      this.flushPending_ = true;
      window.setTimeout(this.flush_.bind(this), 250);
    },

    flush_: function() {
      chrome.storage.local.set(this.items_, function() {
        if (chrome.runtime.lastError)
          throw new Error(chrome.runtime.lastError);
        this.flushPending_ = false;
      }.bind(this));
    },

    getItem: function(key) {
      return this.items_[key];
    },

    setItem: function(key, value) {
      this.items_[key] = value;
      this.setNeedsFlush_();
    },

    key: function(i) {
      return Object.keys(this.items_).sort()[i];
    },

    get length() {
      return Object.keys(this.items_).length;
    }
  };

  chromeapp.addEventListener('launch', init);
  chrome.app.window.current().onClosed.addListener(onClosed);
  chrome.app.window.current().focus();

  var timelineViewEl = undefined;

  function init(launch_event) {
    var storage = new ChromeStorageToLocalStorageAdapter();
    console.log('init');
    storage.init(init2.bind(this, launch_event, storage));
  }

  function init2(launch_event, storage) {
    console.log('init2');
    base.Settings.setAlternativeStorageInstance(storage);

    timelineViewEl = $('#timeline-view')
    window.g_timelineView = timelineViewEl;
    tracing.TimelineView.decorate(timelineViewEl);

    var num_args = launch_event.args[0]
    beginLoad(num_args);
  }

  function beginLoad(num_args) {
    console.log('beginLoad');
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

      var model = new tracing.TimelineModel();
      model.importTraces(traces);
      timelineViewEl.model = model;
    }
  }

  function onClosed() {
    chromeapp.exit(1);
  }

})();
