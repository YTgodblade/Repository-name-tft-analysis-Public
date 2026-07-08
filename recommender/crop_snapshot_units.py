from PIL import Image, ImageDraw
from pathlib import Path

INPUT = "recommender/screenshots/current_screen.png"
OUT_DIR = Path("recommender/crops_snapshot_units")
OUT_DIR.mkdir(parents=True, exist_ok=True)

img = Image.open(INPUT)
w, h = img.size

print("이미지 크기:", w, h)

# 일단 1920x1080 기준 대략 좌표
# 안 맞으면 debug_units.png 보고 수정
start_x = 430
start_y = 120

card_w = 130
card_h = 170

gap_x = 18
gap_y = 22

cols = 7
rows = 3

debug = img.copy()
draw = ImageDraw.Draw(debug)

count = 1

for r in range(rows):
    for c in range(cols):
        x1 = start_x + c * (card_w + gap_x)
        y1 = start_y + r * (card_h + gap_y)
        x2 = x1 + card_w
        y2 = y1 + card_h

        box = (x1, y1, x2, y2)

        crop = img.crop(box)
        crop.save(OUT_DIR / f"unit_slot_{count:02d}.png")

        draw.rectangle(box, outline="red", width=4)
        draw.text((x1, y1 - 18), f"{count}", fill="red")

        count += 1

debug.save(OUT_DIR / "debug_units.png")

print("기물 칸 crop 완료!")
print("저장 폴더:", OUT_DIR)