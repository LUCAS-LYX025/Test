# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: transform.py
@time: 2024/4/28 16:06
"""
from PIL import Image
import pytesseract


def main():
    # 设置 Tesseract OCR 引擎的安装路径（根据你的实际安装路径进行设置）
    pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

    # 读取图片
    image_path = '/Users/leiyuxing/PycharmProjects/TestFramework/study/test1.png'
    # 替换为你的图片路径
    img = Image.open(image_path)

    # 使用 Pytesseract 进行 OCR 文字识别
    text = pytesseract.image_to_string(img, lang='chi_sim')

    # 打印识别出的文字
    print(text)


if __name__ == '__main__':
    main()
