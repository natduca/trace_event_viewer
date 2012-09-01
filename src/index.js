// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
var g_timelineView;
(function() {
  function onDOMContentLoaded() {
    g_timelineView = document.querySelector('#view');
    base.ui.decorate(g_timelineView, tracing.TimelineView);
    chrome.send('ready');
  }

  function getAsync(url, cb, err_cb) {
    var req = new XMLHttpRequest();
    req.open('GET', url, true);
    req.onreadystatechange = function(aEvt) {
      if (req.readyState == 4) {
        window.setTimeout(function() {
          if (req.status == 200) {
            cb(req.responseText);
          } else {
            console.log('Failed to load ' + url);
            if (err_cb)
              err_cb(req.status)
          }
        }, 0);
      }
    };
    req.send(null);
  }

  function loadTracesFromURLs(urls) {
    var traces = [];
    var traces_outstanding = urls.length;
    var failure = false;
    var failureMessages = [];
    for (var i = 0; i < urls.length; ++i) {
      (function() {
        var i_ = i;
        getAsync(urls[i_],
                 function(text) {
                   traces[i_] = text;
                   if(--traces_outstanding == 0)
                     finalizeLoad();
                 },
                 function(status) {
                   failure = true;
                   failureMessages.push('Load failed, got status=' + status + ' on ' + urls[i_]);
                   if(--traces_outstanding == 0)
                     finalizeLoad();
                 }
                );
      })();
    }
    function finalizeLoad() {
      if (failure) {
        chrome.send('loadTracesFromURLs_Failed', failureMessages);
        return;
      }
      var ok;
      try {
        ok = loadTraces(traces);
        if (!ok)
          errMsg = "loadTraces failure of some other sort.";
      } catch(err) {
        ok = false;
        errMsg = err;
      }
      if (!ok)
        chrome.send('loadTracesFromURLs_Failed', ["import failed: " + errMsg]);
      else
        chrome.send('loadTracesFromURLs_Done');
    }
  }

  function loadTraces(events) {
    if (g_timelineView == undefined)
      throw Error('timelineview is null');

    var m = new tracing.TimelineModel();
    m.importTraces(events, true)
    g_timelineView.model = m;
    return true;
  }

  function setRefreshRate(hz) {
    timelineView.timeline.viewport.gridStep_ = 1000 / hz;
  }

  window.loadTracesFromURLs = loadTracesFromURLs;
  window.loadTraces = loadTraces;
  window.setRefreshRate = setRefreshRate;
  document.addEventListener('DOMContentLoaded', onDOMContentLoaded);
})();
