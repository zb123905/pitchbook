"""
Chart Configuration Module
Handles chart styling, colors, and Chinese font configuration
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import rcParams
import os
import logging

logger = logging.getLogger(__name__)


# Color schemes for different chart types
COLOR_SCHEMES = {
    'industry': {
        'AI/Machine Learning': '#FF6B6B',
        'FinTech': '#4ECDC4',
        'Healthcare': '#45B7D1',
        'CleanTech': '#96CEB4',
        'SaaS': '#FFEAA7',
        'E-commerce': '#DFE6E9',
        'Cybersecurity': '#74B9FF',
        'EdTech': '#A29BFE',
        'default': '#DDDDDD'
    },
    'deal_stage': {
        'Seed': '#E17055',
        'Series A': '#00CEC9',
        'Series B': '#0984E3',
        'Series C': '#6C5CE7',
        'Series D': '#FD79A8',
        'IPO': '#FDCB6E',
        'M&A': '#E84393',
        'default': '#B2BEC3'
    },
    'sentiment': {
        'positive': '#00B894',
        'neutral': '#DFE6E9',
        'negative': '#D63031'
    }
}

# Chart styling defaults
CHART_STYLE = {
    'figure.figsize': (12, 8),
    'figure.dpi': 100,
    'font.size': 10,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'lines.linewidth': 2,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.facecolor': '#FAFAFA'
}


def setup_chinese_font():
    """
    Configure matplotlib to display Chinese characters properly
    """
    # Try common Chinese fonts
    chinese_fonts = [
        'SimHei',           # 黑体
        'SimSun',           # 宋体
        'Microsoft YaHei',  # 微软雅黑
        'PingFang SC',      # macOS 中文字体
        'Noto Sans CJK SC', # Linux 中文字体
    ]

    font_found = False
    for font_name in chinese_fonts:
        try:
            # Test if font is available
            plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
            # Test rendering
            fig, ax = plt.subplots(figsize=(1, 1))
            ax.text(0.5, 0.5, '测试中文', fontsize=12)
            plt.close(fig)
            font_found = True
            logger.info(f"✓ Chinese font configured: {font_name}")
            break
        except:
            continue

    if not font_found:
        logger.warning("⚠ Chinese font not found, text may not display correctly")
        logger.warning("  Install Chinese fonts or specify font path manually")

    # Fix minus sign display (important for negative numbers)
    plt.rcParams['axes.unicode_minus'] = False

    return font_found


def get_color_for_label(label: str, scheme: str = 'industry') -> str:
    """
    Get color for a label based on predefined color scheme

    Args:
        label: The label to get color for
        scheme: Color scheme name ('industry', 'deal_stage', 'sentiment')

    Returns:
        Hex color code
    """
    scheme_colors = COLOR_SCHEMES.get(scheme, {})
    return scheme_colors.get(label, scheme_colors.get('default', '#DDDDDD'))


def apply_chart_style(style: dict = None):
    """
    Apply chart styling to matplotlib

    Args:
        style: Custom style dict (overrides defaults)
    """
    # Start with default style
    chart_style = CHART_STYLE.copy()

    # Override with custom style if provided
    if style:
        chart_style.update(style)

    # Apply to rcParams
    for key, value in chart_style.items():
        try:
            rcParams[key] = value
        except:
            logger.warning(f"Failed to set style: {key} = {value}")


def save_chart(fig, filepath: str, dpi: int = 300, bbox_inches: str = 'tight'):
    """
    Save chart to file with proper settings

    Args:
        fig: matplotlib figure object
        filepath: Output file path
        dpi: Resolution (default 300 for high quality)
        bbox_inches: Bounding box setting
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    try:
        fig.savefig(
            filepath,
            dpi=dpi,
            bbox_inches=bbox_inches,
            facecolor='white',
            edgecolor='none'
        )
        logger.info(f"✓ Chart saved: {filepath}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to save chart: {e}")
        return False


# Initialize on module load
setup_chinese_font()
apply_chart_style()
