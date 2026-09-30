# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cv2
import config_loader
import db
from recognizer import Recognizer

cfg = config_loader.load_config(os.path.join(HERE, "config.ini"))
config_map = db.load_database(os.path.join(HERE, cfg["db_file"]))
print("roles:", len(config_map))

rec = Recognizer(cfg, config_map)

root = r"Y:\Fairytale\Fish\BattleTreerecognizer"
for path, label in [
    (os.path.join(root, "screenshot_color.png"), "normal"),
    (os.path.join(root, "screenshot_color_elec.png"), "elec"),
]:
    img = cv2.imread(path)
    img = cv2.copyMakeBorder(img, 60, 60, 60, 60, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    print(f"\n=== {label} ({img.shape}) ===")
    for ch_name, ch_img in rec.make_channels(img):
        texts = rec.ocr_channel(ch_img)
        matched = rec.match_names(texts)
        print(f"  通道[{ch_name}] OCR={texts} 匹配={matched}")
