/* ************************************************************************

   qooxdoo - the new era of web development

   http://qooxdoo.org

   Copyright:
     2004-2011 1&1 Internet AG, Germany, http://www.1und1.de

   License:
     LGPL: http://www.gnu.org/licenses/lgpl.html
     EPL: http://www.eclipse.org/org/documents/epl-v10.php
     See the LICENSE file in the project's top-level directory for details.

   Authors:
     * Martin Wittemann (martinwittemann)

************************************************************************ */
/**
 * Internal class which contains the checks used by {@link qx.core.Environment}.
 * All checks in here are marked as internal which means you should never use
 * them directly.
 *
 * This class should contain all checks about HTML.
 *
 * @internal
 */
qx.Bootstrap.define("qx.bom.client.Html",
{
  statics:
  {
    /**
     * Whether the client supports Web Workers.
     *
     * @internal
     * @return {Boolean} <code>true</code> if webworkers are supported
     */
    getWebWorker : function() {
      return window.Worker != null;
    },


    /**
     * Whether the client supports File Readers
     *
     * @internal
     * @return {Boolean} <code>true</code> if FileReaders are supported
     */
    getFileReader : function() {
      return window.FileReader != null;
    },


    /**
     * Whether the client supports Geo Location.
     *
     * @internal
     * @return {Boolean} <code>true</code> if geolocation supported
     */
    getGeoLocation : function() {
      return navigator.geolocation != null;
    },


    /**
     * Whether the client supports audio.
     *
     * @internal
     * @return {Boolean} <code>true</code> if audio is supported
     */
    getAudio : function() {
      return !!document.createElement('audio').canPlayType;
    },

    /**
     * Whether the client can play ogg audio format.
     *
     * @internal
     * @return {String} "" or "maybe" or "probably"
     */
    getAudioOgg : function() {
      if (!qx.bom.client.Html.getAudio()) {
        return "";
      }
      var a = document.createElement("audio");
      return a.canPlayType("audio/ogg");
    },

    /**
     * Whether the client can play mp3 audio format.
     *
     * @internal
     * @return {String} "" or "maybe" or "probably"
     */
    getAudioMp3 : function() {
      if (!qx.bom.client.Html.getAudio()) {
        return "";
      }
      var a = document.createElement("audio");
      return a.canPlayType("audio/mpeg");
    },

    /**
     * Whether the client can play wave audio wave format.
     *
     * @internal
     * @return {String} "" or "maybe" or "probably"
     */
    getAudioWav : function() {
      if (!qx.bom.client.Html.getAudio()) {
        return "";
      }
      var a = document.createElement("audio");
      return a.canPlayType("audio/x-wav");
    },

    /**
     * Whether the client can play au audio format.
     *
     * @internal
     * @return {String} "" or "maybe" or "probably"
     */
    getAudioAu : function() {
      if (!qx.bom.client.Html.getAudio()) {
        return "";
      }
      var a = document.createElement("audio");
      return a.canPlayType("audio/basic");
    },

    /**
     * Whether the client can play aif audio format.
     *
     * @internal
     * @return {String} "" or "maybe" or "probably"
     */
    getAudioAif : function() {
      if (!qx.bom.client.Html.getAudio()) {
        return "";
      }
      var a = document.createElement("audio");
      return a.canPlayType("audio/x-aiff");
    },


    /**
     * Whether the client supports video.
     *
     * @internal
     * @return {Boolean} <code>true</code> if video is supported
     */
    getVideo : function() {
      return !!document.createElement('video').canPlayType;
    },

    /**
     * Whether the client supports ogg video.
     *
     * @internal
     * @return {String} "" or "maybe" or "probably"
     */
    getVideoOgg : function() {
      if (!qx.bom.client.Html.getVideo()) {
        return "";
      }
      var v = document.createElement("video");
      return v.canPlayType('video/ogg; codecs="theora, vorbis"');
    },

    /**
     * Whether the client supports mp4 video.
     *
     * @internal
     * @return {String} "" or "maybe" or "probably"
     */
    getVideoH264 : function() {
      if (!qx.bom.client.Html.getVideo()) {
        return "";
      }
      var v = document.createElement("video");
      return v.canPlayType('video/mp4; codecs="avc1.42E01E, mp4a.40.2"');
    },

    /**
     * Whether the client supports webm video.
     *
     * @internal
     * @return {String} "" or "maybe" or "probably"
     */
    getVideoWebm : function() {
      if (!qx.bom.client.Html.getVideo()) {
        return "";
      }
      var v = document.createElement("video");
      return v.canPlayType('video/webm; codecs="vp8, vorbis"');
    },

    /**
     * Whether the client supports local storage.
     *
     * @internal
     * @return {Boolean} <code>true</code> if local storage is supported
     */
    getLocalStorage : function() {
      try {
        return window.localStorage != null;
      } catch (exc) {
        // Firefox Bug: Local execution of window.sessionStorage throws error
        // see https://bugzilla.mozilla.org/show_bug.cgi?id=357323
        return false;
      }
    },


    /**
     * Whether the client supports session storage.
     *
     * @internal
     * @return {Boolean} <code>true</code> if session storage is supported
     */
    getSessionStorage : function() {
      try {
        return window.sessionStorage != null;
      } catch (exc) {
        // Firefox Bug: Local execution of window.sessionStorage throws error
        // see https://bugzilla.mozilla.org/show_bug.cgi?id=357323
        return false;
      }
    },


    /**
     * Whether the browser supports CSS class lists.
     * https://developer.mozilla.org/en/DOM/element.classList
     *
     * @internal
     * @return {Boolean} <code>true</code> if class list is supported.
     */
    getClassList : function() {
      return !!(document.documentElement.classList &&
        qx.Bootstrap.getClass(document.documentElement.classList) === "DOMTokenList"
      );
    },


    /**
     * Checks if XPath could be used.
     *
     * @internal
     * @return {Boolean} <code>true</code> if xpath is supported.
     */
    getXPath : function() {
      return !!document.evaluate;
    },


    /**
     * Checks if XUL could be used.
     *
     * @internal
     * @return {Boolean} <code>true</code> if XUL is supported.
     */
    getXul : function() {
      try {
        document.createElementNS("http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul", "label");
        return true;
      } catch (e) {
        return false;
      }
    },


    /**
     * Checks if SVG could be used
     *
     * @internal
     * @return {Boolean} <code>true</code> if SVG is supported.
     */
    getSvg : function() {
      return document.implementation && document.implementation.hasFeature &&
        (document.implementation.hasFeature("org.w3c.dom.svg", "1.0") ||
        document.implementation.hasFeature(
          "http://www.w3.org/TR/SVG11/feature#BasicStructure",
          "1.1"
        )
      );
    },


    /**
     * Checks if VML could be used
     *
     * @internal
     * @return {Boolean} <code>true</code> if VML is supported.
     */
    getVml : function() {
      return qx.bom.client.Engine.getName() == "mshtml";
    },


    /**
     * Checks if canvas could be used
     *
     * @internal
     * @return {Boolean} <code>true</code> if canvas is supported.
     */
    getCanvas : function() {
      return !!window.CanvasRenderingContext2D;
    },


    /**
     * Asynchronous check for using data urls.
     *
     * @internal
     * @param callback {Function} The function which should be executed as
     *   soon as the check is done.
     */
    getDataUrl : function(callback) {
      var data = new Image();
      data.onload = data.onerror = function() {
        // wrap that into a timeout because IE might execute it synchronously
        window.setTimeout(function() {
          callback.call(null, (data.width == 1 && data.height == 1));
        }, 0);
      };
      data.src = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==";
    },

    /**
     * Checks if dataset could be used
     *
     * @internal
     * @return {Boolean} <code>true</code> if dataset is supported.
     */
    getDataset : function() {
      return !!document.documentElement.dataset;
    },


    /**
     * Check for element.contains
     * 
     * @internal
     * @return {Boolean} <code>true</code> if element.contains is supported
     */
    getContains : function()
    {
      // "object" in IE6/7/8, "function" in IE9
      return (typeof document.documentElement.contains !== "undefined");
    },
    
    
    /**
     * Check for element.compareDocumentPosition
     * 
     * @internal
     * @return {Boolean} <code>true</code> if element.compareDocumentPosition is supported
     */
    getCompareDocumentPosition : function()
    {
      return (typeof document.documentElement.compareDocumentPosition === "function");
    },


    /**
     * Check for element.textContent. Legacy IEs do not support this, use
     * innerText instead.
     * 
     * @internal
     * @return {Boolean} <code>true</code> if textContent is supported
     */
    getTextContent : function()
    {
      var el = document.createElement("span");
      return (typeof el.textContent !== "undefined");
    },


    /**
     * Check for a console object.
     * 
     * @internal
     * @return {Boolean} <code>true</code> if a console is available.
     */
    getConsole : function()
    {
      return typeof window.console !== "undefined";
    }
  },

  defer : function (statics) {
    qx.core.Environment.add("html.webworker", statics.getWebWorker),
    qx.core.Environment.add("html.filereader", statics.getFileReader),
    qx.core.Environment.add("html.geolocation", statics.getGeoLocation),
    qx.core.Environment.add("html.audio", statics.getAudio),
    qx.core.Environment.add("html.audio.ogg", statics.getAudioOgg),
    qx.core.Environment.add("html.audio.mp3", statics.getAudioMp3),
    qx.core.Environment.add("html.audio.wav", statics.getAudioWav),
    qx.core.Environment.add("html.audio.au", statics.getAudioAu),
    qx.core.Environment.add("html.audio.aif", statics.getAudioAif),
    qx.core.Environment.add("html.video", statics.getVideo),
    qx.core.Environment.add("html.video.ogg", statics.getVideoOgg),
    qx.core.Environment.add("html.video.h264", statics.getVideoH264),
    qx.core.Environment.add("html.video.webm", statics.getVideoWebm),
    qx.core.Environment.add("html.storage.local", statics.getLocalStorage),
    qx.core.Environment.add("html.storage.session", statics.getSessionStorage),
    qx.core.Environment.add("html.classlist", statics.getClassList),
    qx.core.Environment.add("html.xpath", statics.getXPath),
    qx.core.Environment.add("html.xul", statics.getXul),
    qx.core.Environment.add("html.canvas", statics.getCanvas),
    qx.core.Environment.add("html.svg", statics.getSvg),
    qx.core.Environment.add("html.vml", statics.getVml),
    qx.core.Environment.add("html.dataset", statics.getDataset),
    qx.core.Environment.addAsync("html.dataurl", statics.getDataUrl)
    qx.core.Environment.add("html.element.contains", statics.getContains);
    qx.core.Environment.add("html.element.compareDocumentPosition", statics.getCompareDocumentPosition);
    qx.core.Environment.add("html.element.textcontent", statics.getTextContent);
    qx.core.Environment.add("html.console", statics.getConsole);
  }
});
