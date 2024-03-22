"""
Signal Desktop currently does not support copy-pasting gifs from the clipboard
    (it results in static images being pasted).

This script downloads the gif using an URL in the clipboard and pastes it to the Signal desktop app as an attachment,
    resulting in the gif being shared as intended.

To be able to use this script, you need to have a gif URL in your clipboard.

If AUTOMATICALLY_SEND_MESSAGE is set to True, the message will be _sent_ automatically after the gif is pasted.
    Otherwise, you will need to press Enter to send the message.

Signal is even automatically opened/switched to, iff AUTOMATICALLY_OPEN_SIGNAL is set to True.
    However, this currently only works on MacOS. Disable AUTOMATICALLY_OPEN_SIGNAL if you are not using MacOS.
    You have to have Signal focused for the script to work if AUTOMATICALLY_OPEN_SIGNAL is set to False.
"""

import os
import time
from functools import cache
from pathlib import Path

import httpx
import platformdirs
import pyautogui
import pyperclip
from loguru import logger
from pynput import keyboard

ALLOWED_EXTENSIONS = {
	".gif",
	".webp",
}
AUTOMATICALLY_OPEN_SIGNAL = True
AUTOMATICALLY_SEND_MESSAGE = True
HOTKEY = "<ctrl>+g"
SECONDS_TO_HOLD_MULTIPLE_KEYS = 0.1
SECONDS_TO_SLEEP_AFTER_ACTION = 1.0

KEYBOARD_CONTROLLER = keyboard.Controller()


def fmt_bytes_to_mb(num_bytes: int):
	return f"{num_bytes / 1024 / 1024:.2f} MB"


@cache
def get_base_dir() -> Path:
	dir = Path(platformdirs.user_cache_dir(appname="signal_desktop_gif"))
	dir.mkdir(parents=True, exist_ok=True)
	logger.info(f"Using base cache directory: {dir}")
	files = list(dir.iterdir())
	logger.info(f"Current files {len(files):_}, total size: {fmt_bytes_to_mb(sum(f.stat().st_size for f in files))}.")
	return dir


def url_to_path_name(url: httpx.URL) -> str:
	# @TODO: consider using more than a path, if it's ever needed
	return url.path.lstrip("/").replace("/", "_").replace("\\", "_")


def get_url_from_clipboard() -> httpx.URL | None:
	clipboard = pyperclip.paste().strip()
	logger.info(f"Clipboard content: '{clipboard}'")
	try:
		gif_url = httpx.URL(clipboard)
		return gif_url
	except httpx.InvalidURL:
		logger.error(f"The clipboard does not contain a valid URL: {clipboard}")
		return None


def download_gif(gif_url: httpx.URL) -> Path | None:
	"""Downloads the (gif) url to a temp folder and returns the path to the (gif) file."""

	# Check if the (gif) file already exists
	gif_file_name = url_to_path_name(gif_url)
	gif_file_path = get_base_dir() / gif_file_name
	if gif_file_path.exists() and (file_size := gif_file_path.stat().st_size) > 0:
		logger.success(f"The gif file already exists and is not empty: {fmt_bytes_to_mb(file_size)}, {gif_file_path}")
		return gif_file_path

	# Check if the (gif) file extension is allowed
	if gif_file_path.suffix not in ALLOWED_EXTENSIONS:
		logger.error(
			f"The '{gif_file_path.suffix}' file extension is not allowed, valid options are: {ALLOWED_EXTENSIONS}"
		)
		return None

	# Download the (gif) url
	try:
		logger.info(f"Downloading the gif from {gif_url}")
		r = httpx.get(gif_url, timeout=20)
	except Exception as e:
		logger.error("Failed to download the gif:", e)
		return None
	logger.success(f"Gif downloaded successfully from {gif_url}, size: {fmt_bytes_to_mb(len(r.content))}.")

	# Write the gif to a cached file
	try:
		logger.info(f"Writing the gif to a file: {gif_file_path}")
		with open(gif_file_path, "wb") as f:
			f.write(r.content)
	except Exception as e:
		logger.error(f"Failed to write the gif to a file: {e}")
		return None
	logger.success(f"Gif downloaded successfully to {gif_file_path}")

	return gif_file_path


def paste_gif_to_signal(gif_path: Path):
	if AUTOMATICALLY_OPEN_SIGNAL:
		logger.info("Opening the Signal app.")
		os.system("open /Applications/Signal.app")
		time.sleep(SECONDS_TO_SLEEP_AFTER_ACTION)

	logger.info("Selecting message input textbox.")
	# https://github.com/signalapp/Signal-Desktop/issues/2706#issuecomment-854147859
	pyautogui.hotkey("command", "shift", "t", interval=SECONDS_TO_HOLD_MULTIPLE_KEYS)

	logger.info("Opening the file attachment dialog.")
	# a non-zero interval is needed to prevent the hotkey from being ignored (on MacOS)
	pyautogui.hotkey("command", "u", interval=SECONDS_TO_HOLD_MULTIPLE_KEYS)

	logger.info("Opening the path dialog.")
	# pyautogui.hotkey("command", "shift", "g", interval=SECONDS_TO_HOLD_MULTIPLE_KEYS)
	# this search works better on MacOS
	pyautogui.hotkey("/")
	time.sleep(SECONDS_TO_SLEEP_AFTER_ACTION)

	logger.info("Typing the gif path.")
	KEYBOARD_CONTROLLER.type(str(gif_path.resolve())[1:])  # the first slash is already there
	time.sleep(SECONDS_TO_SLEEP_AFTER_ACTION)

	# then, the first Enter enters the parent folder
	logger.info("Pressing enter to enter the gif path.")
	pyautogui.press("enter")
	time.sleep(SECONDS_TO_SLEEP_AFTER_ACTION)

	# and the second Enter selects the gif file
	logger.info("Pressing enter to insert the gif file.")
	pyautogui.press("enter")

	if AUTOMATICALLY_SEND_MESSAGE:
		time.sleep(SECONDS_TO_SLEEP_AFTER_ACTION)
		logger.info("Pressing enter to send the message.")
		pyautogui.press("enter")


def download_and_paste():
	gif_url = get_url_from_clipboard()
	gif_path = download_gif(gif_url)

	if gif_path is None:
		logger.error("Failed to download the gif, quitting.")
		return

	paste_gif_to_signal(gif_path)
	logger.success("Gif pasted successfully. Well, maybe. There's no way to check (:")


def main():
	# to just run once:
	# download_and_paste()

	# Show cache stats on startup
	get_base_dir()

	with keyboard.GlobalHotKeys({HOTKEY: download_and_paste}) as h:
		logger.success(f"Press {HOTKEY} to download and paste a gif when its URL is in the clipboard.")
		try:
			h.join()
		except KeyboardInterrupt:
			logger.success("kthxbyeee!")


if __name__ == "__main__":
	main()
