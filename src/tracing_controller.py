#!/usr/bin/env python
# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Note, this is untested because to properly test it, I need to rector the
# GpuInternals code for better unit testing of this interface.
import json
class TracingController(object):
  def __init__(self, chrome_shim):
    chrome_shim.add_event_listener('beginRequestBufferPercentFull', self.on_begin_request_buffer_percent_full)
    chrome_shim.add_event_listener('beginTracing', self.on_begin_tracing)
    chrome_shim.add_event_listener('endTracingAsync', self.on_end_tracing_async)    
    chrome_shim.add_event_listener('loadTraceFile', self.on_load_trace_file)
    chrome_shim.add_event_listener('saveTraceFile', self.on_save_trace_file)
    chrome_shim.add_event_listener('on', self.on_load_trace_file)
    self.browser = chrome_shim.browser


  # recording --- not implemented
  def on_begin_request_buffer_percent_full(self):
    self.browser.run_javascript('tracingController.onRequestBufferPercentFullComplete(0)');

  
  def on_begin_tracing(self):
    self.browser.run_javascript('tracingController.onEndTracingComplete()');

  def on_end_tracing_async(self):
    # self.browser.run_javascript('tracingController.onTraceDataCollected(events)');
    # self.browser.run_javascript('tracingController.onEndTracingComplete()');
    pass
  

  # loading
  def on_load_trace_file(self):
    print "File loading not implemented yet."
    # onLoadTraceFileComplete(data)
    self.browser.run_javascript('tracingController.onLoadTraceFileCanceled()');

  # saving
  def on_save_trace_file(self, data):
    print "File saving not implemented yet."
    # onSaveTraceFileComplete
    self.browser.run_javascript('tracingController.onSaveTraceFileCanceled()');