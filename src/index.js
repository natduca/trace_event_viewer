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

  function loadTracesFromURLs(urls) {
    var traces = [];
    for (var i = 0; i < urls.length; ++i) {
      var req = new XMLHttpRequest();
      req.open('GET', urls[i], false);
      req.send(null);
      if (req.status != 200)
        throw 'Load failed, got status=' + req.status + ' on ' + urls[i]
      traces.push(req.responseText);
    }
    return loadTraces(traces);
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
