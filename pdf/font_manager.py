"""
Font Manager for PDF Generation
Handles Chinese font registration and configuration for ReportLab
"""
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FontManager:
    """
    Manages fonts for PDF generation

    Handles:
    - Chinese font registration (SimHei, SimSun, Microsoft YaHei)
    - Font configuration
    - Font fallback
    """

    # Common Chinese fonts on Windows
    CHINESE_FONTS = {
        'SimHei': 'C:/Windows/Fonts/simhei.ttf',
        'SimSun': 'C:/Windows/Fonts/simsun.ttc',
        'Microsoft YaHei': 'C:/Windows/Fonts/msyh.ttc',
        'Microsoft YaHei Bold': 'C:/Windows/Fonts/msyhbd.ttc',
        'KaiTi': 'C:/Windows/Fonts/simkai.ttf',
        'FangSong': 'C:/Windows/Fonts/simfang.ttf',
    }

    # Alternative Chinese fonts for Linux/Mac
    ALTERNATIVE_FONTS = {
        'Noto Sans CJK SC': '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        'WenQuanYi Micro Hei': '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        'PingFang SC': '/System/Library/Fonts/PingFang.ttc',  # macOS
    }

    def __init__(self):
        """Initialize font manager"""
        self.registered_fonts = {}
        self.default_font = None
        self.bold_font = None
        self.title_font = None

    def register_chinese_fonts(self):
        """
        Register Chinese fonts with ReportLab

        Returns:
            bool: True if at least one font was successfully registered
        """
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        registered_count = 0

        # Try Windows Chinese fonts
        for font_name, font_path in self.CHINESE_FONTS.items():
            if os.path.exists(font_path):
                try:
                    # Handle TTC font collections
                    if font_path.endswith('.ttc'):
                        # For TTC files, use subfontIndex
                        try:
                            pdfmetrics.registerFont(TTFont(font_name, font_path, subfontIndex=0))
                            self.registered_fonts[font_name] = font_path
                            registered_count += 1
                            logger.info(f"✓ Registered font: {font_name}")
                        except Exception as e:
                            logger.warning(f"Failed to register {font_name} (TTC): {e}")
                    else:
                        # For TTF files
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        self.registered_fonts[font_name] = font_path
                        registered_count += 1
                        logger.info(f"✓ Registered font: {font_name}")
                except Exception as e:
                    logger.warning(f"Failed to register {font_name}: {e}")

        # If no Windows fonts found, try alternatives
        if registered_count == 0:
            logger.info("No Windows Chinese fonts found, trying alternatives...")
            for font_name, font_path in self.ALTERNATIVE_FONTS.items():
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont(font_name, font_path, subfontIndex=0))
                        self.registered_fonts[font_name] = font_path
                        registered_count += 1
                        logger.info(f"✓ Registered alternative font: {font_name}")
                    except Exception as e:
                        logger.warning(f"Failed to register {font_name}: {e}")

        # Set default fonts (使用宋体作为正文字体)
        if 'SimSun' in self.registered_fonts:
            self.default_font = 'SimSun'
        elif 'SimHei' in self.registered_fonts:
            self.default_font = 'SimHei'
        elif 'Microsoft YaHei' in self.registered_fonts:
            self.default_font = 'Microsoft YaHei'
        elif 'Noto Sans CJK SC' in self.registered_fonts:
            self.default_font = 'Noto Sans CJK SC'
        else:
            # Use first available font
            if self.registered_fonts:
                self.default_font = list(self.registered_fonts.keys())[0]
                logger.warning(f"Using fallback font: {self.default_font}")
            else:
                logger.error("No Chinese fonts registered! PDF may not display Chinese text correctly.")

        # Set bold font (使用黑体作为粗体字体)
        if 'SimHei' in self.registered_fonts:
            self.bold_font = 'SimHei'
        elif 'Microsoft YaHei Bold' in self.registered_fonts:
            self.bold_font = 'Microsoft YaHei Bold'
        elif self.default_font:
            self.bold_font = self.default_font

        # Set title font (使用黑体作为标题字体)
        self.title_font = self.bold_font or self.default_font

        success = registered_count > 0
        logger.info(f"Font registration complete: {registered_count} fonts registered")
        logger.info(f"  Default font: {self.default_font}")
        logger.info(f"  Bold font: {self.bold_font}")
        logger.info(f"  Title font: {self.title_font}")

        return success

    def get_font_config(self):
        """
        Get font configuration for PDF generation

        Returns:
            dict: Font configuration
        """
        return {
            'default_font': self.default_font or 'Helvetica',  # Fallback to Helvetica
            'bold_font': self.bold_font or 'Helvetica-Bold',
            'title_font': self.title_font or 'Helvetica-Bold',
            'font_size_title': 24,
            'font_size_heading': 16,
            'font_size_body': 11,
            'font_size_caption': 9,
            'available_fonts': list(self.registered_fonts.keys())
        }

    def register_font_from_path(self, font_name: str, font_path: str):
        """
        Register a custom font from a specific path

        Args:
            font_name: Name to assign to the font
            font_path: Path to the font file (.ttf or .ttc)

        Returns:
            bool: True if successful
        """
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        if not os.path.exists(font_path):
            logger.error(f"Font file not found: {font_path}")
            return False

        try:
            if font_path.endswith('.ttc'):
                pdfmetrics.registerFont(TTFont(font_name, font_path, subfontIndex=0))
            else:
                pdfmetrics.registerFont(TTFont(font_name, font_path))

            self.registered_fonts[font_name] = font_path
            logger.info(f"✓ Registered custom font: {font_name} from {font_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to register custom font {font_name}: {e}")
            return False


# Global font manager instance
_font_manager_instance = None


def get_font_manager():
    """
    Get the global font manager instance (singleton)

    Returns:
        FontManager: Global font manager instance
    """
    global _font_manager_instance

    if _font_manager_instance is None:
        _font_manager_instance = FontManager()
        _font_manager_instance.register_chinese_fonts()

    return _font_manager_instance


# Auto-initialize on module load
try:
    get_font_manager()
except Exception as e:
    logger.warning(f"Failed to initialize font manager: {e}")
