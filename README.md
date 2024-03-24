# Signal Desktop GIF

Paste GIFs into Signal Desktop with a single global keyboard shortcut.

Tested on Windows and MacOS. Needs testing on Linux.

## Usage

1. Copy a GIF url to your clipboard.
2. (Only on Windows and Linux) Have your Signal Desktop conversation open and focused.
3. Press `Ctrl + g` to paste the GIF into Signal Desktop.

## Installation

Install [`signal-desktop-gif` from PyPI](https://pypi.org/project/signal-desktop-gif/) using any tool you like, e.g. `pip` or [`pipx`](https://pipx.pypa.io/stable/).

You could also just install using `rye`, see the [Development](#development) section below.

```bash
pip install signal-desktop-gif
```

Run the script with `signal-desktop-gif`:

```bash
signal-desktop-gif
```

## Development

1. Install [rye](https://rye-up.com/guide/installation/).
2. Clone this repo and run `rye sync` in its root.
3. `rye run signal-desktop-gif`

## Configuration

TODO.
For now, you have to edit the source code and change the various `GLOBAL_CONFIG_VARIABLES` (including shortcuts) in the [script](./src/signal_desktop_gif/__init__.py).

## Known Issues

- Shortcuts and other [options are not configurable yet](#configuration).
- Quitting on Windows is buggy, you can use `Ctrl + Shift + e` to exit the script if `Ctrl + c` doesn't work.

## Links

- <https://github.com/signalapp/Signal-Desktop/issues/4841>
- Thanks to [this Reddit post](https://www.reddit.com/r/signal/comments/180hm37/desktop_and_gifs/) for pointing out that HTTP URLs can be pasted directly into Signal Desktop (well, at least on Windows and Linux, MacOS doesn't support this).
