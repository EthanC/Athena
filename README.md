# Athena

Athena is a utility which generates the current Fortnite Item Shop into a stylized image and shares it on Twitter.

As seen on [@FNMasterCom](https://twitter.com/FNMasterCom/status/1144757522873671681)...

<img src="https://i.imgur.com/m138XR5.png" width="400px" draggable="false">

## Requirements

- [Python 3.7](https://www.python.org/downloads/)
- [Requests](http://docs.python-requests.org/en/master/user/install/)
- [(Colorama](https://pypi.org/project/colorama/)
- [Pillow](https://pillow.readthedocs.io/en/stable/installation.html#basic-installation)
- [python-twitter](https://github.com/bear/python-twitter#installing)

An [fnbr.co API Key](https://fnbr.co/api/docs) is required to obtain the Item Shop data, [Twitter API credentials](https://developer.twitter.com/en/apps) are required to Tweet the image.

## Usage

Open `configuration_example.json` in your preferred text editor, fill the configurable values. Once finished, save and rename the file to `configuration.json`.

- `delayStart`: Set to `0` to begin the process immediately
- `supportACreator`: Leave blank to omit the Support-A-Creator tag section of the Tweet
- `twitter`: Set `enabled` to `false` if you wish for `itemshop.png` to not be Tweeted

Edit the images found in `assets/images/` to your liking, avoid changing image dimensions for optimal results.

```
python itemshop.py
```

## Credits

- Item Shop data provided by the [fnbr.co](https://fnbr.co/) API
- Burbank font property of [Adobe](https://fonts.adobe.com/fonts/burbank)
- Luckiest Guy font property of [Google](https://fonts.google.com/specimen/Luckiest+Guy)
