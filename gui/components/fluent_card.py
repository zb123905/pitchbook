"""
Fluent Design 卡片组件

带有层次感和阴影效果的卡片组件
"""
import customtkinter as ctk
from ..utils.fluent_theme import FluentTheme, get_color, get_spacing, get_corner_radius


class FluentCard(ctk.CTkFrame):
    """
    Fluent Design 卡片组件

    模拟 Fluent Design 的层次感：
    - elevation=0: 无阴影，与背景融合
    - elevation=1: 浮起，带细微边框
    - elevation=2: 更明显浮起，带蓝色边框
    - elevation=3: 最高浮起，用于强调
    """

    # 边框颜色映射（基于 elevation）
    BORDER_COLORS = {
        0: 'transparent',
        1: 'border_default',
        2: 'accent_primary',
        3: 'accent_primary',
    }

    # 背景颜色映射（基于 elevation）
    BG_COLORS = {
        0: 'bg_layer_1',
        1: 'surface_primary',
        2: 'surface_primary',
        3: 'surface_primary',
    }

    def __init__(
        self,
        master,
        elevation: int = 1,
        hoverable: bool = False,
        **kwargs
    ):
        """
        初始化 Fluent 卡片

        Args:
            master: 父容器
            elevation: 层次级别 (0-3)
            hoverable: 是否支持悬停效果
            **kwargs: 其他 CTkFrame 参数
        """
        self._elevation = max(0, min(3, elevation))
        self._hoverable = hoverable
        self._is_hovered = False

        # 获取主题配置
        bg_color_key = self.BG_COLORS[self._elevation]
        border_color_key = self.BORDER_COLORS[self._elevation]

        # 设置边框宽度
        border_width = 0 if self._elevation == 0 else (
            2 if self._elevation >= 2 else FluentTheme.get_border_width('thin')
        )

        # 设置默认样式
        kwargs.setdefault('corner_radius', FluentTheme.get_corner_radius('medium'))
        kwargs.setdefault('fg_color', FluentTheme.color(bg_color_key))

        if border_width > 0:
            kwargs.setdefault('border_width', border_width)
            kwargs.setdefault('border_color', FluentTheme.color(border_color_key))

        super().__init__(master, **kwargs)

        # 绑定悬停事件
        if hoverable and self._elevation > 0:
            self.bind('<Enter>', self._on_enter)
            self.bind('<Leave>', self._on_leave)

    def _on_enter(self, event=None):
        """悬停进入 - 增加高亮"""
        if not self._hoverable or self._is_hovered:
            return

        self._is_hovered = True
        self.configure(
            border_color=FluentTheme.color('accent_hover')
        )

    def _on_leave(self, event=None):
        """悬停离开 - 恢复原样"""
        if not self._hoverable or not self._is_hovered:
            return

        self._is_hovered = False
        border_color_key = self.BORDER_COLORS[self._elevation]
        self.configure(
            border_color=FluentTheme.color(border_color_key)
        )

    def set_elevation(self, elevation: int):
        """
        动态设置层次级别

        Args:
            elevation: 新的层次级别 (0-3)
        """
        self._elevation = max(0, min(3, elevation))

        bg_color_key = self.BG_COLORS[self._elevation]
        border_color_key = self.BORDER_COLORS[self._elevation]

        border_width = 0 if self._elevation == 0 else (
            2 if self._elevation >= 2 else FluentTheme.get_border_width('thin')
        )

        self.configure(
            fg_color=FluentTheme.color(bg_color_key),
            border_width=border_width,
            border_color=FluentTheme.color(border_color_key)
        )


class FluentContentCard(FluentCard):
    """
    Fluent 内容卡片

    预设样式的卡片，包含标题区域
    """

    def __init__(
        self,
        master,
        title: str = "",
        icon: str = "",
        elevation: int = 1,
        **kwargs
    ):
        """
        初始化内容卡片

        Args:
            master: 父容器
            title: 卡片标题
            icon: 图标（emoji 或文字）
            elevation: 层次级别
            **kwargs: 其他参数
        """
        super().__init__(master, elevation=elevation, **kwargs)

        # 内容容器
        self._content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._content_frame.pack(fill="both", expand=True, padx=FluentTheme.get_padding('sm'), pady=FluentTheme.get_padding('sm'))

        # 如果有标题或图标，创建头部
        if title or icon:
            self._header = self._create_header(title, icon)
        else:
            self._header = None

    def _create_header(self, title: str, icon: str):
        """创建卡片头部"""
        header = ctk.CTkFrame(self._content_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, FluentTheme.get_spacing('sm')))

        if icon:
            # 简洁的图标显示（无圆圈背景）
            icon_label = ctk.CTkLabel(
                header,
                text=icon,
                font=ctk.CTkFont(size=16),
                text_color=FluentTheme.color('accent_primary')
            )
            icon_label.pack(side="left", padx=(0, FluentTheme.get_spacing('xs')))

        if title:
            title_label = ctk.CTkLabel(
                header,
                text=title,
                font=FluentTheme.get_font('title', 'bold'),
                text_color=FluentTheme.color('text_primary'),
                anchor="w"
            )
            title_label.pack(side="left")

        return header

    def get_content_frame(self):
        """获取内容框架，用于添加自定义组件"""
        return self._content_frame

    def add_widget(self, widget, **pack_kwargs):
        """添加组件到内容区域"""
        widget.pack(in_=self._content_frame, **pack_kwargs)


class FluentStatCard(FluentCard):
    """
    Fluent 统计卡片

    用于显示数字统计的紧凑卡片
    """

    def __init__(
        self,
        master,
        label: str,
        value: str = "0",
        icon: str = "",
        elevation: int = 1,
        **kwargs
    ):
        """
        初始化统计卡片

        Args:
            master: 父容器
            label: 标签文本
            value: 数值文本
            icon: 图标
            elevation: 层次级别
            **kwargs: 其他参数
        """
        super().__init__(master, elevation=elevation, **kwargs)

        # 主内容
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=FluentTheme.get_padding('md'), pady=FluentTheme.get_padding('md'))

        # 顶部行：图标 + 数值
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x")

        if icon:
            icon_label = ctk.CTkLabel(
                top_row,
                text=icon,
                font=ctk.CTkFont(size=18),
                text_color=FluentTheme.color('accent_primary')
            )
            icon_label.pack(side="left")

        self.value_label = ctk.CTkLabel(
            top_row,
            text=value,
            font=FluentTheme.get_font('display', 'bold'),
            text_color=FluentTheme.color('text_primary')
        )
        self.value_label.pack(side="right")

        # 底部标签
        self.label_widget = ctk.CTkLabel(
            content,
            text=label,
            font=FluentTheme.get_font('body'),
            text_color=FluentTheme.color('text_secondary'),
            anchor="w"
        )
        self.label_widget.pack(fill="x", pady=(FluentTheme.get_spacing('xs'), 0))

    def set_value(self, value: str):
        """更新数值"""
        self.value_label.configure(text=value)

    def set_label(self, label: str):
        """更新标签"""
        self.label_widget.configure(text=label)
