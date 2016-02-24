#!/usr/bin/env python
#
# Downloader for Google Web Fonts
#
# For usage information run with "--help"
#
# Works on Python 2.6 and later, 3 and later
# Requires tinycss (and argparse for Python 2.6) from pip
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Copyright 2012 Kevin Locke <kevin@kevinlocke.name>

from __future__ import with_statement

import argparse
import collections
import errno
import gzip
import io
import itertools
import logging
import os
import re
import shutil
import sys

import tinycss

try:
    from httplib import HTTPConnection, HTTPSConnection
except ImportError:
    from http.client import HTTPConnection, HTTPSConnection

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

VERSION = (0, 1, 0)

# ADT for font positional command-line arguments
FontArgument = collections.namedtuple("FontArgument", ["family", "variants"])

# ADT for download information
DownloadInfo = collections.namedtuple("DownloadItem", ["url", "filename"])

# Default HTTP User-Agent string
default_user_agent = \
    "DL4GoogleWebFonts/" + ".".join(str(x) for x in VERSION)

# Mapping from font format to file extension
fontfmt_extensions = {
    "embedded-opentype": "eot",
    "opentype": "ttf",
    "svg": "svg",
    "truetype": "ttf",
    "woff": "woff",
}

# Mapping from font format to User-Agent string required to get the format
fontfmt_user_agent = {
    # EOT is served to IE 8-
    # IE 8 on Windows 7
    "embedded-opentype": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)",

    # SVG is served to Safari Mobile 3-4
    # Safari 3 on iPhone
    "svg": "Mozilla/5.0 (iPhone; U; CPU like Mac OS X) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3",

    # TTF is served to Android 4, Opera 11.01-, Safari Mobile 5+, non-Mobile Safari
    # Safari 6 on iPad
    "truetype": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/531.21.8 (KHTML, like Gecko) Version/4.0.4 Safari/531.21.10",

    # WOFF is served to Chrome, Firefox, Opera 11.10+
    # Firefox 15 on Ubuntu
    "woff": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1",
}

# Font formats which require separate requests for each variant
# FIXME:  This is probably UA-dependent.  Switch to non-separate where possible
fontfmt_serialize = frozenset(["embedded-opentype", "svg"])

logger = None


def setup_logging():
    """Initialize the global logger variable to a root logger for the console"""
    # global logger

    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)


setup_logging()


# TODO:  Replace with urllib3/Request (want to limit dependencies...)
class ConnectionPool(object):
    """A very simple and naive connection pool for HTTP/HTTPS"""

    _http_connections = {}
    _https_connections = {}

    def close(self, proto, host):
        if proto == "http":
            conn = self._http_connections.pop(host, None)
        elif proto == "https":
            conn = self._https_connections.pop(host, None)
        else:
            raise ValueError("Unsupported protocol")

        if conn:
            conn.close()

    def close_all(self):
        conns = itertools.chain(
            self._http_connections.values(),
            self._https_connections.values()
        )
        for conn in conns:
            conn.close()
        self._http_connections.clear()
        self._https_connections.clear()

    def get(self, proto, host):
        if proto == "http":
            if host not in self._http_connections:
                self._http_connections[host] = HTTPConnection(host)
            return self._http_connections[host]
        elif proto == "https":
            if host not in self._https_connections:
                self._https_connections[host] = HTTPSConnection(host)
            return self._https_connections[host]
        else:
            raise ValueError("Unsupported protocol")


# Shared global connection pool
connection_pool = ConnectionPool()


class FontFaceRule(object):
    """A parsed at-rule for declaring a font-face."""

    def __init__(self, at_keyword, declarations, line, column):
        self.at_keyword = at_keyword
        self.declarations = declarations
        self.line = line
        self.column = column


