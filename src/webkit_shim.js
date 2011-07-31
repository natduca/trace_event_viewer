// Copyright 2011 Google Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Chrome's codebase is written to expect the most current version
// of WebKit. Whereas, trace_event is hosted in whatever version of
// WebKit that PyGtk or WxPython uses. So, we have to fake things out.

// NOTE: don't depend on cr.PropertyKind.ATTR being null vs undefined ...
//       non-Chrome WebKits give undefined for non-present elements, but when
//       you set an attribute to undefined, older WebKits tells you its
//       undefined. Mert.

if (!window["DOMTokenList"]) {
  function _DOMTokenList(parentEl) {
    this.parentEl = parentEl;
  }

  _DOMTokenList.prototype = {
    __proto__: Object.prototype,

    get _tokens() {
      return this.parentEl.className.split(' ');
    },
    set _tokens(tokens) {
      this.parentEl.className = tokens.join(" ");
    },

    add: function(token) {
      var t = this._tokens;
      var i = t.indexOf(token);
      if (i == -1) {
        t.push(token);
        this._tokens = t;
      }
    },
    remove: function(token) {
      var t = this._tokens;
      var i = t.indexOf(token);
      if (i >= 0) {
        t.splice(i, 1);
        this._tokens = t;
      } else {
        throw Error("Token not found!");
      }
    },
    contains: function(token) {
      var t = this._tokens;
      return t.indexOf(token) >= 0;
    },
    toggle: function(token) {
      if (this.contains(token))
        this.remove(token);
      else
        this.add(token);
    },
    item: function(i) {
      return this._tokens[i];
    }
  };
  
  (function() {
    function fixup(el) {
      el.classList = new _DOMTokenList(el);
      for (var i = 0; i < el.children.length; ++i) {
        fixup(el.children[i]);
      }
    }
    fixup(document.documentElement);
    
    document._createElement = document.createElement;
    document.createElement = function(tagName) {
      var el = document._createElement(tagName);
      el.classList = new _DOMTokenList(el);
      return el;
    }
    document.addEventListener('DOMContentLoaded', function() {
      fixup(document.body);
    });
  })();
}
