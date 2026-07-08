from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import pytesseract
import re
import pandas as pd
from difflib import get_close_matches

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

INPUT = "recommender/crops_team/team_area.png"
OUT_DIR = Path("recommender/ocr_names")
OUT_DIR.mkdir(parents=True, exist_ok=True)

df_units = pd.read_csv("unit_tier_kr.csv")
UNIT_NAMES = df_units["unit_kr"].dropna().astype(str).tolist()

img = Image.open(INPUT)
w, h = img.size

print("team_area 크기:", w, h)

# team_area.png 기준 좌표
start_x = 15
start_y = 18

card_w = 130
card_h = 185

gap_x = 28
gap_y = 30

cols = 5
rows = 2

# 이름 영역
name_y1_offset = 148
name_y2_offset = 183

def preprocess(crop):
    crop = crop.resize((crop.width * 5, crop.height * 5))
    crop = crop.convert("L")
    crop = ImageEnhance.Contrast(crop).enhance(3.0)
    crop = crop.filter(ImageFilter.SHARPEN)
    return crop

def clean_text(text):
    text = text.strip()
    text = text.replace("\n", "")
    text = text.replace(" ", "")
    text = re.sub(r"[^가-힣A-Za-z]", "", text)
    return text

def fix_name(text):
    if not text:
        return ""

    if text in UNIT_NAMES:
        return text

    matches = get_close_matches(text, UNIT_NAMES, n=1, cutoff=0.35)

    if matches:
        return matches[0]

    return text

debug = img.copy()
draw = ImageDraw.Draw(debug)

names = []
count = 1

for r in range(rows):
    for c in range(cols):
        card_x1 = start_x + c * (card_w + gap_x)
        card_y1 = start_y + r * (card_h + gap_y)

        name_box = (
            card_x1,
            card_y1 + name_y1_offset,
            card_x1 + card_w,
            card_y1 + name_y2_offset,
        )

        crop = img.crop(name_box)
        crop.save(OUT_DIR / f"raw_name_{count:02d}.png")

        processed = preprocess(crop)
        processed.save(OUT_DIR / f"processed_name_{count:02d}.png")

        text = pytesseract.image_to_string(
            processed,
            lang="kor+eng",
            config="--psm 7"
        )

        clean = clean_text(text)
        fixed = fix_name(clean)

        if fixed:
            names.append(fixed)

        draw.rectangle(name_box, outline="red", width=3)
        draw.text((name_box[0], name_box[1] - 15), str(count), fill="red")

        print(f"{count}: OCR='{clean}' → 보정='{fixed}'")

        count += 1

debug.save(OUT_DIR / "debug_ocr_boxes.png")

# 중복 제거
names = list(dict.fromkeys(names))

print("\n인식된 기물:")
print(names)
print("\n디버그 이미지:")
print(OUT_DIR / "debug_ocr_boxes.png")