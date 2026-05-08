"""SVG template: Mission Telemetry stats card (850x180, or 215 with activity)."""

from generator.utils import METRIC_ICONS, METRIC_LABELS, METRIC_COLORS, format_number

WIDTH = 850
HEIGHT_BASE = 180
HEIGHT_WITH_ACTIVITY = 215


def _build_sparkline(activity: list, width: int, theme: dict) -> str:
    if not activity:
        return ""

    left_pad = 85
    right_pad = 20
    bar_area_w = width - left_pad - right_pad
    n = len(activity)
    gap = 2
    bar_w = max(2.0, (bar_area_w - gap * (n - 1)) / n)
    max_val = max(activity) or 1
    max_bar_h = 22
    bar_bottom_y = 205
    cyan = theme.get("synapse_cyan", "#00d4ff")

    parts = [
        f'  <line x1="20" y1="162" x2="{width - 20}" y2="162" '
        f'stroke="{theme["star_dust"]}" stroke-width="1" opacity="0.5"/>',
        f'  <text x="20" y="184" fill="{theme["text_faint"]}" font-size="9" '
        f'font-family="monospace" letter-spacing="2" dominant-baseline="middle">ACTIVITY</text>',
    ]

    for i, count in enumerate(activity):
        bar_h = max(2.0, (count / max_val) * max_bar_h)
        bar_x = left_pad + i * (bar_w + gap)
        bar_y = bar_bottom_y - bar_h
        opacity = 0.15 + 0.75 * (count / max_val)
        parts.append(
            f'  <rect x="{bar_x:.1f}" y="{bar_y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" '
            f'rx="1" fill="{cyan}" opacity="{opacity:.2f}"/>'
        )

    return "\n".join(parts)


def render(stats: dict, metrics: list, theme: dict, activity: list = None) -> str:
    """Render the stats card SVG.

    Args:
        stats: dict with keys like commits, stars, prs, issues, repos
        metrics: list of metric keys to display
        theme: color palette dict
    """
    height = HEIGHT_WITH_ACTIVITY if activity else HEIGHT_BASE
    cell_width = WIDTH / len(metrics)
    divider_bottom = HEIGHT_WITH_ACTIVITY - 55 if activity else 155

    # Build metric cells
    cells = []
    dividers = []
    for i, key in enumerate(metrics):
        cx = cell_width * i + cell_width / 2
        icon_color = theme.get(METRIC_COLORS.get(key, "synapse_cyan"), "#00d4ff")
        value = format_number(stats.get(key, 0))
        label = METRIC_LABELS.get(key, key.title())
        icon_path = METRIC_ICONS.get(key, "")
        delay = f"{i * 0.3}s"

        cells.append(f'''    <g class="metric-cell">
      <g transform="translate({cx - 8:.1f}, 48)">
        <svg viewBox="0 0 16 16" width="16" height="16" fill="{icon_color}" class="metric-icon" style="animation-delay: {delay}">
          {icon_path}
        </svg>
      </g>
      <text x="{cx}" y="100" text-anchor="middle" fill="{icon_color}" font-size="26" font-weight="bold" font-family="sans-serif" opacity="0.35" filter="url(#num-glow)">{value}</text>
      <text x="{cx}" y="100" text-anchor="middle" fill="{theme['text_bright']}" font-size="26" font-weight="bold" font-family="sans-serif">{value}</text>
      <text x="{cx}" y="118" text-anchor="middle" fill="{theme['text_faint']}" font-size="11" font-family="monospace" letter-spacing="1">{label}</text>
    </g>''')

        # Vertical divider between cells (not after last)
        if i < len(metrics) - 1:
            dx = cell_width * (i + 1)
            dividers.append(
                f'    <line x1="{dx}" y1="55" x2="{dx}" y2="{divider_bottom}" '
                f'stroke="{theme["star_dust"]}" stroke-width="1" opacity="0.5"/>'
            )

    cells_str = "\n".join(cells)
    dividers_str = "\n".join(dividers)
    sparkline_str = _build_sparkline(activity or [], WIDTH, theme)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <defs>
    <style>
      .metric-icon {{
        animation: count-glow 4s ease-in-out infinite;
      }}
      @keyframes count-glow {{
        0%, 100% {{ fill-opacity: 0.7; }}
        50% {{ fill-opacity: 1; }}
      }}
    </style>
    <filter id="num-glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3"/>
    </filter>
  </defs>

  <!-- Card background -->
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="12" ry="12"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>

  <!-- Section title -->
  <text x="30" y="38" fill="{theme['text_faint']}" font-size="11" font-family="monospace" letter-spacing="3">MISSION TELEMETRY</text>

  <!-- Dividers -->
{dividers_str}

  <!-- Metric cells -->
{cells_str}

  <!-- Activity sparkline -->
{sparkline_str}
</svg>'''
