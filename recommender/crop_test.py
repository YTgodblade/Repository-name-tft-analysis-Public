from PIL import Image, ImageDraw
from pathlib import Path

INPUT = "recommender/screenshots/current_screen.png"
OUT_DIR = Path("recommender/crops")
OUT_DIR.mkdir(parents=True, exist_ok=True)

img = Image.open(INPUT)
w, h = img.size

print("이미지 크기:", w, h)

# 1920x1080 기준 대략 좌표
regions = {
    "gold_area": (820, 955, 930, 1030),
    "level_area": (300, 930, 430, 1035),
    "hp_area": (1710, 230, 1810, 310),
}

for name, box in regions.items():
    crop = img.crop(box)
    crop.save(OUT_DIR / f"{name}.png")
    print(name, box)

# 확인용 박스 이미지
debug = img.copy()
draw = ImageDraw.Draw(debug)

for name, box in regions.items():
    draw.rectangle(box, outline="red", width=4)
    draw.text((box[0], box[1] - 20), name, fill="red")

debug.save(OUT_DIR / "debug_regions.png")

print("crop 완료!")
print("recommender/crops 폴더를 확인하세요.")