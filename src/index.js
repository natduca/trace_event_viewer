// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
(function() {
  var include = function(path) {
    document.write('<script src="' + path + '"></script>');
  };
  include("/chrome/gpu_internals/overlay.js");
  include("/chrome/gpu_internals/timeline_model.js");
  include("/chrome/gpu_internals/sorted_array_utils.js");
  include("/chrome/gpu_internals/timeline.js");
  include("/chrome/gpu_internals/timeline_track.js");
  include("/chrome/gpu_internals/fast_rect_renderer.js");
  include("/chrome/gpu_internals/timeline_view.js");

  var timelineView;

  function onDOMContentLoaded() {
    timelineView = $('timeline-view');
    cr.ui.decorate(timelineView, gpu.TimelineView);
    chrome.send('ready');
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

  window.loadTrace = loadTrace;
  document.addEventListener('DOMContentLoaded', onDOMContentLoaded);
})();