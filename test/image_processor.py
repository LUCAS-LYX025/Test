from PIL import Image
import streamlit as st

class ImageProcessor:
    """
    图片处理工具类
    提供格式转换、水印添加等功能
    """

    def __init__(self):
        self.available_fonts = self._detect_fonts()

    def _detect_fonts(self):
        """检测可用的字体"""
        fonts = []
        # 这里可以添加字体检测逻辑
        return fonts

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

    def add_watermark(self, image, text, position, font_size, color, opacity, rotation, font_file=None):
        """添加水印 - 增强版，支持中文字体"""
        try:
            from PIL import ImageDraw, ImageFont
            import os

            # 创建水印图层
            if image.mode != 'RGBA':
                watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
                image_rgba = image.convert('RGBA')
            else:
                watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
                image_rgba = image

            draw = ImageDraw.Draw(watermark)

            # 字体处理逻辑
            font = None

            # 1. 如果用户上传了字体文件
            if font_file is not None:
                try:
                    # 保存上传的字体文件到临时位置
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.ttf') as tmp_file:
                        tmp_file.write(font_file.getvalue())
                        font_path = tmp_file.name

                    font = ImageFont.truetype(font_path, font_size)
                    # 清理临时文件
                    os.unlink(font_path)
                except Exception as e:
                    print(f"使用上传字体失败: {e}")

            # 2. 自动检测系统字体
            if font is None:
                font = self._get_available_font(font_size)

            # 3. 如果还是没找到字体，使用默认字体
            if font is None:
                try:
                    font = ImageFont.load_default()
                    # 调整默认字体的大小
                    from PIL import ImageFont
                    default_font = ImageFont.load_default()
                    # 对于默认字体，我们只能调整绘制位置来模拟大小
                except:
                    pass

            # 获取文字尺寸
            try:
                if hasattr(draw, 'textbbox'):  # PIL 9.2.0+
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                else:  # 旧版本PIL
                    bbox = draw.textsize(text, font=font)
                    text_width, text_height = bbox
            except:
                # 如果获取文字尺寸失败，使用估计值
                text_width = len(text) * font_size
                text_height = font_size

            # 计算位置
            positions = {
                "顶部居左": (10, 10),
                "顶部居中": ((image.width - text_width) // 2, 10),
                "顶部居右": (image.width - text_width - 10, 10),
                "左边居中": (10, (image.height - text_height) // 2),
                "图片中心": ((image.width - text_width) // 2, (image.height - text_height) // 2),
                "右边居中": (image.width - text_width - 10, (image.height - text_height) // 2),
                "底部居左": (10, image.height - text_height - 10),
                "底部居中": ((image.width - text_width) // 2, image.height - text_height - 10),
                "底部居右": (image.width - text_width - 10, image.height - text_height - 10)
            }

            x, y = positions.get(position, (10, 10))

            # 绘制水印（带透明度）
            alpha = int(255 * opacity)
            fill_color = color + (alpha,)

            # 添加文字阴影效果，提高可读性
            shadow_color = (0, 0, 0, alpha // 2)
            draw.text((x + 1, y + 1), text, font=font, fill=shadow_color)
            draw.text((x, y), text, font=font, fill=fill_color)

            # 旋转水印
            if rotation != 0:
                watermark = watermark.rotate(rotation, expand=False, resample=Image.Resampling.BICUBIC,
                                             center=(x + text_width // 2, y + text_height // 2))

            # 合并图片和水印
            result = Image.alpha_composite(image_rgba, watermark)

            # 如果原图不是RGBA，转换回去
            if image.mode != 'RGBA':
                result = result.convert(image.mode)

            return result

        except Exception as e:
            print(f"水印添加失败: {e}")
            return image

    def _get_available_font(self, font_size):
        """获取可用的字体"""
        from PIL import ImageFont
        import sys
        import os

        # 常见的中文字体路径
        font_paths = []

        # Windows 字体路径
        if sys.platform == "win32":
            windir = os.environ.get("WINDIR", "C:\\Windows")
            font_paths.extend([
                os.path.join(windir, "Fonts", "simhei.ttf"),  # 黑体
                os.path.join(windir, "Fonts", "simsun.ttc"),  # 宋体
                os.path.join(windir, "Fonts", "msyh.ttc"),  # 微软雅黑
                os.path.join(windir, "Fonts", "msyhbd.ttc"),  # 微软雅黑粗体
            ])

        # Linux 字体路径
        elif sys.platform.startswith("linux"):
            font_paths.extend([
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ])

        # macOS 字体路径
        # elif sys.platform == "darwin":
        #     font_paths.extend([
        #         "/System/Library/Fonts/PingFang.ttc",
        #         "/System/Library/Fonts/STHeiti Light.ttc",
        #         "/System/Library/Fonts/Helvetica.ttc",
        #         "/Library/Fonts/Arial.ttf",
        #     ])

        # 尝试每个字体路径
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except Exception:
                    continue
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        custom_font_path = os.path.join(current_dir, "fonts/PingFang.ttc")

        # 在 Streamlit 中显示调试信息
        import streamlit as st
        st.success(f"📁 当前文件目录: `{current_dir}`")
        st.success(f"🎯 字体文件路径: `{custom_font_path}`")
        st.success(f"✅ 字体文件是否存在: `{os.path.exists(custom_font_path)}`")

        if os.path.exists(custom_font_path):
            try:
                st.success("✅ 正在加载自定义字体...")
                return ImageFont.truetype(custom_font_path, font_size)
            except Exception as e:
                st.error(f"❌ 自定义字体加载失败: {e}")
                pass  # 如果自定义字体也失败，继续尝试其他选项
        else:
            st.warning("⚠️ 自定义字体文件不存在，继续尝试其他选项")
        # # 如果都没找到，尝试使用指定的 PingFang.ttc 路径
        # custom_font_path = "/mount/src/test/test/PingFang.ttc"
        # if os.path.exists(custom_font_path):
        #     try:
        #         return ImageFont.truetype(custom_font_path, font_size)
        #     except Exception:
        #         pass  # 如果自定义字体也失败，继续尝试其他选项

        # 如果都没找到，尝试系统默认字体
        try:
            return ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                return ImageFont.load_default()
            except:
                return None
