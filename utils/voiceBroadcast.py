# -*- coding: utf-8 -*-

"""
@author: lucas
@Function: 语音播报功能
@file: voiceBroadcast.py
@time: 2021/10/2 4:00 下午
"""
import pyttsx3


def voiceBroadcast(speckingRate, content):
    """
    speckingRate: 语速
    content: 需要播报的内容
    """
    engine = pyttsx3.init()
    engine.getProperty('rate')
    engine.setProperty('rate', speckingRate)
    engine.say(content)
    engine.runAndWait()
    engine.stop()

