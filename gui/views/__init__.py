"""Views package"""
from .config_panel import ConfigPanel
from .progress_panel import ProgressPanel
from .output_panel import OutputPanel
from .log_panel import LogPanel
from .dashboard_panel import ModernDashboardPanel
from .pitchbook_panel import PitchBookPanel

__all__ = [
    'ConfigPanel',
    'ProgressPanel',
    'OutputPanel',
    'LogPanel',
    'ModernDashboardPanel',
    'PitchBookPanel'
]