class CSSFontFace3Parser(tinycss.css21.CSS21Parser):
    """A CSS parser which recognizes @font-face rules."""

    def parse_at_rule(self, rule, previous_rules, errors, context):
        if rule.at_keyword == "@font-face":
            if rule.head:
                raise tinycss.css21.ParseError(rule.head[0],
                                               "Unexpected token {0} in {1} rule header".format(
                                                   rule.head[0].type, rule.at_keyword))
            declarations, body_errors = self.parse_declaration_list(rule.body)
            errors.extend(body_errors)
            return FontFaceRule(rule.at_keyword, declarations,
                                rule.line, rule.column)

        return super(CSSFontFace3Parser, self).parse_at_rule(rule,
                                                             previous_rules, errors, context)


# FIXME:  Should return HTTPResponse wrapper which handles decoding
def decode_response(response):
    """Returns a file-like object of the content data in an HTTPResponse"""

    encoding = response.getheader("Content-Encoding")
    if encoding == "gzip":
        if sys.version_info < (3, 2):
            gzipdata = io.BytesIO(response.read())
            responsedata = gzip.GzipFile(fileobj=gzipdata)
        else:
            responsedata = gzip.GzipFile(fileobj=response)
    elif encoding == "identity" or not encoding:
        responsedata = response
    else:
        raise RuntimeError("Server used unsupported content encoding '{0}'".format(encoding))

    return responsedata


def download_file(url, filename):
    """
        Downloads a given URL and save it with a given filename if that file
        does not exist
    """

    logger.info("Downloading '{0}' as '{1}'".format(url, filename))

    urlparts = urlparse.urlsplit(url)
    urlpath = urlparts.path
    if urlparts.query:
        urlpath += "?" + urlparts.query

    conn = connection_pool.get(urlparts.scheme, urlparts.netloc)

    headers = {
        "Accept-Encoding": "gzip",
        "Connection": "keep-alive",
        "User-Agent": default_user_agent,
    }
    conn.request(method="GET", url=urlpath, headers=headers)
    response = conn.getresponse()

    if response.status != 200:
        logger.error("Server returned status {0} ({1}) for {2}".format(
            response.status, response.reason, url))
        return False
    else:
        logger.debug("Server returned status {0} ({1}) for {2}".format(
            response.status, response.reason, url))

    responsedata = decode_response(response)

    try:
        fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0666)
    except OSError as e:
        if e.errno == errno.EEXIST:
            logger.warn("File '{0}' already exists, skipping".format(filename))
        else:
            logger.error("Unable to open output file '{0}': {1}".format(filename, str(e)), exc_info=True)
        return False

    try:
        with os.fdopen(fd, "wb") as outfile:
            shutil.copyfileobj(responsedata, outfile)
    except Exception as e:
        logger.error("Error downloading {0}: {1}".format(url, str(e)), exc_info=True)
        return False

    return True


def choose_font_name(names):
    """Choose the "best" filename for a font from a given set"""

    safe = [n for n in names if "/" not in n]

    remaining = [n for n in names if " " not in n]
    if len(remaining) == 0:
        # Try other heuristics
        remaining = safe

    if len(remaining) > 1:
        # Return the longest
        choice = reduce(lambda m, n: m if len(m) > len(n) else n, remaining)
    else:
        choice = remaining[0]

    logger.debug("Chose name '{0}' from {1}".format(choice, names))
    return choice


def extract_font_names(srctokens):
    """Returns any local font names from a list of CSS tokens"""

    names = []

    for token in srctokens:
        if token.type == "FUNCTION" and token.function_name == "local":
            # Content can be quoted or unquoted
            if len(token.content) == 1 and token.content[0].type == "STRING":
                names.append(token.content[0].value)
            else:
                names.append("".join([c.as_css() for c in token.content]))

    return names


