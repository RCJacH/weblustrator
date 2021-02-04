# Weblustrator

## Introduction

There are few workflow-related features missing from illustration applications on the current market.
For example, global variables, allowing the alternation of object attributes across layers or even files; dynamic resizing, changing the size of an object based on the size of parent layer or the canvas; and version controls, with branching and submodules.

All of those can be done with web technologies, such as html, CSS, and SVG. It's unfortunately that they are neglected outside of building websites or web applications.

Weblustrator attempts to tackle this problem by providing tools for designers to create rasterization more easily and more accurately.
One for previewing design projects in browser with live reload, another to render the result into a rasterized file format such as png.

## Installation

Weblustrator requires the installation of [Python 3.8+](https://python.org).
Earlier versions are not tested yet.

After python is installed, get this package through pip

`pip install weblustrator`

## How to use

### Server

The Weblustrator server is for previewing.

In a shell window or using a task in vscode or other editors, `cd` into your project directory, and run `weblustrator serve` to start the server.

The default address for the server is `localhost:5500`.
This page lists all files under the directory with accepted file formats.
Clicking on any of the links to visit the target page.

Now you can edit the corresponding file, and the result of the edit will be displayed in the browser.

### Render

When you are done editing, you can render the target file with the command `weblustrator render <path/of/the/file>`.
The `<path/of/the/file>` can be relative, meaning everything after `localhost:5500/`.
After chromium opens and closes for a screencap, the result will be saved to the same directory as `<filename>.png`.

### Command Line Options

- Host IP and port can be altered with `--host` and `--port` options, for example, `weblustrator serve --host 0.0.0.0 --port 8080` will locate the server at `0.0.0.0:8080`. A matching setting must be used for the rendering.
- A `-p` or `--path` option is available to change the project location from your current shell directory.
- `--width` and `--height` options can be used to change the viewport, or the canvas size for the rendering process.
- Multiple inputs are allow rendering, input string are [glob patterns](https://en.wikipedia.org/wiki/Glob_%28programming%29).
