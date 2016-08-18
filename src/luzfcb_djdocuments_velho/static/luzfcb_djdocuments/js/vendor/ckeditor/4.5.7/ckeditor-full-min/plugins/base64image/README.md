Base64Image Plugin for CKEditor 4
=================================

Created by ALL-INKL.COM - Neue Medien Münnich - 04. Feb 2014

Adapted by Contractual.ly - March 2014.

Adds images from local client as base64 string into the source without server
side processing. You can also add external image urls into the source.

## Requirements
The Browser must support the JavaScript File API.

## Installation

 1. Download the plugin from https://github.com/85x14/base64image
 
 2. Extract (decompress) the downloaded file into the plugins folder of your
	CKEditor installation.
	Example: http://example.com/ckeditor/plugins/base64image
	
 3. Enable the plugin by using the extraPlugins configuration setting.
	Example: CKEDITOR.config.extraPlugins = "base64image";

## Configuration

Optionally add `config.base64image_disableUrlImages = true;` to your CKEditor config to disable the option to add
external image URLs.