def extract_font_urls(fontfmt, srctokens):
    """Returns any URLs matching a given format in a given list of CSS tokens"""

    url = None  # Last URL token parsed (cleared by non-S token)
    urls = []  # All URLs parsed

    for token in srctokens:
        if token.type == "URI":
            url = token.value
        elif token.type == "FUNCTION" and token.function_name == "format":
            if not url:
                logger.warn("CSS warning: Ignoring format() without associated url()")
            else:
                # CSS3 spec says format can be list of format strings
                # FIXME:  Should warn about non-STRING tokens and 0 STRINGs
                urlfontfmts = [t.value for t in token.content if t.type == "STRING"]
                if fontfmt in urlfontfmts:
                    urls.append(url)
                else:
                    logger.debug("Ignoring URL {0} with format({1}) while fetching format({2})".format(
                        url, "".join([c.as_css() for c in token.content]), fontfmt))
                url = None
        elif token.type == "FUNCTION" and token.function_name == "local":
            # Ignore local name here
            pass
        elif token.type == "S":
            # Ignore space
            pass
        else:
            if url:
                logger.debug("Ignoring URL without format(): {0}".format(url))
                url = None

            if token.type != "DELIM" or token.value != ",":
                logger.warn("CSS warning: Ignoring unexpected token {0}".format(token))

    return urls


def extract_font_downloads(fontfmt, rule):
    """Returns any font downloads for the specified format in the given CSS rule"""

    names = []
    urls = []

    for declaration in rule.declarations:
        if declaration.name == "src":
            names.extend(extract_font_names(declaration.value))
            urls.extend(extract_font_urls(fontfmt, declaration.value))

    if urls:
        if not names:
            name = urls[0].rsplit("/", 1)[-1].rsplit(".", 1)[0]
            logger.warn("No name found for {0}, using name from URL".format(urls[0]))
        else:
            name = choose_font_name(names)

        # Ensure urls are unique
        urls = set(urls)

        if len(urls) > 1:
            logger.warn("Ignoring additional URLs for same format: {0}".format(urls))

        fontfmt_ext = fontfmt_extensions[fontfmt]
        url = urls.pop()

        ext = urlparse.urlsplit(url).path.rsplit(".", 1)[-1]
        if "/" in ext:
            logger.debug("No extension for '{0}', using '{1}' from format".format(url, fontfmt_ext))
            ext = fontfmt_ext
        elif ext != fontfmt_ext:
            logger.warn("URL extension '{0}' does not match format extension '{1}'".format(ext, fontfmt_ext))

        downloads = [DownloadInfo(url=url, filename=name + "." + ext)]
    else:
        logger.warn("Ignoring @font-face without src")
        downloads = []

    return downloads


def fetch_fonts_from_css(fontfmt, stylesheet):
    """Downloads any fonts for the given format in the given CSS stylesheet"""

    downloads = []
    haveff = False
    for rule in stylesheet.rules:
        if rule.at_keyword == "@font-face":
            haveff = True
            downloads.extend(extract_font_downloads(fontfmt, rule))

    downloadcnt = 0
    if not haveff:
        logger.warn("No @font-face rules found in stylesheet")
    else:
        for download in downloads:
            if download_file(download.url, download.filename):
                downloadcnt += 1

    return downloadcnt


def make_css_path(subsets, fonts):
    """Returns the path to a CSS file for the given subsets and fonts"""

    url = "/css?family="

    families = []
    for font in fonts:
        family = font.family.replace(" ", "+")
        if font.variants:
            family += ":" + ",".join(font.variants)
        families.append(family)

    url += "|".join(families)

    if subsets:
        url += "&subset=" + ",".join(subsets)

    return url


def fetch_css(fontfmt, subsets, fonts):
    """Downloads CSS files with the given formats, subsets, and fonts"""

    path = make_css_path(subsets, fonts)
    user_agent = fontfmt_user_agent[fontfmt]
    headers = {
        "Accept": "text/css",
        "Accept-Encoding": "gzip",
        "Connection": "keep-alive",
        "User-Agent": user_agent,
    }

    logger.info("Downloading {0} for {1} format".format(path, fontfmt))

    conn = connection_pool.get("http", "fonts.googleapis.com")
    conn.request(method="GET", url=path, headers=headers)

    return conn.getresponse()


