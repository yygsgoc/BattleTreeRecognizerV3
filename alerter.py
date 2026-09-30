# -*- coding: utf-8 -*-
"""语音提示:命中预设的道具/招式/特性时播报。

直接调用 Windows SAPI(comtypes + 同步 Speak),不使用 pyttsx3 的事件循环。
pyttsx3 的 sapi5 驱动依赖 COM 事件(EndStream)结束 runAndWait,
复用同一 engine 时第二次不再发声("只播一次"bug),故弃用。
"""
import pythoncom
import comtypes.client


class Alerter:
    def __init__(self, cfg):
        self.cfg = cfg
        self.enabled = bool(cfg.get("tts_enabled"))
        self._output_note = None  # 缓存设备选择提示,避免每次播报重复打印

    def _get_voice(self):
        pythoncom.CoInitialize()
        voice = comtypes.client.CreateObject("SAPI.SpVoice")
        # 优先选择中文语音
        try:
            voices = voice.GetVoices()
            for i in range(voices.Count):
                desc = voices.Item(i).GetDescription()
                if "Chinese" in desc or "中文" in desc:
                    voice.Voice = voices.Item(i)
                    break
        except Exception:
            pass
        # SAPI 语速范围 -10..10(0=正常)
        rate = int(self.cfg.get("tts_rate", 0))
        voice.Rate = max(-10, min(10, rate))
        # 音频输出设备(空=默认)
        self._select_output(voice)
        return voice

    def _select_output(self, voice):
        """按 config 的 tts_output_device 选择输出设备(包含匹配)。

        空配置 = 系统默认;未命中或异常 = 安全回退默认,并提示一次。
        """
        target = str(self.cfg.get("tts_output_device", "") or "").strip()
        if not target:
            return
        note = None
        try:
            outputs = voice.GetAudioOutputs()
            target_l = target.lower()
            for i in range(outputs.Count):
                tok = outputs.Item(i)
                desc = tok.GetDescription() or ""
                if target_l in desc.lower():
                    voice.AudioOutput = tok
                    note = f"🔊 TTS 输出设备: {desc}"
                    break
            if note is None:
                note = f"⚠️ 未找到 TTS 输出设备「{target}」,已回退默认输出"
        except Exception as e:
            note = f"⚠️ 设置 TTS 输出设备失败({e}),已回退默认输出"
        if note and note != self._output_note:
            print(note)
            self._output_note = note

    def build_alert(self, result):
        """result: {名字: [配置行,...]} -> 返回提示文本,无触发返回 None。

        配置行: 0编号 1名字 2道具 3-6招式 7性格 ... 14特性
        """
        if not result:
            return None
        items = set(self.cfg.get("alert_items", []))
        moves = set(self.cfg.get("alert_moves", []))
        abilities = set(self.cfg.get("alert_abilities", []))
        if not (items or moves or abilities):
            return None

        parts = []
        for name, configs in result.items():
            triggered = []
            for conf in configs:
                item = conf[2]
                if item and item in items and item not in triggered:
                    triggered.append(item)
                for m in conf[3:7]:
                    if m and m in moves and m not in triggered:
                        triggered.append(m)
                ability = conf[14]
                if ability:
                    for ab in ability.split("／"):
                        if ab and ab in abilities and ab not in triggered:
                            triggered.append(ab)
            if triggered:
                parts.append(f"{name}，" + "，".join(triggered))
        if not parts:
            return None
        return "注意：" + "；".join(parts)

    def speak(self, text):
        if not (self.enabled and text):
            return
        try:
            voice = self._get_voice()
            voice.Speak(str(text))  # 同步播报,阻塞至播完
        except Exception as e:
            print(f"⚠️ 语音播报失败: {e}")
