# -*- coding: utf-8 -*-
"""V3 无 GUI 入口:读配置 -> 初始化 -> 手柄触发 -> 识别打印 + 语音提示。"""
import os
import sys
import time

import pygame

import config_loader
import db
from recognizer import Recognizer, print_results
from alerter import Alerter


def base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def find_joystick():
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        return None
    j = pygame.joystick.Joystick(0)
    j.init()
    return j


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

    base = base_dir()
    cfg_path = os.path.join(base, "config.ini")
    try:
        cfg = config_loader.load_config(cfg_path)
    except FileNotFoundError:
        print(f"❌ 找不到配置文件: {cfg_path}")
        sys.exit(1)

    db_file = os.path.join(base, cfg["db_file"])
    print(f"正在加载数据库: {db_file}")
    config_map = db.load_database(db_file)
    print(f"数据库加载完成,共 {len(config_map)} 个角色")

    print("正在初始化 OCR 引擎(RapidOCR)...")
    recognizer = Recognizer(cfg, config_map)
    print("OCR 引擎就绪\n")
    alerter = Alerter(cfg)

    pygame.init()
    joystick = find_joystick()
    buttons = set(cfg["buttons"])
    if joystick is not None:
        print(f"🎮 已检测到手柄: {joystick.get_name()}")
    else:
        print("⚠️ 未检测到手柄,每 3 秒重试一次...")
    print(f"🎮 触发按键编号: {sorted(buttons)}")
    print("等待手柄按键触发识别... (Ctrl+C 退出)\n")

    last_scan = 0.0
    prev_buttons = {}
    while True:
        now = time.time()
        if joystick is None and now - last_scan > 3.0:
            last_scan = now
            pygame.joystick.quit()
            joystick = find_joystick()
            if joystick is not None:
                print(f"🎮 已连接手柄: {joystick.get_name()}")
                prev_buttons = {}

        # 直接轮询按键状态(上升沿触发),不依赖 pygame 事件队列:
        # ① Joy-Con 下 event.get() 全量会抛 KeyError(pygame #3954/#4568)
        # ② 只取按键事件会让摇杆轴事件堆积在队列里,数分钟后队列满、
        #    新按键事件被丢弃 → 识别"卡死"。轮询不经过队列,无此问题。
        pygame.event.pump()  # 刷新 SDL 手柄状态
        if joystick is not None:
            try:
                n = joystick.get_numbuttons()
                for i in range(n):
                    cur = joystick.get_button(i)
                    if cur and not prev_buttons.get(i, False) and i in buttons:
                        print(f"🎮 检测到按键 {i} -> 触发 OCR")
                        try:
                            result = recognizer.recognize_once()
                            if result:
                                print_results(result)
                            else:
                                print("❌ 未识别到宝可梦")
                            alert_text = alerter.build_alert(result)
                            if alert_text:
                                print(f"🔔 {alert_text}")
                                alerter.speak(alert_text)
                        except Exception as e:
                            print(f"⚠️ 识别出错: {e}")
                    prev_buttons[i] = cur
            except Exception:
                # 手柄状态异常(如断开),置空等待重新扫描
                joystick = None
                prev_buttons = {}
        time.sleep(0.02)


if __name__ == "__main__":
    main()
