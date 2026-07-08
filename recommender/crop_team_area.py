from PIL import Image, ImageDraw
from pathlib import Path

INPUT = "recommender/screenshots/current_screen.png"
OUT_DIR = Path("recommender/crops_team")
OUT_DIR.mkdir(parents=True, exist_ok=True)

img = Image.open(INPUT)
w, h = img.size

print("이미지 크기:", w, h)

# 네가 올린 1920x1080 스냅샷 기준
team_area = (900, 250, 1720, 720)

crop = img.crop(team_area)
crop.save(OUT_DIR / "team_area.png")

debug = img.copy()
draw = ImageDraw.Draw(debug)
draw.rectangle(team_area, outline="red", width=5)
draw.text((team_area[0], team_area[1] - 25), "team_area", fill="red")

debug.save(OUT_DIR / "debug_team_area.png")

print("완료!")
print("저장 폴더:", OUT_DIR)