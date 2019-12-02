import json
import locale
import logging
from datetime import datetime

import requests
from PIL import Image, ImageFont

log = logging.getLogger(__name__)


class Utility:
    """Class containing utilitarian functions intended to reduce duplicate code."""

    def GET(self, url: str, headers: dict, parameters: dict = {"language": "en"}):
        """
        Return the response of a successful HTTP GET request to the specified
        URL with the optionally provided header values.
        """

        res = requests.get(url, headers=headers, params=parameters)

        # HTTP 200 (OK)
        if res.status_code == 200:
            return res.text
        else:
            log.critical(f"Failed to GET {url} (HTTP {res.status_code})")

    def nowISO(self):
        """Return the current utc time in ISO8601 timestamp format."""

        return datetime.utcnow().isoformat()

    def ISOtoHuman(self, date: str, language: str):
        """Return the provided ISO8601 timestamp in human-readable format."""

        try:
            locale.setlocale(locale.LC_ALL, language)
        except locale.Error:
            log.warn(f"Unsupported locale configured, using system default")

        try:
            # Unix-supported zero padding removal
            return datetime.strptime(date, "%Y-%m-%d").strftime("%A, %B %-d, %Y")
        except ValueError:
            try:
                # Windows-supported zero padding removal
                return datetime.strptime(date, "%Y-%m-%d").strftime("%A, %B %#d, %Y")
            except Exception as e:
                log.error(self, f"Failed to convert to human-readable time, {e}")

    def ReadFile(self, filename: str, extension: str, directory: str = ""):
        """
        Read and return the contents of the specified file.

        Optionally specify a relative directory.
        """

        try:
            with open(
                f"{directory}{filename}.{extension}", "r", encoding="utf-8"
            ) as file:
                return file.read()
        except Exception as e:
            log.critical(f"Failed to read {filename}.{extension}, {e}")


class ImageUtil:
    """Class containing utilitarian image-based functions intended to reduce duplicate code."""

    def Open(self, filename: str, directory: str = "assets/images/"):
        """Return the specified image file."""

        return Image.open(f"{directory}{filename}")

    def Download(self, url: str):
        """Download and return the raw file from the specified url as an image object."""

        res = requests.get(url, stream=True)

        # HTTP 200 (OK)
        if res.status_code == 200:
            return Image.open(res.raw)
        else:
            log.critical(f"Failed to GET {url} (HTTP {res.status_code})")

    def RatioResize(self, image: Image.Image, maxWidth: int, maxHeight: int):
        """Resize and return the provided image while maintaining aspect ratio."""

        ratio = max(maxWidth / image.width, maxHeight / image.height)

        return image.resize(
            (int(image.width * ratio), int(image.height * ratio)), Image.ANTIALIAS
        )

    def CenterX(self, foregroundWidth: int, backgroundWidth: int, distanceTop: int = 0):
        """Return the tuple necessary for horizontal centering and an optional vertical distance."""

        return (int(backgroundWidth / 2) - int(foregroundWidth / 2), distanceTop)

    def Font(
        self,
        size: int,
        font: str = "BurbankBigCondensed-Black.otf",
        directory: str = "assets/fonts/",
    ):
        """Return a font object with the specified font file and size."""

        try:
            return ImageFont.truetype(f"{directory}{font}", size)
        except OSError:
            log.warn(
                "BurbankBigCondensed-Black.otf not found, defaulted font to LuckiestGuy-Regular.ttf"
            )

            return ImageFont.truetype(f"{directory}LuckiestGuy-Regular.ttf", size)
        except Exception as e:
            log.error(f"Failed to load font, {e}")

    def FitTextX(
        self,
        text: str,
        size: int,
        maxSize: int,
        font: str = "BurbankBigCondensed-Black.otf",
    ):
        """Return the font and width which fits the provided text within the specified maxiumum width."""

        font = ImageUtil.Font(self, size)
        textWidth, _ = font.getsize(text)
        change = 0

        while textWidth >= maxSize:
            change += 1
            size -= 1
            font = ImageUtil.Font(self, size)
            textWidth, _ = font.getsize(text)

        return ImageUtil.Font(self, size), textWidth, change
