# -*- coding: utf-8 -*-
"""读取 config.ini,带编码兜底(UTF-8 -> GBK),缺键回退默认值。"""
import configparser


def _decode(raw):
    for enc in ("utf-8-sig", "gbk"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def _get_int(cp, section, key, default):
    v = cp.get(section, key, fallback=None)
    if v is None or v.strip() == "":
        return default
    try:
        return int(v.strip())
    except ValueError:
        return default


def _get_float(cp, section, key, default):
    v = cp.get(section, key, fallback=None)
    if v is None or v.strip() == "":
        return default
    try:
        return float(v.strip())
    except ValueError:
        return default


def _get_bool(cp, section, key, default):
    v = cp.get(section, key, fallback=None)
    if v is None or v.strip() == "":
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


def _get_ints(cp, section, key, default):
    v = cp.get(section, key, fallback=None)
    if v is None or v.strip() == "":
        return list(default)
    v = v.replace("，", ",")
    try:
        out = [int(x) for x in v.split(",") if x.strip()]
        return out if out else list(default)
    except ValueError:
        return list(default)


def _get_strs(cp, section, key):
    v = cp.get(section, key, fallback="")
    if not v.strip():
        return []
    v = v.replace("，", ",")
    return [x.strip() for x in v.split(",") if x.strip()]


def load_config(path):
    with open(path, "rb") as f:
        raw = f.read()
    cp = configparser.ConfigParser(interpolation=None)
    cp.read_string(_decode(raw))

    return {
        "crop": (
            _get_int(cp, "识别", "x1", 676),
            _get_int(cp, "识别", "y1", 64),
            _get_int(cp, "识别", "x2", 1560),
            _get_int(cp, "识别", "y2", 137),
        ),
        "mask": (
            _get_int(cp, "识别", "mask_x1", 300),
            _get_int(cp, "识别", "mask_x2", 540),
        ),
        "border": _get_int(cp, "识别", "border", 60),
        "high_thresh": _get_int(cp, "识别", "high_thresh", 245),
        "low_thresh": _get_int(cp, "识别", "low_thresh", 60),
        "match_cutoff": _get_float(cp, "识别", "match_cutoff", 0.4),
        "channels": _get_strs(cp, "识别", "channels"),
        "buttons": _get_ints(cp, "触发", "buttons", (4, 6, 7, 9, 10)),
        "db_file": cp.get("数据", "db_file", fallback="BattleTreeNpcPokemonStats_CN_New_Calc.xlsx").strip(),
        "tts_enabled": _get_bool(cp, "提示", "tts_enabled", True),
        "tts_rate": _get_int(cp, "提示", "tts_rate", 0),
        "tts_output_device": cp.get("提示", "tts_output_device", fallback="").strip(),
        "alert_items": _get_strs(cp, "提示", "alert_items"),
        "alert_moves": _get_strs(cp, "提示", "alert_moves"),
        "alert_abilities": _get_strs(cp, "提示", "alert_abilities"),
    }
