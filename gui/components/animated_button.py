"""
Fluent Design 动画按钮

带有平滑悬停和点击动画效果的按钮组件
使用 Windows 11 Fluent Design 风格
"""
import customtkinter as ctk
from ..utils.apple_theme import AppleTheme
from ..utils.fluent_theme import FluentTheme as Fluent
from ..utils.animation import ScaleAnimation, Easing


class AnimatedButton(ctk.CTkButton):
    """苹果风格动画按钮"""

    def __init__(
        self,
        master,
        style: str = 'primary',
        scale_on_hover: bool = True,
        scale_on_click: bool = True,
        **kwargs
    ):
        """
        初始化动画按钮

        Args:
            master: 父容器
            style: 按钮样式 ('primary', 'secondary', 'success', 'danger', 'ghost')
            scale_on_hover: 悬停时是否缩放
            scale_on_click: 点击时是否缩放
            **kwargs: 其他 CTkButton 参数
        """
        # 应用主题样式
        self._style = style
        self._scale_on_hover = scale_on_hover
        self._scale_on_click = scale_on_click
        self._current_animation = None
        self._is_pressed = False

        # 获取主题配置 - 使用 Fluent 主题
        corner_radius = kwargs.pop('corner_radius', Fluent.get_corner_radius('small'))  # 4px (from 6px)

        # 根据样式设置默认颜色
        style_defaults = self._get_style_defaults(style)
        for key, value in style_defaults.items():
            kwargs.setdefault(key, value)

        kwargs.setdefault('corner_radius', corner_radius)

        super().__init__(master, **kwargs)

        # 绑定事件
        if scale_on_hover:
            self.bind('<Enter>', self._on_enter)
            self.bind('<Leave>', self._on_leave)

        if scale_on_click:
            self.bind('<ButtonPress-1>', self._on_press)
            self.bind('<ButtonRelease-1>', self._on_release)

    def _get_style_defaults(self, style: str) -> dict:
        """获取样式的默认配置 - 使用 Fluent 主题"""
        return {
            'primary': {
                'fg_color': Fluent.color('accent_primary'),  # Windows 11 蓝色
                'hover_color': Fluent.color('accent_hover'),
                'text_color': (Fluent.LIGHT['text_on_accent'], Fluent.DARK['text_on_accent']),
                'height': Fluent.HEIGHT['button'],  # 36px
            },
            'secondary': {
                'fg_color': Fluent.color('bg_layer_2'),
                'hover_color': Fluent.color('bg_layer_3'),
                'text_color': Fluent.color('text_primary'),
                'height': Fluent.HEIGHT['button'],
            },
            'success': {
                'fg_color': Fluent.color('success'),
                'hover_color': ('#0E6F0E', '#0A5A0A'),  # 更深的绿色
                'text_color': (Fluent.LIGHT['text_on_accent'], Fluent.DARK['text_on_accent']),
                'height': Fluent.HEIGHT['button'],
            },
            'danger': {
                'fg_color': Fluent.color('error'),
                'hover_color': ('#A52A2A', '#8B2222'),  # 更深的红色
                'text_color': (Fluent.LIGHT['text_on_accent'], Fluent.DARK['text_on_accent']),
                'height': Fluent.HEIGHT['button'],
            },
            'ghost': {
                'fg_color': 'transparent',
                'hover_color': Fluent.color('bg_layer_2'),
                'text_color': Fluent.color('text_primary'),
                'border_width': Fluent.get_border_width('thin'),  # 1px
                'border_color': Fluent.color('border_default'),
                'height': Fluent.HEIGHT['button'],
            },
        }.get(style, {})

    def _on_enter(self, event=None):
        """悬停进入 - 轻微放大"""
        if self._is_pressed or not self._scale_on_hover:
            return

        # 取消之前的动画
        if self._current_animation and self._current_animation.is_running():
            self._current_animation.stop()

        # 启动缩放动画
        self._current_animation = ScaleAnimation(
            self,
            from_scale=1.0,
            to_scale=1.02,
            duration=100,  # 更快的响应
            easing=Easing.ease_out_quad
        )
        self._current_animation.start()

    def _on_leave(self, event=None):
        """悬停离开 - 恢复原大小"""
        if self._is_pressed or not self._scale_on_hover:
            return

        # 取消之前的动画
        if self._current_animation and self._current_animation.is_running():
            self._current_animation.stop()

        # 启动缩放动画（恢复）
        self._current_animation = ScaleAnimation(
            self,
            from_scale=1.02,
            to_scale=1.0,
            duration=100,  # 更快的恢复
            easing=Easing.ease_out_quad
        )
        self._current_animation.start()

    def _on_press(self, event=None):
        """按下 - 缩小"""
        if not self._scale_on_click:
            return

        self._is_pressed = True

        # 取消之前的动画
        if self._current_animation and self._current_animation.is_running():
            self._current_animation.stop()

        # 启动缩小动画
        self._current_animation = ScaleAnimation(
            self,
            from_scale=1.0,
            to_scale=0.96,
            duration=80,  # 更快的点击响应
            easing=Easing.ease_out_quad
        )
        self._current_animation.start()

    def _on_release(self, event=None):
        """释放 - 恢复"""
        if not self._scale_on_click:
            return

        self._is_pressed = False

        # 取消之前的动画
        if self._current_animation and self._current_animation.is_running():
            self._current_animation.stop()

        # 启动恢复动画
        self._current_animation = ScaleAnimation(
            self,
            from_scale=0.96,
            to_scale=1.0,
            duration=120,  # 更平滑的恢复
            easing=Easing.ease_out_back
        )
        self._current_animation.start()


class AnimatedSegmentedButton(ctk.CTkSegmentedButton):
    """Fluent 风格动画分段按钮"""

    def __init__(self, master, **kwargs):
        # 应用 Fluent 主题 - 使用更小的圆角
        corner_radius = kwargs.pop('corner_radius', Fluent.get_corner_radius('small'))  # 4px
        kwargs.setdefault('corner_radius', corner_radius)

        # CTkSegmentedButton 只接受这些颜色参数
        colors = Fluent.get_colors()
        if ctk.get_appearance_mode() == 'Dark':
            kwargs.setdefault('fg_color', colors['bg_layer_2'])
            kwargs.setdefault('text_color', colors['text_primary'])
            kwargs.setdefault('text_color_disabled', colors['text_disabled'])
        else:
            kwargs.setdefault('fg_color', Fluent.color('bg_layer_2'))  # #EDEDED
            kwargs.setdefault('text_color', '#000000')
            kwargs.setdefault('text_color_disabled', Fluent.color('text_disabled'))

        super().__init__(master, **kwargs)


class AnimatedSwitch(ctk.CTkSwitch):
    """Fluent 风格动画开关"""

    def __init__(self, master, **kwargs):
        # 应用 Fluent 主题
        corner_radius = kwargs.pop('corner_radius', Fluent.get_corner_radius('small'))  # 4px
        kwargs.setdefault('corner_radius', corner_radius)

        # Fluent 风格的颜色 - 统一蓝色
        kwargs.setdefault('progress_color', Fluent.color('accent_primary'))
        kwargs.setdefault('button_color', Fluent.color('surface_primary'))
        kwargs.setdefault('button_hover_color', Fluent.color('bg_layer_2'))

        super().__init__(master, **kwargs)
