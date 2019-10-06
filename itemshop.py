import json
from math import ceil
from sys import exit
from time import sleep

import twitter
from PIL import Image, ImageDraw

from logger import Log
from util import ImageUtil, Utility


class Athena:
    """Fortnite Item Shop Generator."""

    def main(self):
        Log.Intro(self, "Athena - Fortnite Item Shop Generator")
        Log.Intro(self, "https://github.com/EthanC/Athena\n")

        initialized = Athena.LoadConfiguration(self)

        if initialized is True:
            if self.delay > 0:
                Log.Info(self, f"Delaying process start for {self.delay}s...")
                sleep(self.delay)

            itemShop = Utility.GET(self, "https://fn.notofficer.de/api/shop")

            if itemShop is not None:
                itemShop = json.loads(itemShop)

                # Strip time from the timestamp, we only need the date
                date = Utility.ISOtoHuman(self, itemShop["date"].split("T")[0])
                Log.Success(self, f"Retrieved Item Shop for {date}")

                shopImage = Athena.GenerateImage(self, date, itemShop)

                if shopImage is True:
                    if self.twitterEnabled is True:
                        Athena.Tweet(self, date)

    def LoadConfiguration(self):
        """
        Set the configuration values specified in configuration.json
        
        Return True if configuration sucessfully loaded.
        """

        configuration = json.loads(Utility.ReadFile(self, "configuration", "json"))

        try:
            self.delay = configuration["delayStart"]
            self.supportACreator = configuration["supportACreator"]
            self.twitterEnabled = configuration["twitter"]["enabled"]
            self.twitterAPIKey = configuration["twitter"]["apiKey"]
            self.twitterAPISecret = configuration["twitter"]["apiSecret"]
            self.twitterAccessToken = configuration["twitter"]["accessToken"]
            self.twitterAccessSecret = configuration["twitter"]["accessSecret"]

            Log.Success(self, "Loaded configuration")

            return True
        except Exception as e:
            Log.Error(self, f"Failed to load configuration, {e}")

    def GenerateImage(self, date: str, itemShop: dict):
        """
        Generate the Item Shop image using the provided Item Shop.

        Return True if image sucessfully saved.
        """

        try:
            featured = itemShop["featured"]
            daily = itemShop["daily"]

            # Ensure both Featured and Daily have at least 1 item
            if (len(featured) <= 0) or (len(daily) <= 0):
                raise Exception(f"Featured: {len(featured)}, Daily: {len(daily)}")
        except Exception as e:
            Log.Error(self, f"Failed to parse Item Shop Featured and Daily items, {e}")

            return False

        # Determine the max amount of rows required for the current
        # Item Shop when there are 3 columns for both Featured and Daily.
        # This allows us to determine the image height.
        rows = max(ceil(len(featured) / 3), ceil(len(daily) / 3))
        shopImage = Image.new("RGB", (1920, ((545 * rows) + 340)))

        try:
            background = ImageUtil.Open(self, "background.png")
            background = ImageUtil.RatioResize(
                self, background, shopImage.width, shopImage.height
            )
            shopImage.paste(
                background, ImageUtil.CenterX(self, background.width, shopImage.width)
            )
        except FileNotFoundError:
            Log.Warn(self, "Failed to open background.png, defaulting to dark gray")
            shopImage.paste((18, 18, 18), [0, 0, shopImage.size[0], shopImage.size[1]])

        logo = ImageUtil.Open(self, "logo.png")
        logo = ImageUtil.RatioResize(self, logo, 0, 210)
        shopImage.paste(
            logo, ImageUtil.CenterX(self, logo.width, shopImage.width, 20), logo
        )

        canvas = ImageDraw.Draw(shopImage)
        font = ImageUtil.Font(self, 48)
        textWidth, _ = font.getsize(date)
        canvas.text(
            ImageUtil.CenterX(self, textWidth, shopImage.width, 255),
            date,
            (255, 255, 255),
            font=font,
        )
        canvas.text((20, 255), "Featured", (255, 255, 255), font=font)
        textWidth, _ = font.getsize("Daily")
        canvas.text(
            (shopImage.width - (textWidth + 20), 255),
            "Daily",
            (255, 255, 255),
            font=font,
        )

        # Track grid position
        i = 0

        for item in featured:
            card = Athena.GenerateCard(self, item)

            if card is not None:
                shopImage.paste(
                    card,
                    (
                        (20 + ((i % 3) * (card.width + 5))),
                        (315 + ((i // 3) * (card.height + 5))),
                    ),
                    card,
                )

                i += 1

        # Reset grid position
        i = 0

        for item in daily:
            card = Athena.GenerateCard(self, item)

            if card is not None:
                shopImage.paste(
                    card,
                    (
                        (990 + ((i % 3) * (card.width + 5))),
                        (315 + ((i // 3) * (card.height + 5))),
                    ),
                    card,
                )

                i += 1

        try:
            shopImage.save("itemshop.png")
            Log.Success(self, "Generated Item Shop image")

            return True
        except Exception as e:
            Log.Error(self, f"Failed to save Item Shop image, {e}")

    def GenerateCard(self, item: dict):
        """Return the card image for the provided Fortnite Item Shop item."""

        try:
            name = item["items"][0]["name"]
            rarity = item["items"][0]["rarity"]
            category = item["items"][0]["type"]
            price = str(item["finalPrice"])
            if (category == "Outfit") or (category == "Wrap"):
                if item["items"][0]["images"]["featured"] is not None:
                    icon = item["items"][0]["images"]["featured"]["url"]
                else:
                    icon = item["items"][0]["images"]["icon"]["url"]
            else:
                icon = item["items"][0]["images"]["icon"]["url"]
        except Exception as e:
            Log.Error(self, f"Failed to parse item {name}, {e}")

            return

        if rarity == "Common":
            blendColor = (190, 190, 190)
        elif rarity == "Uncommon":
            blendColor = (96, 170, 58)
        elif rarity == "Rare":
            blendColor = (73, 172, 242)
        elif rarity == "Epic":
            blendColor = (177, 91, 226)
        elif rarity == "Legendary":
            blendColor = (211, 120, 65)
        elif rarity == "Marvel":
            blendColor = (197, 51, 52)
        elif rarity == "Dark":
            blendColor = (251, 34, 223)
        elif rarity == "DC":
            blendColor = (84, 117, 199)
        else:
            blendColor = (255, 255, 255)

        card = Image.new("RGBA", (300, 545))

        try:
            layer = ImageUtil.Open(self, f"card_top_{rarity.lower()}.png")
        except FileNotFoundError:
            Log.Warn(
                self,
                f"Failed to open card_top_{rarity.lower()}.png, defaulted to Common",
            )
            layer = ImageUtil.Open(self, "card_top_common.png")

        card.paste(layer)

        icon = ImageUtil.Download(self, icon)
        icon = ImageUtil.RatioResize(self, icon, 285, 365)
        card.paste(icon, ImageUtil.CenterX(self, icon.width, card.width), icon)

        if len(item["items"]) > 1:
            # Track grid position
            i = 0

            # Start at position 1 in items array
            for extra in item["items"][1:]:
                try:
                    extraRarity = extra["rarity"]
                    extraIcon = extra["images"]["smallIcon"]["url"]
                except Exception as e:
                    Log.Error(self, f"Failed to parse item {name}, {e}")

                    return

                try:
                    layer = ImageUtil.Open(
                        self, f"box_bottom_{extraRarity.lower()}.png"
                    )
                except FileNotFoundError:
                    Log.Warn(
                        self,
                        f"Failed to open box_bottom_{extraRarity.lower()}.png, defaulted to Common",
                    )
                    layer = ImageUtil.Open(self, "box_bottom_common.png")

                card.paste(layer, (17, (17 + ((i // 1) * (layer.height)))))

                extraIcon = ImageUtil.Download(self, extraIcon)
                extraIcon = ImageUtil.RatioResize(self, extraIcon, 75, 75)

                card.paste(
                    extraIcon, (17, (17 + ((i // 1) * (extraIcon.height)))), extraIcon
                )

                try:
                    layer = ImageUtil.Open(
                        self, f"box_faceplate_{extraRarity.lower()}.png"
                    )
                except FileNotFoundError:
                    Log.Warn(
                        self,
                        f"Failed to open box_faceplate_{extraRarity.lower()}.png, defaulted to Common",
                    )
                    layer = ImageUtil.Open(self, "box_faceplate_common.png")

                card.paste(layer, (17, (17 + ((i // 1) * (layer.height)))), layer)

                i += 1

        try:
            layer = ImageUtil.Open(self, f"card_faceplate_{rarity.lower()}.png")
        except FileNotFoundError:
            Log.Warn(
                self,
                f"Failed to open card_faceplate_{rarity.lower()}.png, defaulted to Common",
            )
            layer = ImageUtil.Open(self, "card_faceplate_common.png")

        card.paste(layer, layer)

        try:
            layer = ImageUtil.Open(self, f"card_bottom_{rarity.lower()}.png")
        except FileNotFoundError:
            Log.Warn(
                self,
                f"Failed to open card_bottom_{rarity.lower()}.png, defaulted to Common",
            )
            layer = ImageUtil.Open(self, "card_bottom_common.png")

        card.paste(layer, layer)

        canvas = ImageDraw.Draw(card)

        font = ImageUtil.Font(self, 30)
        textWidth, _ = font.getsize(f"{rarity} {category}")
        canvas.text(
            ImageUtil.CenterX(self, textWidth, card.width, 385),
            f"{rarity} {category}",
            blendColor,
            font=font,
        )

        vbucks = ImageUtil.Open(self, "vbucks.png")
        vbucks = ImageUtil.RatioResize(self, vbucks, 25, 25)

        textWidth, _ = font.getsize(price)
        canvas.text(
            ImageUtil.CenterX(self, ((textWidth - 5) - vbucks.width), card.width, 495),
            price,
            (255, 255, 255),
            font=font,
        )

        card.paste(
            vbucks,
            ImageUtil.CenterX(self, (vbucks.width + (textWidth + 5)), card.width, 495),
            vbucks,
        )

        font = ImageUtil.Font(self, 56)
        textWidth, _ = font.getsize(name)
        if textWidth >= 270:
            # Ensure that the item name does not overflow
            font, textWidth = ImageUtil.FitTextX(self, name, 56, 265)
        canvas.text(
            ImageUtil.CenterX(self, textWidth, card.width, 425),
            name,
            (255, 255, 255),
            font=font,
        )

        return card

    def Tweet(self, date: str):
        """
        Tweet the current `itemshop.png` local file to Twitter using the credentials provided
        in `configuration.json`.
        """

        try:
            twitterAPI = twitter.Api(
                consumer_key=self.twitterAPIKey,
                consumer_secret=self.twitterAPISecret,
                access_token_key=self.twitterAccessToken,
                access_token_secret=self.twitterAccessSecret,
            )

            twitterAPI.VerifyCredentials()
        except Exception as e:
            Log.Error(self, f"Failed to authenticate with Twitter, {e}")

            return

        body = f"#Fortnite Item Shop for {date}"

        if self.supportACreator is not None:
            body = f"{body}\n\nSupport-a-Creator Code: {self.supportACreator}"

        try:
            with open("itemshop.png", "rb") as shopImage:
                twitterAPI.PostUpdate(body, media=shopImage)

            Log.Success(self, "Tweeted Item Shop")
        except Exception as e:
            Log.Error(self, f"Failed to Tweet Item Shop, {e}")


if __name__ == "__main__":
    try:
        Athena.main(Athena)
    except KeyboardInterrupt:
        Log.Info(Athena, "Exiting...")
        exit()
