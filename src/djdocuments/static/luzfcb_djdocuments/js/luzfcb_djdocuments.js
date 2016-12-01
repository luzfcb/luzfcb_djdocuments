/**
 * Created by luzfcb on 24/02/16.
 */

var zeropad = function (n, c) {
    'use strict';

    var s = String(n);
    if (s.length < c) {
        return zeropad("0" + n, c);
    }
    else {
        return s;
    }
};

var identificador_doc = function (id_doc, versao_doc) {
    'use strict';
    return zeropad(id_doc, 8) + 'v' + zeropad(versao_doc, 3);
};

function contem(a, b) {
    'use strict';
    return String.prototype.indexOf.call(String.prototype.toLowerCase.call(a), String.prototype.toLowerCase.call(b)) !== -1;
}
function inserirApos(caracter, strOriginal, strParaInserir) {
    'use strict';
    // obs: insere no inicio se caractere nao for encontrado
    var idx = String.prototype.indexOf.call(strOriginal, caracter);
    if (idx == strOriginal.length) {
        return strOriginal + strParaInserir;
    }
    else {
        idx = idx + 1;
        return (strOriginal.slice(0, idx) + strParaInserir + strOriginal.slice(idx + Math.abs(0)));
    }
}
function inserirAntes(caracter, strOriginal, strParaInserir) {
    'use strict';
    // obs: insere no inicio se caractere nao for encontrado
    var idx = String.prototype.indexOf.call(strOriginal, caracter);
    if (idx == strOriginal.length || idx < 0) {
        return strParaInserir + strOriginal;
    }
    else {
        return (strOriginal.slice(0, idx) + strParaInserir + strOriginal.slice(idx + Math.abs(0)));
    }
}
jQuery(document).ready(function ($) {
    'use strict';

    jQuery(document).on('click', '.djpopup', function () {

        var popUpObj;
        //var id = $(this).attr('id');
        var id = uuid.v4();
        var url_to_open = $(this).prop("href");
        var desabilitado = $(this).attr("disabled") || false;

        if (!desabilitado) {
            // console.table($(this));
            var width = 990;
            var height = 980;
            //var h = $(this).data('height');
            //var s = $(this).data('scrollbars');
            var fullscreen = $(this).hasClass('djfullscreen');

            if (fullscreen) {
                width = screen.width;
                height = screen.height
            }
            //
            //
            //var left = (screen.width / 2) - (w / 2);
            //var top = (screen.height / 2) - (h / 2);
            //var features = 'scrollbars=' + s + ',resizable=yes,width=' + w + ',height=' + h + ',top=' + top + ',left=' + left + ',modal=yes';
            //

            if (!contem(url_to_open, 'popup=')) {
                if (contem(url_to_open, '?')) {
                    url_to_open = inserirApos('?', url_to_open, "popup=1&");
                }
                else {
                    if (contem(url_to_open, '#')) {
                        url_to_open = inserirAntes('#', url_to_open, "?popup=1");
                    }
                    else {
                        url_to_open = url_to_open + "?popup=1";
                    }
                }
            }
            // var popup_windows_options = 'all=yes';
            var popup_windows_options = "toolbar=no," +
                "scrollbars=yes," +
                "location=no," +
                "statusbar=no," +
                "menubar=no," +
                "resizable=0," +
                "width=" + width + "," +
                "height=" + height + "," +
                //"left = 490," +
                //"top=300"
                "";

            popUpObj = window.open(url_to_open, id, popup_windows_options);

            if (window.focus) {
                popUpObj.focus();
            }


            //popUpObj = window.open(url_to_open,
            //    id,
            //    "ModalPopUp",
            //    "toolbar=no," +
            //    "scrollbars=no," +
            //    "location=no," +
            //    "statusbar=no," +
            //    "menubar=no," +
            //    "resizable=0," +
            //    "width=100," +
            //    "height=100," +
            //    "left = 490," +
            //    "top=300");

            if ($(this).hasClass('.nolock') === false) {

                LoadModalDiv(popUpObj);
                autoHideModalDivIfPopUPClosed(popUpObj);
            }
        }
        return false;

    });

    function autoHideModalDivIfPopUPClosed(popUpObj) {
        var timer = setInterval(function () {
            if (popUpObj.closed) {
                clearInterval(timer);
                HideModalDiv('');
            }
        }, 500);

    }

    function LoadModalDiv(popUpObj) {
        var jdDivBackground_id = "jdDivBackground";
        var bcgDiv = document.getElementById(jdDivBackground_id);
        if (bcgDiv === null) {
            bcgDiv = document.createElement("div");
            bcgDiv.setAttribute("id", jdDivBackground_id);
            bcgDiv.setAttribute("style", " position:fixed; top:0px; left:0px;background-color:black; z-index:100000;opacity: 0.8;filter:alpha(opacity=60); -moz-opacity: 0.8; overflow:hidden; display:none");
            document.body.appendChild(bcgDiv);
        }
        function focus_on_popup() {
            popUpObj.focus();
        }

        if (popUpObj) {
            bcgDiv.onclick = focus_on_popup;
        }


        bcgDiv.style.display = "block";


        if (bcgDiv != null) {
            //if (document.body.clientHeight > document.body.scrollHeight) {
            //    bcgDiv.style.height = document.body.clientHeight + "px";
            //}
            //else {
            //    bcgDiv.style.height = document.body.scrollHeight + "px";
            //}
            bcgDiv.style.width = "100%";
            bcgDiv.style.height = "100%";
        }
    }

});

