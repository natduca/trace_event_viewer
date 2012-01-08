// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
var g_timelineView;
(function() {
  var include = function(path) {
    document.write('<script src="' + path + '"></script>');
  };
  include("/chrome/tracing/overlay.js");
  include("/chrome/tracing/timeline_model.js");
  include("/chrome/tracing/linux_perf_importer.js");
  include("/chrome/tracing/trace_event_importer.js");
  include("/chrome/tracing/sorted_array_utils.js");
  include("/chrome/tracing/measuring_stick.js");
  include("/chrome/tracing/timeline.js");
  include("/chrome/tracing/timeline_track.js");
  include("/chrome/tracing/fast_rect_renderer.js");
  include("/chrome/tracing/timeline_view.js");

  var timelineView;

  function onDOMContentLoaded() {
    timelineView = $('timeline-view');
    g_timelineView = timelineView;
    cr.ui.decorate(timelineView, tracing.TimelineView);
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
      var i_ = i;
      getAsync(urls[i_],
               function(text) {
                 traces[i_] = text;
                 if(--traces_outstanding == 0)
                   finalizeLoad();
               },
               function(status) {
                 failure = true;
                 failureMessages.push('Load failed, got status=' + req.status + ' on ' + urls[i_]);
                 if(--traces_outstanding == 0)
                   finalizeLoad();
               });
    }
    function finalizeLoad() {
      if (failure) {
        chrome.send('loadTracesFromURLs_Failed', failureMessages);
        return;
      }
      var ok;
      try {
        ok = loadTraces(traces);
      } catch(err) {
        ok = false;
      }
      if (!ok)
        chrome.send('loadTracesFromURLs_Failed', ["import failed"]);
      else
        chrome.send('loadTracesFromURLs_Done');
    }
  }

  function loadTraces(events) {
    if (timelineView == undefined)
      throw Error('timelineview is null');

    var m = new tracing.TimelineModel();
    m.importEvents(events[0], true, events.slice(1));
    timelineView.model = m;
    return true;
  }

  window.loadTracesFromURLs = loadTracesFromURLs;
  window.loadTraces = loadTraces;
  document.addEventListener('DOMContentLoaded', onDOMContentLoaded);
})();
