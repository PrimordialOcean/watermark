from PIL import Image, ExifTags, ImageDraw, ImageFont
from fractions import Fraction
import glob
import os

def get_exif(filepath: str) -> dict:
    """Get Exif of images if exists.
    Args:
        filepath (str): 画像のファイルパス
    Retrurns:
        dict: Exifデータを格納した辞書
    """
    im = Image.open(filepath)
    try:
        exif = im._getexif()
    except AttributeError:
        return {}
    
    exif_table = {}
    for tag_id, value in exif.items():
        tag = ExifTags.TAGS.get(tag_id, tag_id)
        exif_table[tag] = value
    
    return exif_table

def make_text(exif_table: dict) -> str:
    """Extract texts from Exif table.
    Args:
        exif_table (dict): Exifデータを格納した辞書
    Returns:
        text (str): watermarkとして画像に記入する文字列
    """

    camera = exif_table["Model"].strip()
    lens = exif_table["LensModel"].strip("\x00")
    focal = exif_table["FocalLength"]
    iso = exif_table["ISOSpeedRatings"]
    exposure = exif_table["ExposureTime"]
    if exposure < 1:
        ss = Fraction(exposure)
    else:
        ss = exposure
    fn = exif_table["FNumber"]
    artist = exif_table["Artist"].strip()
    date = exif_table["DateTimeOriginal"]
    watermark = f"{camera}, {str(lens)}, {int(focal)}mm, F{fn}, {ss}sec, ISO{iso}, Photo by {artist} @ {date}"
    return watermark

def main():
    filepathlist = glob.glob("*.jpg")
    for filepath in filepathlist:
        exif_table = get_exif(filepath)
        watermark = make_text(exif_table)
        print(watermark)
        opacity = 70
        base = Image.open(filepath).convert("RGBA")
        txt = Image.new("RGBA", base.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)
        fnt = ImageFont.truetype(font="arial.ttf", size=72)
        textw, texth = draw.textsize(watermark, font=fnt)
        draw.text((50, base.height - texth - 20), watermark, font=fnt, fill = (255, 255, 255) + (opacity,))
        out = Image.alpha_composite(base, txt).convert("RGB")
        if not os.path.exists("output"):
            os.makedirs("output")
        out.save(f"output/s-{filepath}.jpg", quality=80)


if __name__ == "__main__":
    main()
