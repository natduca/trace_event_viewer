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
import message_loop

def open_file():
  message_loop.init_main_loop()
  if message_loop.is_gtk:
    raise Exception("not implemented")
  else:
    import wx
    wc = "JSON files (*.json)|*.json|All files (*.*)|*.*"
    fd = wx.FileDialog(None, "Open trace file...", style=wx.FD_OPEN, wildcard=wc)
    res = fd.ShowModal()
    if res != wx.ID_OK:
      return None
    return fd.GetPath()
