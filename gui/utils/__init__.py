"""Utils package"""
from .thread_safe_notifier import (
    ThreadSafeNotifier,
    ProgressEvent,
    LogEvent,
    CompleteEvent,
    StatsEvent
)
from .apple_theme import (
    AppleTheme,
    get_color,
    get_font,
    get_spacing,
    get_corner_radius
)
from .animation import (
    AnimationManager,
    fade_in,
    fade_out,
    scale,
    animate_value,
    Easing
)
from .modern_theme import (
    ModernTheme
)

__all__ = [
    'ThreadSafeNotifier',
    'ProgressEvent',
    'LogEvent',
    'CompleteEvent',
    'StatsEvent',
    'AppleTheme',
    'get_color',
    'get_font',
    'get_spacing',
    'get_corner_radius',
    'AnimationManager',
    'fade_in',
    'fade_out',
    'scale',
    'animate_value',
    'Easing',
    'ModernTheme'
]
