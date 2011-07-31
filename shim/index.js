// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
include = function(path) {
  document.write('<script src="' + path + '"></script>');
}
include("gpu_internals/overlay.js");
include("gpu_internals/browser_bridge.js");
include("gpu_internals/tracing_controller.js");
include("gpu_internals/info_view.js");
include("gpu_internals/timeline_model.js");
include("gpu_internals/sorted_array_utils.js");
include("gpu_internals/timeline.js");
include("gpu_internals/timeline_track.js");
include("gpu_internals/fast_rect_renderer.js");
include("gpu_internals/profiling_view.js");
include("gpu_internals/timeline_view.js");

var browserBridge;
var tracingController;
var timelineView; // made global for debugging purposes only
var profilingView; // made global for debugging purposes only

/**
 * Main entry point. called once the page has loaded.
 */
function onLoad() {
  browserBridge = new gpu.BrowserBridge();
  tracingController = new gpu.TracingController();

  // Create the views.
  cr.ui.decorate('#info-view', gpu.InfoView);

  profilingView = $('profiling-view');
  cr.ui.decorate(profilingView, gpu.ProfilingView);

  // Create the main tab control
  var tabs = $('main-tabs');
  cr.ui.decorate(tabs, cr.ui.TabBox);

  // Sync the main-tabs selectedTabs in-sync with the location.
  tabs.addEventListener('selectedChange', function() {
    if (tabs.selectedTab.id) {
      history.pushState('', '', '#' + tabs.selectedTab.id);
    }
  });
  window.onhashchange = function() {
    var cur = window.location.hash;
    if (cur == '#' || cur == '') {
      tabs.selectedTab = $('info-view');
    } else {
      var tab = $(window.location.hash.substr(1));
      if (tab)
        tabs.selectedTab = tab;
    }
  };
  window.onhashchange();
}

document.addEventListener('DOMContentLoaded', onLoad);