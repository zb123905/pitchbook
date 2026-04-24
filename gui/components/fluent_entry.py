"""
Fluent Design 输入框组件

带有聚焦状态效果的输入框组件
"""
import customtkinter as ctk
from ..utils.fluent_theme import FluentTheme, get_color, get_spacing, get_corner_radius


class FluentEntry(ctk.CTkEntry):
    """
    Fluent Design 输入框

    特性：
    - 聚焦时边框变蓝并加粗
    - 悬停时边框颜色变化
    - 底部指示线（可选）
    """

    def __init__(
        self,
        master,
        show_indicator: bool = False,
        **kwargs
    ):
        """
        初始化 Fluent 输入框

        Args:
            master: 父容器
            show_indicator: 是否显示底部指示线
            **kwargs: 其他 CTkEntry 参数
        """
        self._show_indicator = show_indicator
        self._is_focused = False

        # 设置默认样式
        kwargs.setdefault('corner_radius', FluentTheme.get_corner_radius('small'))
        kwargs.setdefault('border_width', FluentTheme.get_border_width('thin'))
        kwargs.setdefault('border_color', FluentTheme.color('border_default'))
        kwargs.setdefault('height', FluentTheme.HEIGHT['input'])
        kwargs.setdefault('placeholder_text_color', FluentTheme.color('text_tertiary'))
        kwargs.setdefault('text_color', FluentTheme.color('text_primary'))
        kwargs.setdefault('fg_color', FluentTheme.color('surface_primary'))

        super().__init__(master, **kwargs)

        # 创建底部指示线（如果启用）
        self._indicator = None
        if show_indicator:
            self._create_indicator()

        # 绑定事件
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<FocusOut>', self._on_focus_out)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _create_indicator(self):
        """创建底部指示线"""
        self._indicator = ctk.CTkFrame(
            self,
            height=2,
            corner_radius=0,
            fg_color=FluentTheme.color('border_default')
        )
        self._indicator.place(x=0, rely=1.0, y=0, relwidth=1.0, anchor="sw")

    def _on_focus_in(self, event=None):
        """聚焦进入 - 边框变蓝加粗"""
        if self._is_focused:
            return

        self._is_focused = True

        # 更新边框
        self.configure(
            border_width=FluentTheme.get_border_width('medium'),
            border_color=FluentTheme.color('border_focus')
        )

        # 更新指示线
        if self._indicator:
            self._indicator.configure(
                fg_color=FluentTheme.color('accent_primary'),
                height=3
            )

    def _on_focus_out(self, event=None):
        """聚焦离开 - 恢复原样"""
        if not self._is_focused:
            return

        self._is_focused = False

        # 恢复边框
        self.configure(
            border_width=FluentTheme.get_border_width('thin'),
            border_color=FluentTheme.color('border_default')
        )

        # 恢复指示线
        if self._indicator:
            self._indicator.configure(
                fg_color=FluentTheme.color('border_default'),
                height=2
            )

    def _on_enter(self, event=None):
        """悬停进入"""
        if not self._is_focused:
            self.configure(border_color=FluentTheme.color('border_hover'))

    def _on_leave(self, event=None):
        """悬停离开"""
        if not self._is_focused:
            self.configure(border_color=FluentTheme.color('border_default'))


class FluentSearchEntry(FluentEntry):
    """
    Fluent 搜索输入框

    带有搜索图标的输入框
    """

    def __init__(self, master, **kwargs):
        """初始化搜索输入框"""
        # 创建容器
        self._container = ctk.CTkFrame(master, fg_color="transparent")

        # 搜索图标
        self._search_icon = ctk.CTkLabel(
            self._container,
            text="🔍",
            font=ctk.CTkFont(size=14),
            text_color=FluentTheme.color('text_tertiary')
        )
        self._search_icon.pack(side="left", padx=(FluentTheme.get_padding('sm'), 0))

        # 初始化输入框（不传入 master，稍后手动 pack）
        kwargs['show_indicator'] = kwargs.pop('show_indicator', False)
        super().__init__(self._container, **kwargs)
        self.pack(side="left", fill="x", expand=True, padx=(FluentTheme.get_spacing('xs'), FluentTheme.get_padding('sm')))

    def pack(self, **kwargs):
        """重写 pack 方法，使用容器"""
        self._container.pack(**kwargs)

    def grid(self, **kwargs):
        """重写 grid 方法，使用容器"""
        self._container.grid(**kwargs)

    def place(self, **kwargs):
        """重写 place 方法，使用容器"""
        self._container.place(**kwargs)


class FluentTextArea(ctk.CTkTextbox):
    """
    Fluent Design 文本区域

    多行文本输入，带聚焦效果
    """

    def __init__(self, master, **kwargs):
        """初始化文本区域"""
        self._is_focused = False

        # 设置默认样式
        kwargs.setdefault('corner_radius', FluentTheme.get_corner_radius('small'))
        kwargs.setdefault('border_width', FluentTheme.get_border_width('thin'))
        kwargs.setdefault('border_color', FluentTheme.color('border_default'))
        kwargs.setdefault('text_color', FluentTheme.color('text_primary'))
        kwargs.setdefault('fg_color', FluentTheme.color('surface_primary'))
        kwargs.setdefault('font', FluentTheme.get_font('body'))

        super().__init__(master, **kwargs)

        # 绑定事件
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<FocusOut>', self._on_focus_out)

    def _on_focus_in(self, event=None):
        """聚焦进入"""
        if self._is_focused:
            return

        self._is_focused = True
        self.configure(
            border_width=FluentTheme.get_border_width('medium'),
            border_color=FluentTheme.color('border_focus')
        )

    def _on_focus_out(self, event=None):
        """聚焦离开"""
        if not self._is_focused:
            return

        self._is_focused = False
        self.configure(
            border_width=FluentTheme.get_border_width('thin'),
            border_color=FluentTheme.color('border_default')
        )
