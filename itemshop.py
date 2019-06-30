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

            if self.fnbrAPIKey is not None:
                itemShop = Athena.GetItemShop(self, self.fnbrAPIKey)

                if itemShop is not None:
                    itemShop = json.loads(itemShop)

                    # Strip time from the timestamp, we only want the date
                    date = Utility.ISOtoHuman(
                        self, itemShop["data"]["date"].split("T")[0]
                    )
                    Log.Success(self, f"Retrieved Item Shop for {date}")

                    shopImage = Athena.GenerateImage(self, date, itemShop)

                    if shopImage is True:
                        Log.Success(self, "Generated Item Shop image")

                        if self.twitterEnabled is True:
                            tweeted = Athena.Tweet(self, date)

                            if tweeted is True:
                                Log.Success(self, "Tweeted Item Shop")

    def LoadConfiguration(self):
        """
        Set the configuration values specified in configuration.json
        
        Return True if configuration sucessfully loaded.
        """

        configuration = json.loads(Utility.ReadFile(self, "configuration", "json"))

        try:
            self.delay = configuration["delayStart"]
            self.supportACreator = configuration["supportACreator"]
            self.fnbrAPIKey = configuration["fnbr"]["apiKey"]
            self.twitterEnabled = configuration["twitter"]["enabled"]
            self.twitterAPIKey = configuration["twitter"]["apiKey"]
            self.twitterAPISecret = configuration["twitter"]["apiSecret"]
            self.twitterAccessToken = configuration["twitter"]["accessToken"]
            self.twitterAccessSecret = configuration["twitter"]["accessSecret"]

            Log.Success(self, "Loaded configuration")

            return True
        except Exception as e:
            Log.Error(self, f"Failed to load configuration, {e}")

    def GetItemShop(self, fnbrAPIKey: str):
        """Return the current Item Shop from the FNBR.co API."""

        url = "https://fnbr.co/api/shop"
        headers = {"x-api-key": fnbrAPIKey}

        return Utility.GET(self, url, headers=headers)

    def GenerateImage(self, date: str, itemShop: dict):
        """
        Generate the Item Shop image using the provided Item Shop.

        Return True if image sucessfully saved.
        """

        featured = itemShop["data"]["featured"]
        daily = itemShop["data"]["daily"]

        # Determine the max amount of rows for the current Item Shop, when
        # there are three columns for both featured and daily, so that we
        # can determine the height of the complete image.
        rows = max(ceil(len(featured) / 3), ceil(len(daily) / 3))

        shopImage = Image.new("RGB", (1920, ((545 * rows) + 470)))

        background = ImageUtil.Open(self, "background.png")
        background = ImageUtil.RatioResize(
            self, background, shopImage.width, shopImage.height
        )
        shopImage.paste(
            background, ImageUtil.CenterX(self, background.width, shopImage.width)
        )

        logo = ImageUtil.Open(self, "logo.png")
        shopImage.paste(
            logo, ImageUtil.CenterX(self, logo.width, shopImage.width, 20), logo
        )

        canvas = ImageDraw.Draw(shopImage)

        font = ImageUtil.Font(self, 56)

        textWidth, _ = font.getsize(date)
        canvas.text(
            ImageUtil.CenterX(self, textWidth, shopImage.width, 375),
            date,
            (255, 255, 255),
            font=font,
        )

        canvas.text((20, 375), "Featured", (255, 255, 255), font=font)

        textWidth, _ = font.getsize("Daily")
        canvas.text(
            (shopImage.width - (textWidth + 20), 375),
            "Daily",
            (255, 255, 255),
            font=font,
        )

        # Track which grid position we're at
        i = 0

        for item in featured:
            card = Athena.GenerateCard(self, item)

            if card is not None:
                shopImage.paste(
                    card,
                    ((20 + ((i % 3) * card.width)), (450 + ((i // 3) * card.height))),
                    card,
                )

                i = i + 1

        # Reset counter
        i = 0

        for item in daily:
            card = Athena.GenerateCard(self, item)

            if card is not None:
                shopImage.paste(
                    card,
                    ((1000 + ((i % 3) * card.width)), (450 + ((i // 3) * card.height))),
                    card,
                )
                
                i = i + 1

        try:
            shopImage.save("itemshop.png")

            return True
        except Exception as e:
            Log.Error(self, f"Failed to save Item Shop image, {e}")

    def GenerateCard(self, item: dict):
        """Return the card image for the provided Fortnite Item Shop item."""

        name = item["name"]
        rarity = item["rarity"]
        category = item["readableType"]
        price = item["price"]
        icon = item["images"]["featured"]
        if icon is False:
            icon = item["images"]["icon"]

        try:
            card = Image.new("RGBA", (300, 545))

            try:
                cardTop = ImageUtil.Open(self, f"card_top_{rarity}.png")
            except FileNotFoundError:
                # Default to Common if rarity does not exist
                cardTop = ImageUtil.Open(self, "card_top_common.png")
            card.paste(cardTop)

            icon = ImageUtil.Download(self, icon).convert("RGBA")
            icon = ImageUtil.RatioResize(self, icon, 275, 360)
            card.paste(icon, ImageUtil.CenterX(self, icon.width, card.width), icon)

            try:
                cardFaceplate = ImageUtil.Open(self, f"card_faceplate_{rarity}.png")
            except FileNotFoundError:
                # Default to Common if rarity does not exist
                cardFaceplate = ImageUtil.Open(self, "card_faceplate_common.png")
            card.paste(cardFaceplate, cardFaceplate)

            try:
                cardBottom = ImageUtil.Open(self, f"card_bottom_{rarity}.png")
            except FileNotFoundError:
                # Default to Common if rarity does not exist
                cardBottom = ImageUtil.Open(self, "card_bottom_common.png")
            card.paste(cardBottom, cardBottom)

            canvas = ImageDraw.Draw(card)

            font = ImageUtil.Font(self, 56)

            textWidth, _ = font.getsize(name)

            # Ensure that the item name does not overflow
            if textWidth >= 270:
                font, textWidth = ImageUtil.FitTextX(self, name, 56, 265)

            canvas.text(
                ImageUtil.CenterX(self, textWidth, card.width, 395),
                name,
                (255, 255, 255),
                font=font,
            )

            font = ImageUtil.Font(self, 25)

            textWidth, _ = font.getsize(f"{rarity.capitalize()} {category}")
            canvas.text(
                ImageUtil.CenterX(self, textWidth, card.width, 460),
                f"{rarity.capitalize()} {category}",
                (255, 255, 255),
                font=font,
            )

            textWidth, _ = font.getsize(price)
            canvas.text(
                ImageUtil.CenterX(self, textWidth, card.width, 500),
                price,
                (255, 255, 255),
                font=font,
            )

            vbucks = ImageUtil.Open(self, "vbucks.png")
            vbucks = vbucks.resize((20, 20))
            card.paste(
                vbucks,
                ImageUtil.CenterX(self, textWidth, (card.width - 50), 500),
                vbucks,
            )

            return card
        except Exception as e:
            Log.Error(self, f"Failed to generate card for item {name}, {e}")

    def Tweet(self, date: str):
        """
        Tweet the current `itemshop.png` local file to Twitter using the credentials provided in `configuration.json`.
        
        Return True is the Tweet was successfully posted.
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

        body = f"#Fortnite Item Shop for {date} (via fnbr.co)"

        if self.supportACreator is not None:
            tag = f"Support-A-Creator tag: {self.supportACreator}"
            body = f"{body}\n\n{tag}"

        try:
            with open("itemshop.png", "rb") as shopImage:
                twitterAPI.PostUpdate(body, media=shopImage)

            return True
        except Exception as e:
            Log.Error(self, f"Failed to Tweet Item Shop, {e}")


if __name__ == "__main__":
    try:
        Athena.main(Athena)
    except KeyboardInterrupt:
        Log.Info(Athena, "Exiting...")
        exit()
