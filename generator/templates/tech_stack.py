"""SVG template: Language Telemetry + Focus Sectors radar (dynamic height)."""

import math

from generator.utils import calculate_language_percentages, esc, svg_arc_path, resolve_arm_colors

WIDTH = 850


def _build_language_bars(lang_data, theme, left_x, start_y):
    bar_lines = []
    bar_max_width = 200

    for i, lang in enumerate(lang_data):
        y = start_y + i * 22
        bar_w = max(4, (lang["percentage"] / 100) * bar_max_width)
        delay = f"{i * 0.1}s"

        bar_lines.append(f'''    <g transform="translate({left_x}, {y})">
      <text x="0" y="0" fill="{theme['text_dim']}" font-size="11" font-family="sans-serif" dominant-baseline="middle">{esc(lang['name'])}</text>
      <rect x="110" y="-6" width="{bar_w}" height="12" rx="3" fill="{lang['color']}" opacity="0.85">
        <animate attributeName="width" from="0" to="{bar_w}" dur="0.8s" begin="{delay}" fill="freeze"/>
      </rect>
      <text x="320" y="0" fill="{theme['text_faint']}" font-size="10" font-family="monospace" dominant-baseline="middle">{lang['percentage']}%</text>
    </g>''')

    return "\n".join(bar_lines)


def _build_radar_grid(rcx, rcy, grid_rings, theme):
    parts = []
    for ring_r in grid_rings:
        parts.append(
            f'    <circle cx="{rcx}" cy="{rcy}" r="{ring_r}" '
            f'fill="none" stroke="{theme["text_faint"]}" '
            f'stroke-width="0.5" stroke-dasharray="3,3" opacity="0.25"/>'
        )
    return "\n".join(parts)


def _build_radar_sectors(sector_data, rcx, rcy, radius, theme):
    parts = []

    # Filled arc sectors
    for sec in sector_data:
        d = svg_arc_path(rcx, rcy, radius, sec["start_deg"], sec["end_deg"])
        parts.append(
            f'    <path d="{d}" fill="{sec["color"]}" fill-opacity="0.10" '
            f'stroke="{sec["color"]}" stroke-opacity="0.3" stroke-width="0.5"/>'
        )

    # Dynamic radial boundary lines
    sector_count = len(sector_data)
    sector_angle = 360 / sector_count

    for i in range(sector_count):
        angle_deg = i * sector_angle
        angle_rad = math.radians(angle_deg - 90)
        lx = rcx + radius * math.cos(angle_rad)
        ly = rcy + radius * math.sin(angle_rad)

        parts.append(
            f'    <line x1="{rcx}" y1="{rcy}" x2="{lx:.1f}" y2="{ly:.1f}" '
            f'stroke="{theme["text_faint"]}" stroke-width="0.5" opacity="0.3"/>'
        )

    return "\n".join(parts)


def _build_radar_needle(rcx, rcy, radius, theme):
    scan_color = theme.get("synapse_cyan", "#00d4ff")
    tip_x = rcx
    tip_y = rcy - radius

    sweep_d = svg_arc_path(rcx, rcy, radius, 330, 360)

    outer_hw = 2.5
    inner_hw = 0.8

    return (
        f'    <g>'
        f'\n      <path d="{sweep_d}" fill="{scan_color}" fill-opacity="0.07"/>'
        f'\n      <polygon points="{rcx - outer_hw},{rcy} {tip_x},{tip_y} {rcx + outer_hw},{rcy}" '
        f'fill="{scan_color}" opacity="0.25"/>'
        f'\n      <polygon points="{rcx - inner_hw},{rcy} {tip_x},{tip_y} {rcx + inner_hw},{rcy}" '
        f'fill="{scan_color}" opacity="0.5"/>'
        f'\n      <circle cx="{tip_x}" cy="{tip_y}" r="2" fill="{scan_color}" opacity="0.6">'
        f'\n        <animate attributeName="opacity" values="0.4;0.8;0.4" dur="2s" repeatCount="indefinite"/>'
        f'\n      </circle>'
        f'\n      <animateTransform attributeName="transform" type="rotate" '
        f'from="0 {rcx} {rcy}" to="360 {rcx} {rcy}" '
        f'dur="8s" repeatCount="indefinite"/>'
        f'\n    </g>'
    )