def parse_css(response):
    """Converts a CSS HTTPResponse into a tinycss stylesheet"""

    content_type = response.getheader("Content-Type", "text/css")
    css_charset_re = "text/css\s*;\s*charset\s*=\s*([^\s;]+)\s*(?:;|$)"
    css_charset_match = re.match(css_charset_re, content_type, re.I)
    charset = css_charset_match.group(1) if css_charset_match else None

    parser = tinycss.make_parser(CSSFontFace3Parser)

    cssdata = decode_response(response)

    logger.debug("Parsing CSS response with charset '{0}'".format(charset))

    return parser.parse_stylesheet_bytes(cssdata.read(), charset)


def fetch_fonts_format(fontfmt, subsets, fonts):
    """Downloads font files for a given format, subsets, and fonts"""
    response = fetch_css(fontfmt, subsets, fonts)
    if response.status != 200:
        logger.error("Server returned status {0} ({1}) for CSS file.  Incorrect font name?".format(
            response.status, response.reason))
        # Need to empty response before sending next request
        response.read()
        return 0

    stylesheet = parse_css(response)
    return fetch_fonts_from_css(fontfmt, stylesheet)


def fetch_fonts(fontfmts, subsets, fonts):
    """Downloads font files for the given formats, subsets, and fonts"""

    downloadcnt = 0
    for fontfmt in fontfmts:
        if fontfmt in fontfmt_serialize:
            for i in itertools.count():
                # A list of fonts with variant i of their list
                fonts1v = []
                for font in fonts:
                    # Note:  Include empty variant on first pass, if empty
                    if len(font.variants) > i or (i == 0 and len(font.variants) == 0):
                        fonts1v.append(font._replace(variants=font.variants[i:i + 1]))
                if not fonts1v:
                    # All variants of all fonts have been fetched
                    break

                downloadcnt += fetch_fonts_format(fontfmt, subsets, fonts1v)
        else:
            downloadcnt += fetch_fonts_format(fontfmt, subsets, fonts)

    return downloadcnt


def parse_font_arg(arg):
    """Parses a command-line argument into a FontArgument"""

    if ":" in arg:
        family, variants = arg.split(":", 1)

        if "," in variants:
            variants = variants.split(",")
        else:
            variants = [variants]

    else:
        family = arg
        variants = []

    return FontArgument(family=family, variants=variants)


def main(*argv):
    parser = argparse.ArgumentParser(description="Download Google Web Fonts")
    parser.add_argument(
        '-f', '--format', action="append", help="Format to download (may appear multiple times)",
        choices=sorted(fontfmt_user_agent.keys()))
    parser.add_argument(
        '-q', '--quiet', action="count", help="Decrease verbosity (make quieter)")
    parser.add_argument(
        '-s', '--subset', action="append", help="Subset to download (may appear multiple times)")
    parser.add_argument(
        '-v', '--verbose', action="count", help="Increase verbosity")
    parser.add_argument(
        '-V', '--version', action="version", version="%(prog)s " + ".".join(str(x) for x in VERSION))
    parser.add_argument(
        'font', nargs="+", help="Font to download (in same format as CSS URL)", type=parse_font_arg)
    args = parser.parse_args(args=argv[1:])

    # By default, download all formats
    if not args.format:
        args.format = fontfmt_user_agent.keys()

    # Set log level based on verbosity requested (default of INFO)
    verbosity = (args.quiet or 0) - (args.verbose or 0)
    logger.setLevel(logging.INFO + verbosity * 10)

    try:
        fetched = fetch_fonts(frozenset(args.format), args.subset, args.font)
        logger.info("Finished downloading {0} font files".format(fetched))
        return 0
    except Exception as e:
        logger.error("Unexpected internal error: {0}".format(str(e)), exc_info=True)
        return 1
    finally:
        try:
            connection_pool.close_all()
        except Exception as e:
            pass


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
