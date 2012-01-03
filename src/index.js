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

  function loadTraceFromURL(url) {
    var req = new XMLHttpRequest();
    req.open('GET', url, false);
    req.send(null);
    if (req.status != 200)
      throw 'Load failed, got status=' + req.status + ' on ' + url
    loadTrace(req.responseText);
    return true;
  }

  function loadTrace(eventData) {
    if (timelineView == undefined)
      throw Error('timelineview is null');

    timelineView.traceData = eventData;
    return true;
  }

  window.loadTraceFromURL = loadTraceFromURL;
  window.loadTrace = loadTrace;
  document.addEventListener('DOMContentLoaded', onDOMContentLoaded);
})();
