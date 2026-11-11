"""Apply Chaibao's updated body and resting poses to the existing v2 atlas."""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PET = ROOT / "assets/pet"


def cutouts(name, count, width):
    strip = Image.open(ROOT / f"assets/source/{name}.png").convert("RGBA")
    frames = []
    for index in range(count):
        part = strip.crop((strip.width * index // count, 0,
                           strip.width * (index + 1) // count, strip.height))
        alpha = part.getchannel("A")
        part = part.crop(alpha.point(lambda a: 255 if a > 18 else 0).getbbox())
        frames.append(part)
    scale = width / max(part.width for part in frames)
    for part in frames:
        part = part.resize((round(part.width * scale), round(part.height * scale)),
                           Image.Resampling.LANCZOS)
        cell = Image.new("RGBA", (192, 208))
        cell.alpha_composite(part, ((192 - part.width) // 2, 201 - part.height))
        yield cell


def main():
    path = PET / "spritesheet.png"
    sheet = Image.open(path).convert("RGBA")
    walk = list(cutouts("walk", 4, 174))
    for i, cell in enumerate(walk * 2):
        sheet.paste(cell, (192 * i, 208))
        sheet.paste(ImageOps.mirror(cell), (192 * i, 416))
    for i in range(5):
        sheet.paste(sheet.crop((192*i, 0, 192*(i+1), 208)), (192*i, 832))
    for name, cell in zip(("loaf", "sleep"), cutouts("rest", 2, 155)):
        cell.save(PET / f"{name}.png")
    sheet.save(path)


if __name__ == "__main__":
    main()