def _build_radar_labels_and_dots(sector_data, galaxy_arms, rcx, rcy, radius, theme):
    parts = []

    for sec in sector_data:
        mid_deg = (sec["start_deg"] + sec["end_deg"]) / 2
        mid_rad = math.radians(mid_deg - 90)
        label_r = radius + 22  # slightly more spacing
        lx = rcx + label_r * math.cos(mid_rad)
        ly = rcy + label_r * math.sin(mid_rad)

        anchor = "middle" if abs(lx - rcx) < 5 else ("start" if lx > rcx else "end")

        parts.append(
            f'    <text x="{lx:.1f}" y="{ly:.1f}" fill="{sec["color"]}" '
            f'font-size="9" font-family="monospace" text-anchor="{anchor}" '
            f'dominant-baseline="middle">{esc(sec["name"])}</text>'
        )

        parts.append(
            f'    <text x="{lx:.1f}" y="{(ly + 12):.1f}" fill="{theme["text_faint"]}" '
            f'font-size="8" font-family="monospace" text-anchor="{anchor}" '
            f'dominant-baseline="middle">({sec["items"]})</text>'
        )

    radii_cycle = [28, 48, 68]

    for sec_i, sec in enumerate(sector_data):
        arm = galaxy_arms[sec_i]
        items = arm.get("items", [])
        item_count = len(items)

        edge_pad = 10
        usable_start = sec["start_deg"] + edge_pad
        usable_end = sec["end_deg"] - edge_pad

        for j, _ in enumerate(items):
            if item_count == 1:
                item_angle = (usable_start + usable_end) / 2
            else:
                item_angle = usable_start + (usable_end - usable_start) * j / (item_count - 1)

            item_rad = math.radians(item_angle - 90)
            dot_r = radii_cycle[j % 3]

            dx = rcx + dot_r * math.cos(item_rad)
            dy = rcy + dot_r * math.sin(item_rad)

            pulse_begin = (item_angle / 360) * 8 - 0.3
            if pulse_begin < 0:
                pulse_begin += 8

            parts.append(
                f'    <circle cx="{dx:.1f}" cy="{dy:.1f}" r="3" '
                f'fill="{sec["color"]}" opacity="0.35">'
                f'\n      <animate attributeName="opacity" '
                f'values="0.35;0.35;1.0;0.35;0.35" '
                f'keyTimes="0;0.04;0.06;0.10;1" '
                f'dur="8s" begin="{pulse_begin:.2f}s" repeatCount="indefinite"/>'
                f'\n    </circle>'
            )

    return "\n".join(parts)


def render(languages, galaxy_arms, theme, exclude, max_display):
    lang_data = calculate_language_percentages(languages, exclude, max_display)

    left_x = 30
    start_y = 65

    bars_str = _build_language_bars(lang_data, theme, left_x, start_y)

    all_arm_colors = resolve_arm_colors(galaxy_arms, theme)

    sector_data = []
    sector_count = len(galaxy_arms)
    sector_angle = 360 / sector_count

    for i, arm in enumerate(galaxy_arms):
        start = i * sector_angle + 2
        end = (i + 1) * sector_angle - 2

        sector_data.append({
            "name": arm["name"],
            "color": all_arm_colors[i],
            "items": len(arm.get("items", [])),
            "start_deg": start,
            "end_deg": end,
        })

    radius = 75
    rcx = 637
    badge_start_y = 65
    rcy = badge_start_y + radius + 10
    grid_rings = [25, 50, 75]

    lang_height = start_y + len(lang_data) * 22 + 20
    radar_height = rcy + radius + 35
    height = max(220, lang_height, radar_height)

    radar_str = "\n".join([
        _build_radar_grid(rcx, rcy, grid_rings, theme),
        _build_radar_sectors(sector_data, rcx, rcy, radius, theme),
        _build_radar_needle(rcx, rcy, radius, theme),
        _build_radar_labels_and_dots(sector_data, galaxy_arms, rcx, rcy, radius, theme),
    ])

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="12" ry="12"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>

  <text x="30" y="38" fill="{theme['text_faint']}" font-size="11" font-family="monospace" letter-spacing="3">LANGUAGE TELEMETRY</text>
  <line x1="425" y1="25" x2="425" y2="{height - 25}" stroke="{theme['star_dust']}" stroke-width="1" opacity="0.4"/>
  <text x="460" y="38" fill="{theme['text_faint']}" font-size="11" font-family="monospace" letter-spacing="3">FOCUS SECTORS</text>

{bars_str}

{radar_str}
</svg>'''