from PIL import Image
import streamlit as st


class ImageProcessor:
    """
    图片处理工具类
    提供格式转换、水印添加等功能
    """

    def convert_image_for_format(self, image, target_format):
        """根据目标格式转换图片模式"""
        img = image.copy()

        if target_format in ["JPG", "JPEG", "BMP"]:
            # JPG和BMP不支持透明通道，需要转换为RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                # 将原图粘贴到背景上
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
        elif target_format == "PNG":
            # PNG支持透明通道，保持原模式或转换为RGBA
            if img.mode in ('P', 'LA'):
                img = img.convert('RGBA')
        elif target_format == "WEBP":
            # WEBP支持透明通道
            if img.mode in ('P', 'LA'):
                img = img.convert('RGBA')

        return img

    def add_watermark(self, image, text, position, font_size, color, opacity, rotation):
        """添加文字水印到图片"""
        from PIL import ImageDraw, ImageFont
        import os

        # 创建图片副本
        img = image.copy()

        # 转换为RGBA模式以支持透明度
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 创建透明层
        watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)

        # 字体处理 - 支持中文
        font = None
        font_paths = [
            # Windows 字体路径
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
            "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
            # macOS 字体路径
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            # Linux 字体路径
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/arphic/ukai.ttc",
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue

        # 如果系统字体都不可用，使用默认字体（但可能不支持中文）
        if font is None:
            try:
                font = ImageFont.load_default()
                st.warning("⚠️ 未找到中文字体，中文显示可能不正常。建议安装中文字体。")
            except:
                st.error("❌ 无法加载字体")

        # 计算文字尺寸
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # 如果计算失败，使用估计值
            text_width = len(text) * font_size
            text_height = font_size

        # 计算位置
        if position == "顶部居左":
            x = 10
            y = 10
        elif position == "顶部居中":
            x = (img.width - text_width) // 2
            y = 10
        elif position == "顶部居右":
            x = img.width - text_width - 10
            y = 10
        elif position == "左边居中":
            x = 10
            y = (img.height - text_height) // 2
        elif position == "图片中心":
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2
        elif position == "右边居中":
            x = img.width - text_width - 10
            y = (img.height - text_height) // 2
        elif position == "底部居左":
            x = 10
            y = img.height - text_height - 10
        elif position == "底部居中":
            x = (img.width - text_width) // 2
            y = img.height - text_height - 10
        elif position == "底部居右":
            x = img.width - text_width - 10
            y = img.height - text_height - 10
        else:
            x = 10
            y = 10

        # 设置颜色和透明度
        r, g, b = color
        alpha = int(255 * opacity)

        # 如果有旋转角度，创建旋转后的水印
        if rotation != 0:
            # 创建临时图片来绘制文字（更大的画布以适应旋转）
            temp_width = int(text_width * 1.5)
            temp_height = int(text_height * 1.5)
            temp_img = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            temp_draw.text((temp_width // 2 - text_width // 2, temp_height // 2 - text_height // 2),
                           text, font=font, fill=(r, g, b, alpha))

            # 旋转图片
            rotated_img = temp_img.rotate(rotation, expand=True, resample=Image.BICUBIC)

            # 计算旋转后的位置
            rot_width, rot_height = rotated_img.size
            if position == "图片中心":
                x = (img.width - rot_width) // 2
                y = (img.height - rot_height) // 2
            elif "居右" in position:
                x = img.width - rot_width - 10
            elif "居中" in position:
                x = (img.width - rot_width) // 2

            if "底部" in position:
                y = img.height - rot_height - 10
            elif "居中" in position and "底部" not in position and "顶部" not in position:
                y = (img.height - rot_height) // 2

            # 粘贴旋转后的水印
            watermark.paste(rotated_img, (x, y), rotated_img)
        else:
            # 直接绘制文字
            draw.text((x, y), text, font=font, fill=(r, g, b, alpha))

        # 合并原图和水印
        result = Image.alpha_composite(img, watermark)

        return result