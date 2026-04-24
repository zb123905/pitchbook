"""
Fluent Design 主题配置

Windows 11 Fluent Design System for VC/PE PitchBook GUI
基于 Microsoft Fluent Design 设计原则：
- Light (光线)
- Depth (深度)
- Motion (动态)
- Material (材质)
- Scale (缩放)
"""
import customtkinter as ctk


class FluentTheme:
    """Fluent Design 主题配置系统 - Windows 11 风格"""

    # ==================== 颜色系统 ====================

    # 8级中性色系统 (Windows 11 标准)
    LIGHT = {
        # 背景色 - 层次分明
        'bg_base': '#FAFAFA',            # 基础背景 - 最浅
        'bg_layer_1': '#F5F5F5',         # 一级背景
        'bg_layer_2': '#EDEDED',         # 二级背景 - 卡片
        'bg_layer_3': '#E0E0E0',         # 三级背景 - 悬停
        'bg_layer_4': '#CCCCCC',         # 四级背景 - 按下

        # 表面色
        'surface_primary': '#FFFFFF',    # 主表面 - 输入框、下拉菜单
        'surface_secondary': '#F9F9F9',  # 次要表面
        'surface_tertiary': '#F0F0F0',   # 三级表面

        # 文本色
        'text_primary': '#1A1A1A',       # 主要文本 - 接近黑色
        'text_secondary': '#616161',     # 次要文本 - 深灰
        'text_tertiary': '#757575',      # 三级文本 - 中灰
        'text_disabled': '#BDBDBD',      # 禁用文本 - 浅灰
        'text_on_accent': '#FFFFFF',     # 强调色上的文本

        # 单一蓝色强调色系统 (Windows 11 标准)
        'accent_primary': '#0067C0',     # 主要蓝色 - Windows 11 标志蓝
        'accent_hover': '#185ABD',       # 悬停蓝色
        'accent_pressed': '#004578',     # 按下蓝色 - 更深
        'accent_light': '#E5F1FB',       # 浅蓝背景 - 用于高亮
        'accent_subtle': '#F3F9FD',      # 微妙蓝色 - 用于提示

        # 语义色 (保持蓝色系为主)
        'success': '#107C10',            # 绿色 - 成功 (Windows 绿)
        'warning': '#CA5010',            # 橙色 - 警告
        'error': '#D13438',              # 红色 - 错误 (Windows 红)
        'info': '#0067C0',               # 信息 - 使用蓝色

        # 边框色
        'border_default': '#E0E0E0',     # 默认边框
        'border_focus': '#0067C0',       # 聚焦边框 - 蓝色
        'border_hover': '#CCCCCC',       # 悬停边框

        # 分隔线
        'separator': '#E8E8E8',          # 细分隔线
        'separator_thick': '#D0D0D0',    # 粗分隔线
    }

    # 深色模式颜色 (Dark Mode)
    DARK = {
        # 背景色
        'bg_base': '#202020',            # 基础背景
        'bg_layer_1': '#2B2B2B',         # 一级背景
        'bg_layer_2': '#363636',         # 二级背景
        'bg_layer_3': '#404040',         # 三级背景
        'bg_layer_4': '#4A4A4A',         # 四级背景

        # 表面色
        'surface_primary': '#2D2D2D',    # 主表面
        'surface_secondary': '#333333',  # 次要表面
        'surface_tertiary': '#3A3A3A',   # 三级表面

        # 文本色
        'text_primary': '#FFFFFF',       # 主要文本
        'text_secondary': '#CCCCCC',     # 次要文本
        'text_tertiary': '#999999',      # 三级文本
        'text_disabled': '#666666',      # 禁用文本
        'text_on_accent': '#FFFFFF',     # 强调色上的文本

        # 蓝色强调色
        'accent_primary': '#4CC2FF',     # 深色模式蓝色
        'accent_hover': '#60CDFF',       # 悬停蓝色
        'accent_pressed': '#33A3E0',     # 按下蓝色
        'accent_light': '#1A3A4D',       # 浅蓝背景
        'accent_subtle': '#153045',      # 微妙蓝色

        # 语义色
        'success': '#6CCB5F',            # 绿色
        'warning': '#FE8C23',            # 橙色
        'error': '#F48771',              # 红色
        'info': '#4CC2FF',               # 信息 - 蓝色

        # 边框色
        'border_default': '#3A3A3A',     # 默认边框
        'border_focus': '#4CC2FF',       # 聚焦边框
        'border_hover': '#505050',       # 悬停边框

        # 分隔线
        'separator': '#404040',          # 分隔线
        'separator_thick': '#505050',    # 粗分隔线
    }

    # ==================== 圆角半径 ====================
    # Fluent Design 圆角比 Apple 更小更精致
    CORNER_RADIUS = {
        'xsmall': 2,      # 极小 - 装饰条
        'small': 4,       # 小 - 按钮、输入框 (Apple: 6)
        'medium': 8,      # 中 - 卡片 (Apple: 10)
        'large': 12,      # 大 - 大卡片 (Apple: 16)
        'xlarge': 16,     # 超大 - 模态框 (Apple: 24)
    }

    # ==================== 间距系统 ====================
    # Fluent Design 使用更宽松的间距
    SPACING = {
        'xxs': 2,         # 极小间距
        'xs': 4,          # 小间距
        'sm': 8,          # 中小间距
        'md': 12,         # 中等间距
        'lg': 16,         # 大间距
        'xl': 24,         # 超大间距 (卡片间距)
        'xxl': 32,        # 极大间距
        'xxxl': 48,       # 最大间距
    }

    PADDING = {
        'xsm': 8,         # 极小内边距
        'sm': 12,         # 小内边距
        'md': 16,         # 中内边距
        'lg': 20,         # 大内边距
        'xl': 24,         # 超大内边距
    }

    # ==================== 字体层级 ====================
    # 使用 Segoe UI - Windows 标准字体
    FONT_FAMILY = "Segoe UI"

    FONT_SIZE = {
        'caption': 12,       # 说明文字
        'body': 14,          # 正文
        'body_large': 16,    # 大正文
        'subtitle': 18,      # 副标题
        'title': 20,         # 标题
        'title_large': 24,   # 大标题
        'display': 28,       # 展示标题
    }

    # ==================== 动画时长 ====================
    # Fluent Design 动画更快速 - 优化后的帧率体验
    DURATION = {
        'fast': 80,          # 快速 - 80ms (更响应)
        'normal': 120,       # 正常 - 120ms (更流畅)
        'slow': 160,         # 慢速 - 160ms
        'slower': 240,       # 更慢 - 240ms
    }

    # ==================== 边框宽度 ====================
    BORDER_WIDTH = {
        'none': 0,
        'thin': 1,
        'medium': 2,
        'thick': 3,
    }

    # ==================== 高度 ====================
    HEIGHT = {
        'input': 36,         # 输入框高度
        'button': 36,        # 按钮高度
        'button_large': 44,  # 大按钮高度
        'header': 48,        # 顶部栏高度 (简化后)
    }

    # ==================== 类方法 ====================

    @classmethod
    def get_colors(cls, appearance_mode: str = None) -> dict:
        """
        获取当前模式的颜色

        Args:
            appearance_mode: 主题模式 ('System', 'Light', 'Dark')
        """
        if appearance_mode is None:
            appearance_mode = ctk.get_appearance_mode()

        if appearance_mode == 'Dark':
            return cls.DARK
        return cls.LIGHT

    @classmethod
    def color(cls, key: str, appearance_mode: str = None) -> tuple:
        """
        获取颜色值（返回 CTk 兼容的元组格式）

        Args:
            key: 颜色键名 (如 'bg_base', 'accent_primary')
            appearance_mode: 主题模式

        Returns:
            (light_color, dark_color) 元组
        """
        colors = cls.get_colors(appearance_mode)
        value = colors.get(key, cls.LIGHT.get(key, '#000000'))
        return (value, cls.DARK.get(key, value))

    @classmethod
    def get_corner_radius(cls, size: str = 'medium') -> int:
        """获取圆角半径"""
        return cls.CORNER_RADIUS.get(size, 8)

    @classmethod
    def get_spacing(cls, size: str = 'md') -> int:
        """获取间距值"""
        return cls.SPACING.get(size, 12)

    @classmethod
    def get_padding(cls, size: str = 'md') -> int:
        """获取内边距值"""
        return cls.PADDING.get(size, 16)

    @classmethod
    def get_font_size(cls, level: str = 'body') -> int:
        """获取字体大小"""
        return cls.FONT_SIZE.get(level, 14)

    @classmethod
    def get_font(cls, level: str = 'body', weight: str = 'normal') -> ctk.CTkFont:
        """
        获取字体对象

        Args:
            level: 字体层级
            weight: 字重 (normal, bold)
        """
        size = cls.get_font_size(level)
        weight_val = 'bold' if weight == 'bold' else 'normal'
        return ctk.CTkFont(size=size, weight=weight_val)

    @classmethod
    def get_border_width(cls, size: str = 'thin') -> int:
        """获取边框宽度"""
        return cls.BORDER_WIDTH.get(size, 1)

    @classmethod
    def apply_card_style(cls, widget, elevated: bool = False):
        """
        应用 Fluent 卡片样式

        Args:
            widget: CTk 组件
            elevated: 是否为浮起状态 (增加边框)
        """
        widget.configure(
            corner_radius=cls.get_corner_radius('medium'),
            fg_color=cls.color('surface_primary'),
            border_width=cls.get_border_width('medium') if elevated else cls.get_border_width('thin'),
            border_color=cls.color('border_default') if not elevated else cls.color('accent_primary'),
        )

    @classmethod
    def apply_button_style(cls, widget, style: str = 'primary'):
        """
        应用 Fluent 按钮样式

        Args:
            widget: CTkButton 组件
            style: 样式类型 ('primary', 'secondary', 'ghost', 'accent')
        """
        style_map = {
            'primary': {
                'fg_color': cls.color('accent_primary'),
                'hover_color': cls.color('accent_hover'),
                'text_color': (cls.LIGHT['text_on_accent'], cls.DARK['text_on_accent']),
                'corner_radius': cls.get_corner_radius('small'),
                'height': cls.HEIGHT['button'],
            },
            'secondary': {
                'fg_color': cls.color('bg_layer_2'),
                'hover_color': cls.color('bg_layer_3'),
                'text_color': cls.color('text_primary'),
                'corner_radius': cls.get_corner_radius('small'),
                'height': cls.HEIGHT['button'],
            },
            'ghost': {
                'fg_color': 'transparent',
                'hover_color': cls.color('bg_layer_2'),
                'text_color': cls.color('text_primary'),
                'border_width': cls.get_border_width('thin'),
                'border_color': cls.color('border_default'),
                'corner_radius': cls.get_corner_radius('small'),
                'height': cls.HEIGHT['button'],
            },
            'accent': {
                'fg_color': cls.color('accent_primary'),
                'hover_color': cls.color('accent_hover'),
                'text_color': (cls.LIGHT['text_on_accent'], cls.DARK['text_on_accent']),
                'corner_radius': cls.get_corner_radius('medium'),
                'height': cls.HEIGHT['button_large'],
            },
        }

        style_config = style_map.get(style, style_map['primary'])
        widget.configure(**style_config)

    @classmethod
    def apply_input_style(cls, widget):
        """
        应用 Fluent 输入框样式

        Args:
            widget: CTkEntry 组件
        """
        widget.configure(
            corner_radius=cls.get_corner_radius('small'),
            border_width=cls.get_border_width('thin'),
            border_color=cls.color('border_default'),
            height=cls.HEIGHT['input'],
        )

    @classmethod
    def get_status_colors(cls, status: str) -> tuple:
        """
        获取状态对应的颜色

        Args:
            status: 状态类型 (success, warning, error, info, pending, running)

        Returns:
            (light_color, dark_color) 元组
        """
        status_map = {
            'success': cls.color('success'),
            'warning': cls.color('warning'),
            'error': cls.color('error'),
            'info': cls.color('info'),
            'pending': cls.color('text_tertiary'),
            'running': cls.color('accent_primary'),
        }
        return status_map.get(status, cls.color('text_primary'))


# 便捷函数
def get_color(key: str, mode: str = None) -> tuple:
    """快捷获取颜色"""
    return FluentTheme.color(key, mode)


def get_font(level: str = 'body', weight: str = 'normal') -> ctk.CTkFont:
    """快捷获取字体"""
    return FluentTheme.get_font(level, weight)


def get_spacing(size: str = 'md') -> int:
    """快捷获取间距"""
    return FluentTheme.get_spacing(size)


def get_padding(size: str = 'md') -> int:
    """快捷获取内边距"""
    return FluentTheme.get_padding(size)


def get_corner_radius(size: str = 'medium') -> int:
    """快捷获取圆角"""
    return FluentTheme.get_corner_radius(size)
