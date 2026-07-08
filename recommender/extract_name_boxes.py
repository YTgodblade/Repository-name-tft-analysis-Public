from PIL import Image, ImageDraw
from pathlib import Path

INPUT = "recommender/crops_team/team_area.png"
OUT_DIR = Path("recommender/name_boxes")
OUT_DIR.mkdir(parents=True, exist_ok=True)

img = Image.open(INPUT)
w, h = img.size

print("team_area 크기:", w, h)

# team_area.png 기준 좌표
# 카드 배치가 안 맞으면 아래 숫자만 수정하면 됨
start_x = 20
start_y = 115

card_w = 125
card_h = 150

gap_x = 20
gap_y = 40

cols = 5
rows = 2

# 카드 안에서 이름이 있는 아래쪽 영역
name_y1_offset = 115
name_y2_offset = 148

debug = img.copy()
draw = ImageDraw.Draw(debug)

count = 1

for r in range(rows):
    for c in range(cols):
        card_x1 = start_x + c * (card_w + gap_x)
        card_y1 = start_y + r * (card_h + gap_y)
        card_x2 = card_x1 + card_w
        card_y2 = card_y1 + card_h

        name_box = (
            card_x1,
            card_y1 + name_y1_offset,
            card_x2,
            card_y1 + name_y2_offset,
        )

        crop = img.crop(name_box)
        crop.save(OUT_DIR / f"name_{count:02d}.png")

        draw.rectangle(name_box, outline="red", width=3)
        draw.text((name_box[0], name_box[1] - 15), str(count), fill="red")

        count += 1

debug.save(OUT_DIR / "debug_name_boxes.png")

print("이름 영역 crop 완료!")
print("저장 폴더:", OUT_DIR)