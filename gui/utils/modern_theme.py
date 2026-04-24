"""
2025 现代主题系统

集成多种设计风格：
- Bento Grid 布局
- Cyberpunk 霓虹效果
- Glassmorphism 毛玻璃
- Bold Typography 大字体
- 3D Depth 深度效果
"""
import customtkinter as ctk
from typing import Tuple, List


class ModernTheme:
    """2025 现代主题系统"""

    # ==================== 霓虹配色方案 (Cyberpunk) ====================

    NEON_COLORS = {
        # 霓虹色
        'neon_pink': '#FF006E',
        'neon_blue': '#00F0FF',
        'neon_purple': '#B537F2',
        'neon_green': '#39FF14',
        'neon_orange': '#FF6B35',
        'neon_yellow': '#FFD23F',

        # 深色背景
        'cyber_dark': '#0A0E27',
        'cyber_darker': '#050714',
        'cyber_card': '#151932',

        # 渐变色组合
        'gradient_sunset': ['#FF006E', '#FF6B35', '#FFD23F'],
        'gradient_ocean': ['#00F0FF', '#0099FF', '#B537F2'],
        'gradient_forest': ['#39FF14', '#00FF99', '#00F0FF'],
    }

    # ==================== 毛玻璃效果 (Glassmorphism) ====================

    GLASS_STYLES = {
        'light': {
            'bg': 'rgba(255, 255, 255, 0.25)',
            'border': 'rgba(255, 255, 255, 0.5)',
            'blur': 20,
        },
        'dark': {
            'bg': 'rgba(30, 30, 40, 0.6)',
            'border': 'rgba(255, 255, 255, 0.1)',
            'blur': 20,
        },
        'colored': {
            'bg': 'rgba(0, 240, 255, 0.1)',
            'border': 'rgba(0, 240, 255, 0.3)',
            'blur': 15,
        }
    }

    # ==================== Bento Grid 布局 ====================

    BENTO_LAYOUTS = {
        # 配置面板 - 3列网格
        'config_grid': [
            {'col': 0, 'row': 0, 'colspan': 1, 'rowspan': 1, 'title': '邮箱', 'color': '#00F0FF'},
            {'col': 1, 'row': 0, 'colspan': 1, 'rowspan': 1, 'title': '爬虫', 'color': '#FF6B35'},
            {'col': 2, 'row': 0, 'colspan': 1, 'rowspan': 1, 'title': '分析', 'color': '#B537F2'},
            {'col': 0, 'row': 1, 'colspan': 3, 'rowspan': 1, 'title': '操作', 'color': '#39FF14'},
        ],
        # 进度面板 - 垂直堆叠
        'progress_stack': [
            {'height': 120, 'title': '总进度', 'color': '#00F0FF'},
            {'height': 400, 'title': '执行步骤', 'color': 'transparent'},
            {'height': 100, 'title': '实时统计', 'color': '#B537F2'},
        ],
    }

    # ==================== 3D 效果阴影 ====================

    SHADOW_STYLES = {
        'floating': {
            'light': [
                {'offset': (0, -4), 'blur': 12, 'color': 'rgba(255,255,255,0.8)'},
                {'offset': (0, 4), 'blur': 12, 'color': 'rgba(0,0,0,0.1)'},
            ],
            'dark': [
                {'offset': (0, -4), 'blur': 12, 'color': 'rgba(255,255,255,0.05)'},
                {'offset': (0, 4), 'blur': 12, 'color': 'rgba(0,0,0,0.4)'},
            ],
        },
        'pressed': {
            'offset': (0, 2), 'blur': 4, 'color': 'rgba(0,0,0,0.2)'
        },
        'glowing': {
            'offset': (0, 0), 'blur': 20, 'color': 'rgba(0, 240, 255, 0.5)'
        }
    }

    # ==================== 字体层级 (Bold Typography) ====================

    TYPOGRAPHY = {
        'display': {'size': 48, 'weight': 'bold', 'lettering': -1},
        'h1': {'size': 36, 'weight': 'bold', 'lettering': -0.5},
        'h2': {'size': 28, 'weight': 'bold', 'lettering': -0.5},
        'h3': {'size': 22, 'weight': 'semibold', 'lettering': 0},
        'body_large': {'size': 17, 'weight': 'normal', 'lettering': 0},
        'body': {'size': 15, 'weight': 'normal', 'lettering': 0},
        'caption': {'size': 13, 'weight': 'normal', 'lettering': 0},
        'small': {'size': 11, 'weight': 'normal', 'lettering': 0.2},
    }

    # ==================== 渐变预设 ====================

    GRADIENTS = {
        'neon_sunset': {
            'colors': ['#FF006E', '#FF6B35', '#FFD23F'],
            'angle': 135,
        },
        'cyber_blue': {
            'colors': ['#00F0FF', '#0099FF', '#B537F2'],
            'angle': 45,
        },
        'matrix_green': {
            'colors': ['#39FF14', '#00FF99', '#00CC66'],
            'angle': 90,
        },
        'sunset_vibes': {
            'colors': ['#FF6B35', '#FF006E', '#B537F2'],
            'angle': 180,
        },
        'ocean_depth': {
            'colors': ['#00F0FF', '#0066FF', '#B537F2'],
            'angle': 135,
        },
    }

    @classmethod
    def get_neon_color(cls, name: str) -> str:
        """获取霓虹颜色"""
        return cls.NEON_COLORS.get(name, '#00F0FF')

    @classmethod
    def get_gradient(cls, name: str) -> dict:
        """获取渐变配置"""
        return cls.GRADIENTS.get(name, cls.GRADIENTS['cyber_blue'])

    @classmethod
    def create_bento_item(cls, parent, title: str, color: str, colspan: int = 1, rowspan: int = 1):
        """创建 Bento Grid 项目"""
        from ..utils.apple_theme import AppleTheme, get_corner_radius

        frame = ctk.CTkFrame(
            parent,
            corner_radius=get_corner_radius('large'),
            fg_color=color if color != 'transparent' else AppleTheme.color('bg_secondary'),
            border_width=2 if color != 'transparent' else AppleTheme.BORDER_WIDTH['thin'],
            border_color=color if color != 'transparent' else AppleTheme.color('separator'),
        )

        # 添加发光效果（通过多层边框模拟）
        if color != 'transparent' and color.startswith('#'):
            # 内边框模拟发光
            inner = ctk.CTkFrame(
                frame,
                corner_radius=get_corner_radius('large') - 2,
                fg_color=AppleTheme.color('bg_primary'),
            )
            inner.pack(fill="both", expand=True, padx=2, pady=2)
            return frame, inner

        return frame, frame

    @classmethod
    def apply_neon_style(cls, widget, color: str = '#00F0FF'):
        """应用霓虹风格到组件"""
        from ..utils.apple_theme import AppleTheme, get_corner_radius

        widget.configure(
            corner_radius=get_corner_radius('medium'),
            fg_color=AppleTheme.color('bg_primary'),
            border_width=2,
            border_color=color,
        )

    @classmethod
    def create_gradient_button(cls, parent, text: str, command, gradient_name: str = 'cyber_blue'):
        """创建渐变按钮"""
        from ..utils.apple_theme import AppleTheme, get_corner_radius, get_font
        from ..components import AnimatedButton

        gradient = cls.get_gradient(gradient_name)
        primary_color = gradient['colors'][0]

        # 使用主色作为按钮颜色
        btn = AnimatedButton(
            parent,
            text=text,
            command=command,
            width=140,
            height=44,
            font=get_font('subheadline', 'bold'),
            fg_color=(primary_color, primary_color),
            hover_color=(gradient['colors'][1], gradient['colors'][1]),
            text_color=('#000000', '#FFFFFF'),
            corner_radius=get_corner_radius('medium'),
        )
        return btn

    @classmethod
    def create_stat_card(cls, parent, title: str, value: str, icon: str, color: str):
        """创建统计卡片"""
        from ..utils.apple_theme import get_font, get_spacing, get_padding

        card = ctk.CTkFrame(
            parent,
            corner_radius=16,
            fg_color='transparent',
            border_width=2,
            border_color=color,
        )

        # 内容容器
        content = ctk.CTkFrame(
            card,
            corner_radius=14,
            fg_color=('#FAFAFA', '#1A1A2E'),
        )
        content.pack(fill="both", expand=True, padx=2, pady=2)

        # 图标圆圈
        icon_frame = ctk.CTkFrame(
            content,
            width=48,
            height=48,
            corner_radius=24,
            fg_color=color,
        )
        icon_frame.pack(side="left", padx=(16, 12), pady=16)
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=ctk.CTkFont(size=20)
        ).pack(expand=True)

        # 文字
        text_frame = ctk.CTkFrame(content, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, padx=(0, 16), pady=16)

        ctk.CTkLabel(
            text_frame,
            text=title,
            font=get_font('caption'),
            text_color=('#666666', '#8E8E93'),
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            text_frame,
            text=value,
            font=get_font('h3'),
            text_color=color,
            anchor="w"
        ).pack(fill="x")

        return card
