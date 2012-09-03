trace\_event\_viewer` is a standalone version of Chrome's about:tracing UI for
viewing multithreaded performance traces. Works on OSX and Linux.

The core ui of this tool is a javascript app, hosted in a separate project at [trace-viewer](http://code.google.com/p/trace-viewer/). All importing is handled by that module, so [head on over to its project](http://code.google.com/p/trace-viewer/) to find out how to generate traces.

QuickStart
========

**Make sure to git submodule update --init after cloning**

./trace-event-viewer trace_event/data/big_trace.json

    w/a/s/d to move around the UI

Dependencies
==========
Linux:

1. python-gtk2
2. python-webkit

OSX: either,

- wxPython 2.8-osx-unicode-2.6 from (http://www.wxpython.org/download.php#stable)[http://www.wxpython.org/download.php#stable], or
- Pass `--objc` to enable the [beta quality] PyObjC-based GUI

Windows: Not supported, but should be possible.


Trace file format
============

See the [trace-viewer codesite](http://code.google.com/p/trace-viewer/) for information on the formats
that trace-viewer supports.
