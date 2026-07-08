import cv2
from pathlib import Path

INPUT = "recommender/crops_team/team_area.png"
OUT_DIR = Path("recommender/detected_cards")
OUT_DIR.mkdir(parents=True, exist_ok=True)

img = cv2.imread(INPUT)
if img is None:
    raise FileNotFoundError(INPUT)

debug = img.copy()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 카드 테두리/밝은 부분 검출
blur = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blur, 50, 150)

contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

cards = []

for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)

    # 카드 크기 필터
    if 70 <= w <= 180 and 90 <= h <= 230:
        # 너무 위/아래 이상한 영역 제거
        if y > 20:
            cards.append((x, y, w, h))

# 비슷한 박스 중복 제거
cards = sorted(cards, key=lambda b: (b[1], b[0]))

filtered = []

for box in cards:
    x, y, w, h = box
    duplicate = False

    for fx, fy, fw, fh in filtered:
        if abs(x - fx) < 20 and abs(y - fy) < 20:
            duplicate = True
            break

    if not duplicate:
        filtered.append(box)

cards = filtered

# 위쪽 줄 → 아래쪽 줄, 왼쪽 → 오른쪽 정렬
cards = sorted(cards, key=lambda b: (b[1] // 80, b[0]))

print(f"감지된 카드 수: {len(cards)}")

for i, (x, y, w, h) in enumerate(cards, 1):
    card = img[y:y+h, x:x+w]
    save_path = OUT_DIR / f"card_{i:02d}.png"
    cv2.imwrite(str(save_path), card)

    cv2.rectangle(debug, (x, y), (x+w, y+h), (0, 0, 255), 3)
    cv2.putText(
        debug,
        str(i),
        (x, max(y - 8, 15)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2
    )

cv2.imwrite(str(OUT_DIR / "debug_detected_cards.png"), debug)

print("카드 검출 완료!")
print("저장 폴더:", OUT_DIR)