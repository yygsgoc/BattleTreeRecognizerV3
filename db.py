# -*- coding: utf-8 -*-
"""读取数据库 xlsx(15 列,Column15 = 可能的特性)。"""
from collections import defaultdict

import openpyxl


def load_database(xlsx_path):
    """返回 {名字: [配置行列表]}。

    每行 15 列:
      0 编号  1 名字  2 道具  3-6 招式  7 性格
      8 HP  9 攻  10 防  11 特攻  12 特防  13 速度  14 特性
    """
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb.active
    config_map = defaultdict(list)
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or len(row) < 15 or row[1] is None:
            continue
        name = str(row[1]).strip()
        if not name:
            continue
        conf = list(row[:15])
        # 编号补零为 4 位,其余统一转字符串
        conf[0] = str(conf[0]).zfill(4) if conf[0] is not None else ""
        for i in range(len(conf)):
            conf[i] = "" if conf[i] is None else str(conf[i])
        config_map[name].append(conf)
    wb.close()
    return config_map
