import time
import pyautogui
from pathlib import Path

SAVE_DIR = Path("recommender/screenshots")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

print("3초 뒤 현재 화면을 캡처합니다.")
print("TFT 화면을 띄워두세요.")

for i in range(3, 0, -1):
    print(i)
    time.sleep(1)

img = pyautogui.screenshot()
save_path = SAVE_DIR / "current_screen.png"
img.save(save_path)

print("스크린샷 저장 완료!")
print(save_path)