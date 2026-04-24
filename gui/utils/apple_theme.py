"""
苹果风格主题配置

Apple-inspired design system for VC/PE PitchBook GUI
"""
import customtkinter as ctk


class AppleTheme:
    """苹果风格主题配置系统"""

    # ==================== 颜色系统 ====================

    # 浅色模式颜色 (Light Mode)
    LIGHT = {
        # 背景色
        'bg_primary': '#F5F5F7',           # 主背景 - 类似 macOS Finder
        'bg_secondary': '#FFFFFF',          # 次要背景
        'bg_tertiary': '#E5E5EA',           # 三级背景 - 分隔线/卡片
        'bg_elevated': '#FFFFFF',           # 浮起元素
        'bg_gradient_start': '#F0F4FF',     # 渐变起始 - 微蓝
        'bg_gradient_end': '#FAF5FF',       # 渐变结束 - 微紫

        # 文本色
        'text_primary': '#000000',          # 主文本
        'text_secondary': '#3C3C43',        # 次要文本 - 60% opacity
        'text_tertiary': '#8E8E93',         # 三级文本 - 30% opacity
        'text_disabled': '#C7C7CC',         # 禁用文本

        # 强调色 (SF Colors)
        'accent_blue': '#007AFF',           # 蓝色 - 主要操作
        'accent_blue_hover': '#0051D5',
        'accent_cyan': '#32ADE6',           # 青色
        'accent_indigo': '#5856D6',         # 靛蓝
        'accent_purple': '#AF52DE',         # 紫色
        'accent_pink': '#FF2D55',           # 粉色
        'accent_teal': '#5AC8FA',           # 青绿
        'accent_green': '#34C759',          # 绿色 - 成功
        'accent_orange': '#FF9500',         # 橙色 - 警告
        'accent_red': '#FF3B30',            # 红色 - 错误/危险
        'accent_yellow': '#FFCC00',         # 黄色

        # 语义色
        'success': '#34C759',
        'warning': '#FF9500',
        'error': '#FF3B30',
        'info': '#007AFF',

        # 边框色
        'border': '#C6C6C8',
        'border_focus': '#007AFF',
        'border_blue': '#007AFF',
        'border_green': '#34C759',
        'border_orange': '#FF9500',
        'border_purple': '#AF52DE',

        # 分隔线
        'separator': '#E5E5EA',
    }

    # 深色模式颜色 (Dark Mode)
    DARK = {
        # 背景色
        'bg_primary': '#1C1C1E',           # 主背景
        'bg_secondary': '#2C2C2E',          # 次要背景
        'bg_tertiary': '#3A3A3C',           # 三级背景
        'bg_elevated': '#2C2C2E',           # 浮起元素

        # 文本色
        'text_primary': '#FFFFFF',          # 主文本
        'text_secondary': '#8E8E93',        # 次要文本 - 60% opacity
        'text_tertiary': '#48484A',         # 三级文本 - 30% opacity
        'text_disabled': '#48484A',         # 禁用文本

        # 强调色 (SF Colors - Dark)
        'accent_blue': '#0A84FF',           # 蓝色
        'accent_blue_hover': '#409CFF',
        'accent_green': '#30D158',          # 绿色
        'accent_orange': '#FF9F0A',         # 橙色
        'accent_red': '#FF453A',            # 红色

        # 语义色
        'success': '#30D158',
        'warning': '#FF9F0A',
        'error': '#FF453A',
        'info': '#0A84FF',

        # 边框色
        'border': '#3A3A3C',
        'border_focus': '#0A84FF',

        # 分隔线
        'separator': '#3A3A3C',
    }

    # ==================== 圆角半径 ====================

    CORNER_RADIUS = {
        'small': 6,      # 小元素 - 按钮、标签
        'medium': 10,    # 中等元素 - 卡片、输入框
        'large': 16,     # 大元素 - 面板
        'xlarge': 24,    # 超大 - 模态框
    }

    # ==================== 间距系统 ====================

    SPACING = {
        'xs': 4,         # 极小间距
        'sm': 8,         # 小间距
        'md': 12,        # 中等间距
        'lg': 16,        # 大间距
        'xl': 24,        # 超大间距
        'xxl': 32,       # 极大间距
    }

    PADDING = {
        'sm': 12,        # 小内边距
        'md': 16,        # 中内边距
        'lg': 20,        # 大内边距
        'xl': 24,        # 超大内边距
    }

    # ==================== 字体层级 ====================

    # 推荐字体栈
    FONT_FAMILY = "Segoe UI"

    # 字体大小
    FONT_SIZE = {
        'caption': 11,       # 说明文字
        'body': 13,          # 正文
        'subheadline': 14,   # 副标题
        'headline': 16,      # 标题
        'title': 20,         # 小标题
        'large_title': 28,   # 大标题
    }

    # ==================== 动画时长 ====================

    DURATION = {
        'fast': 150,         # 快速过渡 - 按钮 hover
        'normal': 200,       # 正常过渡 - 标签切换
        'slow': 300,         # 慢速过渡 - 入场动画
        'slower': 500,       # 更慢 - 复杂动画
    }

    # ==================== 阴影/边框 ====================

    # CustomTkinter 不支持真阴影，用边框模拟
    BORDER_WIDTH = {
        'none': 0,
        'thin': 1,
        'medium': 2,
        'thick': 3,
    }

    @classmethod
    def get_colors(cls, appearance_mode: str = None) -> dict:
        """
        获取当前模式的颜色

        Args:
            appearance_mode: 主题模式 ('System', 'Light', 'Dark')
                            如果为 None，使用 CTk 当前设置
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
            key: 颜色键名 (如 'bg_primary', 'accent_blue')
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
        return cls.CORNER_RADIUS.get(size, 10)

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
        return cls.FONT_SIZE.get(level, 13)

    @classmethod
    def get_font(cls, level: str = 'body', weight: str = 'normal') -> ctk.CTkFont:
        """
        获取字体对象

        Args:
            level: 字体层级 (caption, body, subheadline, headline, title, large_title)
            weight: 字重 (normal, bold)
        """
        size = cls.get_font_size(level)
        weight_val = 'bold' if weight == 'bold' else 'normal'
        return ctk.CTkFont(size=size, weight=weight_val)

    @classmethod
    def apply_card_style(cls, widget, hover: bool = False, color_variant: str = 'default'):
        """
        应用卡片样式到组件

        Args:
            widget: CTk 组件
            hover: 是否悬停状态
            color_variant: 颜色变体 ('default', 'blue', 'green', 'orange', 'purple', 'pink')
        """
        colors = cls.get_colors()

        # 根据变体选择边框色
        border_colors = {
            'default': cls.color('separator'),
            'blue': cls.color('border_blue'),
            'green': cls.color('border_green'),
            'orange': cls.color('border_orange'),
            'purple': cls.color('border_purple'),
            'pink': cls.color('accent_pink'),
        }
        border_color = border_colors.get(color_variant, cls.color('separator'))

        widget.configure(
            corner_radius=cls.get_corner_radius('medium'),
            fg_color=cls.color('bg_secondary'),
            border_width=2 if color_variant != 'default' else cls.BORDER_WIDTH['thin'],
            border_color=border_color,
        )

    @classmethod
    def get_gradient_colors(cls, appearance_mode: str = None) -> tuple:
        """获取渐变颜色"""
        if appearance_mode is None:
            appearance_mode = ctk.get_appearance_mode()

        if appearance_mode == 'Dark':
            return ('#1a1a2e', '#16213e')
        return (cls.LIGHT['bg_gradient_start'], cls.LIGHT['bg_gradient_end'])

    @classmethod
    def apply_button_style(cls, widget, style: str = 'primary'):
        """
        应用按钮样式

        Args:
            widget: CTkButton 组件
            style: 样式类型 ('primary', 'secondary', 'success', 'danger', 'ghost')
        """
        colors = cls.get_colors()

        style_map = {
            'primary': {
                'fg_color': cls.color('accent_blue'),
                'hover_color': cls.color('accent_blue_hover'),
                'text_color': (cls.LIGHT['text_primary'], cls.DARK['text_primary']),
                'corner_radius': cls.get_corner_radius('small'),
            },
            'secondary': {
                'fg_color': cls.color('bg_tertiary'),
                'hover_color': cls.color('bg_secondary'),
                'text_color': cls.color('text_primary'),
                'corner_radius': cls.get_corner_radius('small'),
            },
            'success': {
                'fg_color': cls.color('success'),
                'hover_color': ('#28A745', '#248A3D'),
                'text_color': (cls.LIGHT['text_primary'], cls.DARK['text_primary']),
                'corner_radius': cls.get_corner_radius('small'),
            },
            'danger': {
                'fg_color': cls.color('error'),
                'hover_color': ('#D32F2F', '#C62828'),
                'text_color': (cls.LIGHT['text_primary'], cls.DARK['text_primary']),
                'corner_radius': cls.get_corner_radius('small'),
            },
            'ghost': {
                'fg_color': 'transparent',
                'hover_color': cls.color('bg_tertiary'),
                'text_color': cls.color('text_primary'),
                'border_width': cls.BORDER_WIDTH['thin'],
                'border_color': cls.color('border'),
                'corner_radius': cls.get_corner_radius('small'),
            },
        }

        style_config = style_map.get(style, style_map['primary'])
        widget.configure(**style_config)

    @classmethod
    def apply_input_style(cls, widget):
        """
        应用输入框样式

        Args:
            widget: CTkEntry 组件
        """
        widget.configure(
            corner_radius=cls.get_corner_radius('small'),
            border_width=cls.BORDER_WIDTH['thin'],
            border_color=cls.color('border'),
            height=36,
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
            'running': cls.color('accent_blue'),
        }
        return status_map.get(status, cls.color('text_primary'))


# 便捷函数
def get_color(key: str, mode: str = None) -> tuple:
    """快捷获取颜色"""
    return AppleTheme.color(key, mode)


def get_font(level: str = 'body', weight: str = 'normal') -> ctk.CTkFont:
    """快捷获取字体"""
    return AppleTheme.get_font(level, weight)


def get_spacing(size: str = 'md') -> int:
    """快捷获取间距"""
    return AppleTheme.get_spacing(size)


def get_corner_radius(size: str = 'medium') -> int:
    """快捷获取圆角"""
    return AppleTheme.get_corner_radius(size)
