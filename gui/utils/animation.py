"""
动画工具库

提供苹果风格的平滑动画效果
"""
import customtkinter as ctk
from typing import Callable, Optional, List, Any, TYPE_CHECKING
from abc import ABC, abstractmethod
import math

if TYPE_CHECKING:
    # 仅用于类型检查
    class TkWidget:
        def after(self, ms: int, func: Callable) -> str: ...
        def after_cancel(self, id: str) -> None: ...
else:
    # 运行时使用 Any
    TkWidget = Any


# ==================== 缓动函数 ====================

class Easing:
    """缓动函数集合"""

    @staticmethod
    def linear(t: float) -> float:
        """线性 - 无缓动"""
        return t

    @staticmethod
    def ease_in_quad(t: float) -> float:
        """缓入 - 加速"""
        return t * t

    @staticmethod
    def ease_out_quad(t: float) -> float:
        """缓出 - 减速"""
        return t * (2 - t)

    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """缓入缓出 - 先加速后减速"""
        if t < 0.5:
            return 2 * t * t
        return 1 - pow(-2 * t + 2, 2) / 2

    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """三次缓入"""
        return t * t * t

    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """三次缓出"""
        return 1 - pow(1 - t, 3)

    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """三次缓入缓出"""
        if t < 0.5:
            return 4 * t * t * t
        return 1 - pow(-2 * t + 2, 3) / 2

    @staticmethod
    def ease_out_elastic(t: float) -> float:
        """弹性缓出"""
        if t == 0 or t == 1:
            return t
        return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1

    @staticmethod
    def ease_out_back(t: float) -> float:
        """回弹缓出"""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


# ==================== 动画基类 ====================

class Animation(ABC):
    """动画基类"""

    def __init__(
        self,
        widget: Any,
        duration: int = 200,
        easing: Callable[[float], float] = Easing.ease_in_out_quad,
        on_complete: Optional[Callable] = None
    ):
        """
        初始化动画

        Args:
            widget: 要动画的组件 (CTkButton, CTkLabel等)
            duration: 动画时长（毫秒）
            easing: 缓动函数
            on_complete: 动画完成回调
        """
        self.widget = widget
        self.duration = duration
        self.easing = easing
        self.on_complete = on_complete
        self._is_running = False
        self._start_time = None
        self._after_id = None

    def start(self) -> 'Animation':
        """启动动画"""
        if self._is_running:
            return self

        self._is_running = True
        self._start_time = None
        self._animate(0)
        return self

    def stop(self):
        """停止动画"""
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        self._is_running = False

    def _animate(self, elapsed: int):
        """动画帧处理"""
        if self._start_time is None:
            self._start_time = elapsed

        progress = min(elapsed - self._start_time, self.duration) / self.duration
        eased_progress = self.easing(progress)

        self._update(eased_progress)

        if progress < 1:
            self._after_id = self.widget.after(20, self._animate)  # 50fps - 更流畅且 CPU 占用更低
        else:
            self._is_running = False
            self._finish()
            if self.on_complete:
                self.on_complete()

    @abstractmethod
    def _update(self, progress: float):
        """更新动画状态 - 子类实现"""
        pass

    def _finish(self):
        """动画完成处理"""
        self._update(1.0)

    def is_running(self) -> bool:
        """动画是否正在运行"""
        return self._is_running


# ==================== 具体动画类型 ====================

