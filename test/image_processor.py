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
            import streamlit as st

            # 显示水印处理开始信息
            with st.expander("🎨 水印处理详情", expanded=True):
                st.write(f"**水印文本**: `{text}`")
                st.write(f"**位置**: `{position}` | **大小**: `{font_size}` | **透明度**: `{opacity}` | **旋转**: `{rotation}°`")
                st.write(f"**图片尺寸**: {image.size} | **模式**: {image.mode}")

            # 创建水印图层
            if image.mode != 'RGBA':
                watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
                image_rgba = image.convert('RGBA')
                st.info("🔄 图片已转换为 RGBA 模式以支持透明度")
            else:
                watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
                image_rgba = image

            draw = ImageDraw.Draw(watermark)

            # 字体处理逻辑
            font = None
            font_source = "未确定"

            # 1. 如果用户上传了字体文件
            if font_file is not None:
                try:
                    st.success("📤 检测到用户上传字体文件，正在处理...")
                    # 保存上传的字体文件到临时位置
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.ttf') as tmp_file:
                        tmp_file.write(font_file.getvalue())
                        font_path = tmp_file.name

                    font = ImageFont.truetype(font_path, font_size)
                    font_source = "用户上传字体"
                    st.success(f"✅ {font_source} 加载成功")
                    # 清理临时文件
                    os.unlink(font_path)
                except Exception as e:
                    st.error(f"❌ 用户上传字体加载失败: {e}")

            # 2. 自动检测系统字体
            if font is None:
                st.info("🔄 开始自动检测系统字体...")
                font = self._get_available_font(font_size)
                if font:
                    font_source = "系统检测字体"
                    st.success(f"✅ {font_source} 加载成功")

            # 3. 如果还是没找到字体，使用默认字体
            if font is None:
                st.warning("⚠️ 开始使用默认字体回退方案...")
                try:
                    font = ImageFont.load_default()
                    font_source = "PIL默认字体"
                    st.success(f"✅ {font_source} 加载成功")

                    # 打印默认字体信息
                    st.info(f"🔤 默认字体类型: {type(font)}")
                    st.write("📝 注意: 默认字体可能不支持中文或大小调整")

                except Exception as e:
                    st.error(f"❌ 默认字体加载失败: {e}")
                    font_source = "无可用字体"

            # 获取文字尺寸
            try:
                if hasattr(draw, 'textbbox'):  # PIL 9.2.0+
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    bbox_method = "textbbox (PIL 9.2.0+)"
                else:  # 旧版本PIL
                    bbox = draw.textsize(text, font=font)
                    text_width, text_height = bbox
                    bbox_method = "textsize (旧版PIL)"

                st.success(f"📐 文字尺寸计算成功: {text_width}×{text_height}px (方法: {bbox_method})")

            except Exception as e:
                st.warning(f"⚠️ 文字尺寸计算失败，使用估计值: {e}")
                # 如果获取文字尺寸失败，使用估计值
                text_width = len(text) * font_size // 2
                text_height = font_size
                st.info(f"📏 使用估计尺寸: {text_width}×{text_height}px")

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
            st.info(f"📍 水印位置: ({x}, {y}) - {position}")

            # 绘制水印（带透明度）
            alpha = int(255 * opacity)
            fill_color = color + (alpha,)

            st.write(f"🎨 颜色: RGB{color} + 透明度 {alpha}")

            # 添加文字阴影效果，提高可读性
            shadow_color = (0, 0, 0, alpha // 2)
            draw.text((x + 1, y + 1), text, font=font, fill=shadow_color)
            draw.text((x, y), text, font=font, fill=fill_color)
            st.success("✅ 水印文字绘制完成")

            # 旋转水印
            if rotation != 0:
                st.info(f"🔄 应用旋转: {rotation}°")
                watermark = watermark.rotate(rotation, expand=False, resample=Image.Resampling.BICUBIC,
                                             center=(x + text_width // 2, y + text_height // 2))

            # 合并图片和水印
            result = Image.alpha_composite(image_rgba, watermark)
            st.success("✅ 图片与水印合并完成")

            # 如果原图不是RGBA，转换回去
            if image.mode != 'RGBA':
                result = result.convert(image.mode)
                st.info(f"🔄 图片转换回原始模式: {image.mode}")

            # 最终成功报告
            st.success(f"""
            🎉 水印添加成功!

            **总结信息:**
            - 字体来源: {font_source}
            - 最终图片尺寸: {result.size}
            - 图片模式: {result.mode}
            - 水印位置: {position}
            - 旋转角度: {rotation}°
            """)

            return result

        except Exception as e:
            st.error(f"""
            💥 水印添加失败!

            错误详情: {e}

            可能的原因:
            - 图片格式不支持
            - 字体文件损坏
            - 内存不足
            - PIL 库异常
            """)
            # 返回原图作为回退
            return image

    def _get_available_font(self, font_size):
        """获取可用的字体"""
        from PIL import ImageFont
        import sys
        import os
        import streamlit as st

        # 在侧边栏显示字体检测过程
        with st.sidebar:
            st.header("🔤 字体检测过程")
            st.write(f"**目标字体大小**: {font_size}")
            st.write(f"**运行平台**: {sys.platform}")

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
            st.info("🪟 检测到 Windows 系统，使用 Windows 字体路径")

        # Linux 字体路径
        elif sys.platform.startswith("linux"):
            font_paths.extend([
                # 中文相关字体
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Android 字体
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 文泉驿微米黑
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # 文泉驿正黑
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Google Noto 字体

                # Ubuntu/Debian 常见路径
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf",

                # RedHat/CentOS/Fedora 常见路径
                "/usr/share/fonts/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf",

                # 其他可能的中文字体路径
                "/usr/share/fonts/truetype/arphic/ukai.ttc",  # AR PL 楷体
                "/usr/share/fonts/truetype/arphic/uming.ttc",  # AR PL 明体
                "/usr/share/fonts/truetype/ttf-wps-fonts/simfang.ttf",  # WPS 仿宋
                "/usr/share/fonts/truetype/ttf-wps-fonts/simhei.ttf",  # WPS 黑体
                "/usr/share/fonts/truetype/ttf-wps-fonts/simkai.ttf",  # WPS 楷体

                # Noto 字体其他可能位置
                "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/noto/NotoSansCJK-Regular.ttc",

                # 用户安装字体
                "/usr/local/share/fonts/wqy-microhei.ttc",
                "~/.local/share/fonts/wqy-microhei.ttc",

                # 容器/云环境常见字体
                "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            ])
            st.info("🐧 检测到 Linux 系统，使用 Linux 字体路径")

        # macOS 字体路径
        elif sys.platform == "darwin":
            font_paths.extend([
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc",
                "/System/Library/Fonts/Helvetica.ttc",
                "/Library/Fonts/Arial.ttf",
            ])
            st.info("🍎 检测到 macOS 系统，使用 macOS 字体路径")

        # 显示所有检测的字体路径
        with st.expander("📋 系统字体路径检测列表", expanded=False):
            for i, font_path in enumerate(font_paths, 1):
                exists = os.path.exists(font_path)
                status = "✅" if exists else "❌"
                st.write(f"{i}. {status} `{font_path}`")

        # 尝试每个字体路径
        found_system_font = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    st.success(f"🎯 系统字体加载成功: `{os.path.basename(font_path)}`")
                    found_system_font = True
                    return font
                except Exception as e:
                    st.warning(f"⚠️ 字体文件存在但加载失败: `{font_path}` - {e}")
                    continue

        if not found_system_font:
            st.warning("🔍 未找到可用的系统字体，尝试项目自定义字体...")

        # 尝试项目自定义字体
        current_dir = os.path.dirname(os.path.abspath(__file__))
        custom_font_path = os.path.join(current_dir, "fonts", "PingFang.ttc")

        with st.expander("📁 自定义字体路径信息", expanded=True):
            st.write(f"**当前文件目录**: `{current_dir}`")
            st.write(f"**自定义字体路径**: `{custom_font_path}`")
            st.write(f"**路径是否存在**: **{'✅ 是' if os.path.exists(custom_font_path) else '❌ 否'}**")

            # 检查字体目录内容
            font_dir = os.path.dirname(custom_font_path)
            if os.path.exists(font_dir):
                try:
                    dir_files = os.listdir(font_dir)
                    st.write(f"**字体目录内容**: {dir_files}")
                except Exception as e:
                    st.error(f"无法读取字体目录: {e}")
            else:
                st.error(f"字体目录不存在: `{font_dir}`")

        if os.path.exists(custom_font_path):
            try:
                st.info("🔄 正在加载自定义字体...")
                font = ImageFont.truetype(custom_font_path, font_size)
                st.success("✅ 自定义字体加载成功!")
                return font
            except Exception as e:
                st.error(f"❌ 自定义字体加载失败: {e}")
        else:
            st.warning("⚠️ 自定义字体文件不存在")

        # 最终回退方案
        st.warning("🚨 开始最终字体回退方案...")

        with st.expander("🔄 最终回退方案尝试", expanded=True):
            # 尝试系统默认英文字体
            st.write("1. 尝试系统英文字体 (arial.ttf)...")
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
                st.success("✅ 系统英文字体加载成功")
                return font
            except Exception as e:
                st.error(f"❌ 系统英文字体失败: {e}")

            # 尝试 PIL 默认字体
            st.write("2. 尝试 PIL 默认字体...")
            try:
                font = ImageFont.load_default()
                st.success("✅ PIL 默认字体加载成功")
                return font
            except Exception as e:
                st.error(f"❌ PIL 默认字体失败: {e}")

        st.error("💥 所有字体方案均失败，返回 None")
        return None
