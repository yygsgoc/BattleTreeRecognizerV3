# -*- coding: utf-8 -*-
import sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
import pygame

pygame.init()
pygame.joystick.init()
j = pygame.joystick.Joystick(0)
j.init()
print("name:", j.get_name())

# 模拟当前 headless 的行为:只取按键事件,轴事件留在队列
print("模拟 15 秒:只 get(JOYBUTTONDOWN),不取轴事件...")
t0 = time.time()
while time.time() - t0 < 15:
    pygame.event.pump()
    try:
        pygame.event.get(pygame.JOYBUTTONDOWN)
    except (SystemError, KeyError):
        pass
    time.sleep(0.05)

# 检查队列里累积了多少轴事件
try:
    axis = pygame.event.get(pygame.JOYAXISMOTION)
    print("累积的 JOYAXISMOTION 事件数:", len(axis))
except Exception as e:
    print("取轴事件异常:", e)

# 再取按钮事件,看队列是否还能正常出
try:
    btns = pygame.event.get(pygame.JOYBUTTONDOWN)
    print("按钮事件:", len(btns))
except Exception as e:
    print("按钮事件异常:", e)

# 直接轮询 get_button(不依赖事件队列)
print("\n直接轮询 get_button 3 秒(验证不依赖事件队列也能读按键)...")
t0 = time.time()
ok = 0
while time.time() - t0 < 3:
    try:
        s = [j.get_button(i) for i in range(j.get_numbuttons())]
        ok += 1
    except Exception as e:
        print("get_button 异常:", e)
        break
    time.sleep(0.05)
print("get_button 轮询正常次数:", ok, "(无异常)")
