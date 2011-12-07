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

  function loadTraceFromURL(url) {
    var req = new XMLHttpRequest();
    req.open('GET', url, false);
    req.send(null);
    if (req.status != 200)
      throw "Load failed"
    var resp = JSON.parse(req.responseText);
    loadTrace(resp);
    return true;
  }

  function loadTrace(trace) {
    if (timelineView == undefined)
      throw Error('timelineview is null');

    // some old traces were just arrays without an outer object
    if (!trace.traceEvents) {
      if (trace instanceof Array)
        timelineView.traceEvents = trace;
      else
        throw Error('trace does not have an events array');
    } else {
      timelineView.traceEvents = trace.traceEvents;
    }
    return true;
  }

  window.loadTraceFromURL = loadTraceFromURL;
  window.loadTrace = loadTrace;
  document.addEventListener('DOMContentLoaded', onDOMContentLoaded);
})();
