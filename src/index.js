// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
include = function(path) {
  document.write('<script src="' + path + '"></script>');
}
include("gpu_internals/overlay.js");
include("gpu_internals/timeline_model.js");
include("gpu_internals/sorted_array_utils.js");
include("gpu_internals/timeline.js");
include("gpu_internals/timeline_track.js");
include("gpu_internals/fast_rect_renderer.js");
include("gpu_internals/timeline_view.js");

var timelineView;

function onDOMContentLoaded() {
  timelineView = $('timeline-view');
  cr.ui.decorate(timelineView, gpu.TimelineView);
  chrome.send('ready')
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


document.addEventListener('DOMContentLoaded', onDOMContentLoaded);