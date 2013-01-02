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
- python2.6 or better
- chrome


Trace file format
============

See the [trace-viewer codesite](http://code.google.com/p/trace-viewer/) for information on the formats
that trace-viewer supports.