function getURLParameter(name) {
    'use strict';
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [, ""])[1].replace(/\+/g, '%20')) || null;
}
function redirecionar(param) {
    'use strict';
    //console.log("algo aqui:" + window.location.href);
    //if (param.charAt(0) !== "/") {
    //    param = "/" + param;
    //}
    //if (window.location.port !== "80" || window.location.port !== "443") {
    //    param = ":" + window.location.port + param;
    //}
    //window.location.href = window.location.protocol + "//" + window.location.hostname + param;
    window.location.href = param;

}
function HideModalDiv(param) {
    'use strict';
    var bcgDiv = document.getElementById("jdDivBackground");
    bcgDiv.style.display = "none";
    //var bcgbody = document.getElementsByName('body');
    //document.focus();
    //redirecionar(param);
}


//     uuid.js
//     https://github.com/broofa/node-uuid
//
//     Copyright (c) 2010-2012 Robert Kieffer
//     MIT License - http://opensource.org/licenses/mit-license.php
/*eslint-disable */
(function () {
    var _global = this;

    // Unique ID creation requires a high quality random # generator.  We feature
    // detect to determine the best RNG source, normalizing to a function that
    // returns 128-bits of randomness, since that's what's usually required
    var _rng;

    // Allow for MSIE11 msCrypto
    var _crypto = _global.crypto || _global.msCrypto;

    // Node.js crypto-based RNG - http://nodejs.org/docs/v0.6.2/api/crypto.html
    //
    // Moderately fast, high quality
    if (typeof(_global.require) == 'function') {
        try {
            var _rb = _global.require('crypto').randomBytes;
            _rng = _rb && function () {
                    return _rb(16);
                };
        } catch (e) {
        }
    }

    if (!_rng && _crypto && _crypto.getRandomValues) {
        // WHATWG crypto-based RNG - http://wiki.whatwg.org/wiki/Crypto
        //
        // Moderately fast, high quality
        var _rnds8 = new Uint8Array(16);
        _rng = function whatwgRNG() {
            _crypto.getRandomValues(_rnds8);
            return _rnds8;
        };
    }

    if (!_rng) {
        // Math.random()-based (RNG)
        //
        // If all else fails, use Math.random().  It's fast, but is of unspecified
        // quality.
        var _rnds = new Array(16);
        _rng = function () {
            for (var i = 0, r; i < 16; i++) {
                if ((i & 0x03) === 0) r = Math.random() * 0x100000000;
                _rnds[i] = r >>> ((i & 0x03) << 3) & 0xff;
            }

            return _rnds;
        };
    }

    // Buffer class to use
    var BufferClass = typeof(_global.Buffer) == 'function' ? _global.Buffer : Array;

    // Maps for number <-> hex string conversion
    var _byteToHex = [];
    var _hexToByte = {};
    for (var i = 0; i < 256; i++) {
        _byteToHex[i] = (i + 0x100).toString(16).substr(1);
        _hexToByte[_byteToHex[i]] = i;
    }

    // **`parse()` - Parse a UUID into it's component bytes**
    function parse(s, buf, offset) {
        var i = (buf && offset) || 0, ii = 0;

        buf = buf || [];
        s.toLowerCase().replace(/[0-9a-f]{2}/g, function (oct) {
            if (ii < 16) { // Don't overflow!
                buf[i + ii++] = _hexToByte[oct];
            }
        });

        // Zero out remaining bytes if string was short
        while (ii < 16) {
            buf[i + ii++] = 0;
        }

        return buf;
    }

    // **`unparse()` - Convert UUID byte array (ala parse()) into a string**
    function unparse(buf, offset) {
        var i = offset || 0, bth = _byteToHex;
        return bth[buf[i++]] + bth[buf[i++]] +
            bth[buf[i++]] + bth[buf[i++]] + '-' +
            bth[buf[i++]] + bth[buf[i++]] + '-' +
            bth[buf[i++]] + bth[buf[i++]] + '-' +
            bth[buf[i++]] + bth[buf[i++]] + '-' +
            bth[buf[i++]] + bth[buf[i++]] +
            bth[buf[i++]] + bth[buf[i++]] +
            bth[buf[i++]] + bth[buf[i++]];
    }

    // **`v1()` - Generate time-based UUID**
    //
    // Inspired by https://github.com/LiosK/UUID.js
    // and http://docs.python.org/library/uuid.html

    // random #'s we need to init node and clockseq
    var _seedBytes = _rng();

    // Per 4.5, create and 48-bit node id, (47 random bits + multicast bit = 1)
    var _nodeId = [
        _seedBytes[0] | 0x01,
        _seedBytes[1], _seedBytes[2], _seedBytes[3], _seedBytes[4], _seedBytes[5]
    ];

    // Per 4.2.2, randomize (14 bit) clockseq
    var _clockseq = (_seedBytes[6] << 8 | _seedBytes[7]) & 0x3fff;

    // Previous uuid creation time
    var _lastMSecs = 0, _lastNSecs = 0;

    // See https://github.com/broofa/node-uuid for API details
    function v1(options, buf, offset) {
        var i = buf && offset || 0;
        var b = buf || [];

        options = options || {};

        var clockseq = options.clockseq != null ? options.clockseq : _clockseq;

        // UUID timestamps are 100 nano-second units since the Gregorian epoch,
        // (1582-10-15 00:00).  JSNumbers aren't precise enough for this, so
        // time is handled internally as 'msecs' (integer milliseconds) and 'nsecs'
        // (100-nanoseconds offset from msecs) since unix epoch, 1970-01-01 00:00.
        var msecs = options.msecs != null ? options.msecs : new Date().getTime();

        // Per 4.2.1.2, use count of uuid's generated during the current clock
        // cycle to simulate higher resolution clock
        var nsecs = options.nsecs != null ? options.nsecs : _lastNSecs + 1;

        // Time since last uuid creation (in msecs)
        var dt = (msecs - _lastMSecs) + (nsecs - _lastNSecs) / 10000;

        // Per 4.2.1.2, Bump clockseq on clock regression
        if (dt < 0 && options.clockseq == null) {
            clockseq = clockseq + 1 & 0x3fff;
        }

        // Reset nsecs if clock regresses (new clockseq) or we've moved onto a new
        // time interval
        if ((dt < 0 || msecs > _lastMSecs) && options.nsecs == null) {
            nsecs = 0;
        }

        // Per 4.2.1.2 Throw error if too many uuids are requested
        if (nsecs >= 10000) {
            throw new Error('uuid.v1(): Can\'t create more than 10M uuids/sec');
        }

        _lastMSecs = msecs;
        _lastNSecs = nsecs;
        _clockseq = clockseq;

        // Per 4.1.4 - Convert from unix epoch to Gregorian epoch
        msecs += 12219292800000;

        // `time_low`
        var tl = ((msecs & 0xfffffff) * 10000 + nsecs) % 0x100000000;
        b[i++] = tl >>> 24 & 0xff;
        b[i++] = tl >>> 16 & 0xff;
        b[i++] = tl >>> 8 & 0xff;
        b[i++] = tl & 0xff;

        // `time_mid`
        var tmh = (msecs / 0x100000000 * 10000) & 0xfffffff;
        b[i++] = tmh >>> 8 & 0xff;
        b[i++] = tmh & 0xff;

        // `time_high_and_version`
        b[i++] = tmh >>> 24 & 0xf | 0x10; // include version
        b[i++] = tmh >>> 16 & 0xff;

        // `clock_seq_hi_and_reserved` (Per 4.2.2 - include variant)
        b[i++] = clockseq >>> 8 | 0x80;

        // `clock_seq_low`
        b[i++] = clockseq & 0xff;

        // `node`
        var node = options.node || _nodeId;
        for (var n = 0; n < 6; n++) {
            b[i + n] = node[n];
        }

        return buf ? buf : unparse(b);
    }

    // **`v4()` - Generate random UUID**

    // See https://github.com/broofa/node-uuid for API details
    function v4(options, buf, offset) {
        // Deprecated - 'format' argument, as supported in v1.2
        var i = buf && offset || 0;

        if (typeof(options) == 'string') {
            buf = options == 'binary' ? new BufferClass(16) : null;
            options = null;
        }
        options = options || {};

        var rnds = options.random || (options.rng || _rng)();

        // Per 4.4, set bits for version and `clock_seq_hi_and_reserved`
        rnds[6] = (rnds[6] & 0x0f) | 0x40;
        rnds[8] = (rnds[8] & 0x3f) | 0x80;

        // Copy bytes to buffer, if provided
        if (buf) {
            for (var ii = 0; ii < 16; ii++) {
                buf[i + ii] = rnds[ii];
            }
        }

        return buf || unparse(rnds);
    }

    // Export public API
    var uuid = v4;
    uuid.v1 = v1;
    uuid.v4 = v4;
    uuid.parse = parse;
    uuid.unparse = unparse;
    uuid.BufferClass = BufferClass;

    if (typeof(module) != 'undefined' && module.exports) {
        // Publish as node.js module
        module.exports = uuid;
    }
    else if (typeof define === 'function' && define.amd) {
        // Publish as AMD module
        define(function () {
            return uuid;
        });


    }
    else {
        // Publish as global (in browsers)
        var _previousRoot = _global.uuid;

        // **`noConflict()` - (browser only) to reset global 'uuid' var**
        uuid.noConflict = function () {
            _global.uuid = _previousRoot;
            return uuid;
        };

        _global.uuid = uuid;
    }
}).call(this);
/*eslint-enable */
