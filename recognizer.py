# -*- coding: utf-8 -*-
"""V3 OCR 核心:彩色截图 -> 多通道预处理 -> RapidOCR -> 约束匹配 -> 打印。"""
import os
import sys
import difflib

import cv2
import numpy as np
import pyautogui as pag
from wcwidth import wcswidth
from rapidocr import RapidOCR


def base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def pad_to_width(text, width=4):
    """把字符串填充到至少指定宽度(汉字算双宽度)。"""
    text = str(text)
    pad_len = width - wcswidth(text)
    if pad_len > 0:
        text = text + " " * pad_len
    return text


class Recognizer:
    def __init__(self, cfg, config_map):
        self.cfg = cfg
        self.config_map = config_map
        self.names = list(config_map.keys())
        # log_level=warning 避免彩色 INFO 日志(ANSI 转义码)在控制台乱码
        self.engine = RapidOCR(params={"Global.log_level": "warning"})

    def screenshot_and_crop(self):
        """彩色截图 -> 裁剪 + 中部遮罩 + 扩边。返回 BGR 图。"""
        x1, y1, x2, y2 = self.cfg["crop"]
        mx1, mx2 = self.cfg["mask"]
        border = self.cfg["border"]
        raw_path = os.path.join(base_dir(), "screenshot_raw.png")
        pag.screenshot(raw_path)  # 保留彩色原件,便于调试与后续颜色预处理
        img = cv2.imread(raw_path)
        if img is None:
            raise RuntimeError(f"截图失败: {raw_path}")
        cropped = img[y1:y2, x1:x2].copy()
        if mx1 != mx2:
            cropped[:, mx1:mx2] = 0
        return cv2.copyMakeBorder(
            cropped, border, border, border, border,
            borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0),
        )

    def make_channels(self, img_bgr):
        """按 config 选择的通道生成预处理候选(均转成 3 通道 BGR 供 OCR)。

        可选通道: high(高阈值白字) / outline(描边反色) / clahe(灰度增强)。
        """
        CHANNEL_LABELS = {"high": "高阈值白字", "outline": "描边反色", "clahe": "灰度增强"}
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        candidates = {}
        _, c1 = cv2.threshold(gray, self.cfg["high_thresh"], 255, cv2.THRESH_BINARY)
        candidates["high"] = c1
        _, c2 = cv2.threshold(gray, self.cfg["low_thresh"], 255, cv2.THRESH_BINARY_INV)
        candidates["outline"] = c2
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        c3 = clahe.apply(gray)
        c3 = cv2.normalize(c3, None, 0, 255, cv2.NORM_MINMAX)
        candidates["clahe"] = c3

        selected = self.cfg.get("channels") or list(candidates.keys())
        out = []
        for key in selected:
            if key in candidates:
                out.append((CHANNEL_LABELS.get(key, key), candidates[key]))
        if not out:  # 配置无效时回退全部通道
            out = [(CHANNEL_LABELS.get(k, k), v) for k, v in candidates.items()]
        return [(name, cv2.cvtColor(c, cv2.COLOR_GRAY2BGR)) for name, c in out]

    def ocr_channel(self, img_bgr):
        result = self.engine(img_bgr)
        texts = []
        if result is not None:
            for t in getattr(result, "txts", None) or []:
                if t and t.strip():
                    texts.append(t.strip())
        return texts

    def match_names(self, texts):
        """把 OCR 文本约束匹配到数据库宝可梦名。返回 {名字: 相似度}。"""
        matched = {}
        for t in texts:
            m = difflib.get_close_matches(t, self.names, n=1, cutoff=self.cfg["match_cutoff"])
            if m:
                score = difflib.SequenceMatcher(None, t, m[0]).ratio()
                if m[0] not in matched or score > matched[m[0]]:
                    matched[m[0]] = score
        return matched

    def recognize_once(self):
        """执行一次识别。返回 {名字: [配置行, ...]}。"""
        img = self.screenshot_and_crop()
        channels = self.make_channels(img)
        best = {}
        best_score = -1.0
        for ch_name, ch_img in channels:
            texts = self.ocr_channel(ch_img)
            matched = self.match_names(texts)
            score = sum(matched.values())
            print(f"  [通道 {ch_name}] OCR={texts} 匹配={list(matched.keys())}")
            if len(matched) > len(best) or (len(matched) == len(best) and score > best_score):
                best = matched
                best_score = score
        return {name: self.config_map[name] for name in best}


def _render_table(conf):
    """按新排版渲染单个配置行的 2 行表格。

    上行: [名字 @ 道具] [编号] [HP] [攻] [特攻] [招式1] [招式2]
    下行: [特性] [性格] [速度] [防] [特防] [招式3] [招式4]
    最小宽度: "名字 @ 道具" / 特性 = 10 中文字符;编号 / 性格 = 2 中文字符。
    conf: 0编号 1名字 2道具 3-6招式 7性格 8HP 9攻 10防 11特攻 12特防 13速度 14特性
    """
    dex, name, item, ability, nature = conf[0], conf[1], conf[2], conf[14], conf[7]
    hp, atk, spa = conf[8], conf[9], conf[11]
    spd, dfs, spdf = conf[13], conf[10], conf[12]
    m1, m2, m3, m4 = conf[3], conf[4], conf[5], conf[6]

    top_text = f"{name} @ {item}"
    w1 = max(wcswidth(top_text), wcswidth(ability), 20)  # 名字@道具 / 特性: 最少 10 中文字符
    w2 = max(wcswidth(dex), wcswidth(nature), 4)         # 编号 / 性格: 最少 2 中文字符
    w3 = max(wcswidth(hp), wcswidth(spd), 3)
    w4 = max(wcswidth(atk), wcswidth(dfs), 3)
    w5 = max(wcswidth(spa), wcswidth(spdf), 3)
    w6 = max(wcswidth(m1), wcswidth(m3), 8)
    w7 = max(wcswidth(m2), wcswidth(m4), 8)

    widths = [w1, w2, w3, w4, w5, w6, w7]
    top_cells = [top_text, dex, hp, atk, spa, m1, m2]
    bot_cells = [ability, nature, spd, dfs, spdf, m3, m4]

    def row(cells):
        return "| " + " | ".join(pad_to_width(v, w) for v, w in zip(cells, widths)) + " |"

    def sep():
        return "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    border = sep()
    return "\n".join([border, row(top_cells), border, row(bot_cells), border])


def print_results(result):
    """打印识别结果表格。result: {名字: [配置行, ...]}。返回是否有输出。"""
    if not result:
        return False
    for name, configs in result.items():
        print(f"🔍 识别为：{name}")
        for conf in configs:
            print(_render_table(conf))
    return True