class FadeAnimation(Animation):
    """淡入淡出动画

    注: CustomTkinter 不直接支持透明度动画
    这里通过改变文本颜色来模拟淡入淡出效果
    """

    def __init__(
        self,
        widget: Any,
        fade_in: bool = True,
        duration: int = 200,
        from_color: tuple = None,
        to_color: tuple = None,
        on_complete: Optional[Callable] = None
    ):
        super().__init__(widget, duration, on_complete=on_complete)
        self.fade_in = fade_in
        self.from_color = from_color
        self.to_color = to_color

    def _update(self, progress: float):
        # 对于 CTkLabel，我们可以模拟淡入淡出
        if isinstance(self.widget, ctk.CTkLabel):
            if self.to_color:
                # 颜色过渡
                from_rgb = self._hex_to_rgb(self.from_color[0]) if self.from_color else (200, 200, 200)
                to_rgb = self._hex_to_rgb(self.to_color[0]) if self.to_color else (0, 0, 0)

                current_rgb = (
                    int(from_rgb[0] + (to_rgb[0] - from_rgb[0]) * progress),
                    int(from_rgb[1] + (to_rgb[1] - from_rgb[1]) * progress),
                    int(from_rgb[2] + (to_rgb[2] - from_rgb[2]) * progress),
                )
                color = f'#{current_rgb[0]:02x}{current_rgb[1]:02x}{current_rgb[2]:02x}'
                self.widget.configure(text_color=(color, color))

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple:
        """十六进制颜色转 RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class ScaleAnimation(Animation):
    """缩放动画

    注: CustomTkinter 不直接支持缩放
    通过改变边框宽度和内边距模拟缩放效果
    """

    def __init__(
        self,
        widget: Any,
        from_scale: float = 1.0,
        to_scale: float = 1.05,
        duration: int = 150,
        easing: Callable[[float], float] = None,
        on_complete: Optional[Callable] = None
    ):
        if easing is None:
            easing = Easing.ease_out_back
        super().__init__(widget, duration, easing, on_complete)
        self.from_scale = from_scale
        self.to_scale = to_scale
        self._original_border = None
        self._original_padding = None

    def _update(self, progress: float):
        current_scale = self.from_scale + (self.to_scale - self.from_scale) * progress

        # 通过边框宽度模拟缩放
        if isinstance(self.widget, ctk.CTkButton):
            if self._original_border is None:
                try:
                    self._original_border = self.widget.cget('border_width')
                except:
                    self._original_border = 0

            # 缩放时减少边框
            new_border = max(0, self._original_border - (current_scale - 1.0) * 10)
            self.widget.configure(border_width=new_border)


class SlideAnimation(Animation):
    """滑动动画

    通过修改 place/pack 坐标实现位移动画
    """

    def __init__(
        self,
        widget: Any,
        from_x: float = 0,
        to_x: float = 0,
        from_y: float = 20,
        to_y: float = 0,
        duration: int = 300,
        on_complete: Optional[Callable] = None
    ):
        super().__init__(widget, duration, Easing.ease_out_cubic, on_complete)
        self.from_x = from_x
        self.to_x = to_x
        self.from_y = from_y
        self.to_y = to_y
        self._use_place = False

    def start(self) -> 'Animation':
        # 检查是否使用 place 布局
        try:
            self.widget.place_info()
            self._use_place = True
        except:
            self._use_place = False

        if not self._use_place:
            # 如果不是 place 布局，暂时不支持
            if self.on_complete:
                self.on_complete()
            return self

        return super().start()

    def _update(self, progress: float):
        if not self._use_place:
            return

        current_x = self.from_x + (self.to_x - self.from_x) * progress
        current_y = self.from_y + (self.to_y - self.from_y) * progress

        try:
            info = self.widget.place_info()
            relx = float(info.get('relx', 0)) if 'relx' in info else current_x / self.widget.winfo_screenwidth()
            rely = float(info.get('rely', 0)) if 'rely' in info else current_y / self.widget.winfo_screenheight()
            self.widget.place(relx=relx, rely=rely)
        except:
            pass


class ValueAnimation(Animation):
    """数值动画 - 用于数字滚动效果"""

    def __init__(
        self,
        from_value: float,
        to_value: float,
        update_callback: Callable[[float], Any],
        duration: int = 300,
        easing: Callable[[float], float] = Easing.ease_out_quad,
        on_complete: Optional[Callable] = None
    ):
        super().__init__(None, duration, easing, on_complete)
        self.from_value = from_value
        self.to_value = to_value
        self.update_callback = update_callback
        # 创建一个虚拟 widget 用于 after 调用
        import tkinter as tk
        self.widget = tk.Tk()
        self.widget.withdraw()

    def _update(self, progress: float):
        current_value = self.from_value + (self.to_value - self.from_value) * progress
        self.update_callback(current_value)


# ==================== 动画管理器 ====================

class AnimationManager:
    """动画管理器 - 用于编排多个动画"""

    def __init__(self):
        self.animations: List[Animation] = []
        self._sequences = []

    def add(self, animation: Animation) -> Animation:
        """添加单个动画"""
        self.animations.append(animation)
        return animation

    def parallel(self, *animations: Animation) -> 'AnimationManager':
        """并行执行多个动画"""
        self._sequences.append(('parallel', animations))
        return self

    def sequence(self, *animations: Animation) -> 'AnimationManager':
        """串行执行多个动画"""
        self._sequences.append(('sequence', animations))
        return self

    def start(self) -> 'AnimationManager':
        """启动所有动画"""
        for seq_type, animations in self._sequences:
            if seq_type == 'parallel':
                # 并行启动
                for anim in animations:
                    anim.start()
            else:  # sequence
                # 串行启动
                if animations:
                    self._start_sequence(animations)

        # 启动独立动画
        for anim in self.animations:
            anim.start()

        return self

    def _start_sequence(self, animations: List[Animation]):
        """启动串行动画序列"""
        if not animations:
            return

        def start_next(index=0):
            if index >= len(animations):
                return
            animations[index].on_complete = lambda: start_next(index + 1)
            animations[index].start()

        start_next()

    def stop_all(self):
        """停止所有动画"""
        for seq_type, animations in self._sequences:
            for anim in animations:
                anim.stop()
        for anim in self.animations:
            anim.stop()


# ==================== 便捷函数 ====================

def fade_in(
    widget: Any,
    duration: int = 200,
    on_complete: Optional[Callable] = None
) -> FadeAnimation:
    """淡入动画"""
    anim = FadeAnimation(widget, fade_in=True, duration=duration, on_complete=on_complete)
    anim.start()
    return anim


def fade_out(
    widget: Any,
    duration: int = 200,
    on_complete: Optional[Callable] = None
) -> FadeAnimation:
    """淡出动画"""
    anim = FadeAnimation(widget, fade_in=False, duration=duration, on_complete=on_complete)
    anim.start()
    return anim


def scale(
    widget: Any,
    to_scale: float = 1.05,
    duration: int = 150,
    on_complete: Optional[Callable] = None
) -> ScaleAnimation:
    """缩放动画"""
    anim = ScaleAnimation(widget, to_scale=to_scale, duration=duration, on_complete=on_complete)
    anim.start()
    return anim


def animate_value(
    from_value: float,
    to_value: float,
    update_callback: Callable[[float], Any],
    duration: int = 300
) -> ValueAnimation:
    """数值动画"""
    anim = ValueAnimation(from_value, to_value, update_callback, duration)
    anim.start()
    return anim
