"""SVG template: Engineering Focus card (850x165)."""

from generator.utils import esc, resolve_arm_colors

WIDTH, HEIGHT = 850, 165


def render(profile: dict, about: dict, theme: dict, galaxy_arms: list) -> str:
    arm_colors = resolve_arm_colors(galaxy_arms, theme)

    cyan   = theme.get("synapse_cyan",    "#00d4ff")
    violet = theme.get("dendrite_violet", "#a78bfa")
    amber  = theme.get("axon_amber",      "#ffb020")
    blue   = theme.get("quantum_blue",    "#3b82f6")

    company  = profile.get("company", "")
    location = profile.get("location", "")
    focus_areas     = about.get("focus_areas", [])
    tech_highlights = about.get("tech_highlights", [])

    focus_colors = [cyan, cyan, violet, blue]

    # ── Focus area pills (2 columns × 2 rows) ──
    focus_parts = []
    col_xs = [30, 440]
    row_ys = [75, 100]

    for i, area in enumerate(focus_areas[:4]):
        col   = i % 2
        row   = i // 2
        x     = col_xs[col]
        y     = row_ys[row]
        color = focus_colors[i] if i < len(focus_colors) else cyan
        dur   = f"{3 + i * 0.5:.1f}s"

        focus_parts.append(
            f'  <circle cx="{x + 5}" cy="{y}" r="3" fill="{color}" opacity="0.8">'
            f'<animate attributeName="opacity" values="0.5;1;0.5" '
            f'dur="{dur}" repeatCount="indefinite"/></circle>'
        )
        focus_parts.append(
            f'  <text x="{x + 16}" y="{y}" fill="{theme["text_dim"]}" font-size="12" '
            f'font-family="sans-serif" dominant-baseline="middle">{esc(area)}</text>'
        )

    # ── Tech highlights (up to 2 lines) ──
    tech_parts = []
    for i, line in enumerate(tech_highlights[:2]):
        y = 125 + i * 18
        tech_parts.append(
            f'  <text x="30" y="{y}" fill="{amber}" font-size="11" '
            f'font-family="monospace" opacity="0.75">{esc(line)}</text>'
        )

    # ── Company badge (top-right) ──
    company_str = ""
    if company:
        company_str = (
            f'  <circle cx="{WIDTH - 120}" cy="34" r="3" fill="{cyan}" opacity="0.8">'
            f'<animate attributeName="opacity" values="0.4;1;0.4" dur="2s" '
            f'repeatCount="indefinite"/></circle>\n'
            f'  <text x="{WIDTH - 112}" y="38" fill="{theme["text_faint"]}" font-size="10" '
            f'font-family="monospace" dominant-baseline="middle">{esc(company.upper())}</text>'
        )

    # ── Location (bottom-right) ──
    location_str = ""
    if location:
        location_str = (
            f'  <text x="{WIDTH - 30}" y="{HEIGHT - 14}" fill="{theme["text_faint"]}" '
            f'font-size="10" font-family="monospace" text-anchor="end" '
            f'opacity="0.5">{esc(location)}</text>'
        )

    focus_str = "\n".join(focus_parts)
    tech_str  = "\n".join(tech_parts)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" ry="12"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>

  <text x="30" y="38" fill="{theme['text_faint']}" font-size="11"
        font-family="monospace" letter-spacing="3">ENGINEERING FOCUS</text>

{company_str}

  <line x1="30" y1="52" x2="{WIDTH - 30}" y2="52"
        stroke="{theme['star_dust']}" stroke-width="1" opacity="0.4"/>

{focus_str}

{tech_str}

{location_str}
</svg>'''
