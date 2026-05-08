"""SVG template: Featured Systems / Projects Constellation (multi-row grid)."""

import math

from generator.utils import wrap_text, deterministic_random, esc, resolve_arm_colors

WIDTH = 850
CARDS_PER_ROW = 4
CARD_H = 140
TITLE_H = 55   # y where first card row starts
ROW_GAP = 18
BOTTOM_PAD = 20
GAP = 15       # horizontal gap between cards (and side margins)


def _card_width():
    return (WIDTH - GAP * (CARDS_PER_ROW + 1)) / CARDS_PER_ROW


def _card_positions(n):
    """Return list of (card_x, card_y) for each of the n cards."""
    cw = _card_width()
    positions = []
    for i in range(n):
        row = i // CARDS_PER_ROW
        col = i % CARDS_PER_ROW
        row_count = min(CARDS_PER_ROW, n - row * CARDS_PER_ROW)
        row_width = row_count * cw + (row_count - 1) * GAP
        row_x_start = (WIDTH - row_width) / 2
        card_x = row_x_start + col * (cw + GAP)
        card_y = TITLE_H + row * (CARD_H + ROW_GAP)
        positions.append((card_x, card_y))
    return positions


def _svg_height(n):
    rows = math.ceil(n / CARDS_PER_ROW)
    return TITLE_H + rows * CARD_H + (rows - 1) * ROW_GAP + BOTTOM_PAD


def _build_defs(n, positions, card_width, card_colors, theme):
    defs_parts = []

    for i in range(n):
        color = card_colors[i]
        defs_parts.append(f'''    <filter id="proj-glow-{i}" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="4" in="SourceGraphic" result="blur"/>
      <feFlood flood-color="{color}" flood-opacity="0.6" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>''')

    defs_parts.append('''    <filter id="card-nebula" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="15"/>
    </filter>''')

    for i in range(n):
        defs_parts.append(f'''    <linearGradient id="card-bg-{i}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{theme['star_dust']}" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="{theme['nebula']}" stop-opacity="0.9"/>
    </linearGradient>''')

    if n >= 2:
        defs_parts.append(f'''    <linearGradient id="conn-grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{card_colors[0]}" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="{card_colors[-1]}" stop-opacity="0.4"/>
    </linearGradient>''')

    for i, (cx, cy) in enumerate(positions):
        defs_parts.append(f'''    <clipPath id="card-clip-{i}">
      <rect x="{cx:.1f}" y="{cy:.1f}" width="{card_width:.1f}" height="{CARD_H}" rx="8" ry="8"/>
    </clipPath>''')

    defs_parts.append('''    <style>
      @keyframes twinkle {
        0%, 100% { opacity: 0.1; }
        50% { opacity: 0.6; }
      }
      @keyframes orbit {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
      @keyframes card-appear {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
      }
    </style>''')

    return "\n".join(defs_parts)


def _build_starfield(n, width, height, card_colors, theme):
    stars = []
    layers = [
        {"prefix": "proj-star",  "count": 15, "margin": 10,
         "r": (0.3, 0.9), "o": (0.05, 0.25), "d": (5.0, 8.0), "o_mult": 3,   "o_cap": 0.6},
        {"prefix": "proj-mstar", "count": 10, "margin": 15,
         "r": (0.5, 1.2), "o": (0.10, 0.40), "d": (3.0, 6.0), "o_mult": 2.5, "o_cap": 0.8},
    ]
    for layer in layers:
        count = layer["count"]
        m     = layer["margin"]
        pfx   = layer["prefix"]
        sx = deterministic_random(f"{pfx}-x", count, m, width - m)
        sy = deterministic_random(f"{pfx}-y", count, m, height - m)
        sr = deterministic_random(f"{pfx}-r", count, *layer["r"])
        so = deterministic_random(f"{pfx}-o", count, *layer["o"])
        sd = deterministic_random(f"{pfx}-d", count, *layer["d"])
        for i in range(count):
            fill = card_colors[i % n] if i % 4 == 0 else theme["text_dim"]
            stars.append(
                f'  <circle cx="{sx[i]:.1f}" cy="{sy[i]:.1f}" r="{sr[i]:.1f}" '
                f'fill="{fill}" opacity="{so[i]:.2f}">'
                f'<animate attributeName="opacity" '
                f'values="{so[i]:.2f};{min(so[i]*layer["o_mult"], layer["o_cap"]):.2f};{so[i]:.2f}" '
                f'dur="{sd[i]:.1f}s" repeatCount="indefinite"/>'
                f'</circle>'
            )
    return "\n".join(stars)


def _build_grid_overlay(width, height, theme):
    lines = []
    for y in range(40, height, 40):
        lines.append(
            f'  <line x1="12" y1="{y}" x2="{width - 12}" y2="{y}" '
            f'stroke="{theme["text_faint"]}" stroke-width="0.5" '
            f'stroke-dasharray="4,8" opacity="0.08"/>'
        )
    for x in range(80, width, 80):
        lines.append(
            f'  <line x1="{x}" y1="12" x2="{x}" y2="{height - 12}" '
            f'stroke="{theme["text_faint"]}" stroke-width="0.5" '
            f'stroke-dasharray="4,8" opacity="0.06"/>'
        )
    return "\n".join(lines)


def _build_connections(n, positions, card_width):
    """Connection lines between cards within the same row."""
    lines = []
    for i in range(n - 1):
        curr_row = i // CARDS_PER_ROW
        next_row = (i + 1) // CARDS_PER_ROW
        if curr_row != next_row:
            continue
        x1 = positions[i][0] + card_width / 2
        x2 = positions[i + 1][0] + card_width / 2
        y_conn = positions[i][1] + 30
        lines.append(
            f'  <line x1="{x1:.1f}" y1="{y_conn:.1f}" x2="{x2:.1f}" y2="{y_conn:.1f}" '
            f'stroke="url(#conn-grad)" stroke-width="1" '
            f'stroke-dasharray="6,4" opacity="0.4"/>'
        )
    return "\n".join(lines)


def _build_title_area(n, width, height, theme):
    bk = theme["text_faint"]
    bl = 16
    cyan = theme.get("synapse_cyan", "#00d4ff")
    parts = [
        f'  <g opacity="0.4">'
        f'\n    <polyline points="5,{bl+5} 5,5 {bl+5},5" fill="none" stroke="{bk}" stroke-width="1.5"/>'
        f'\n    <polyline points="{width-bl-5},5 {width-5},5 {width-5},{bl+5}" fill="none" stroke="{bk}" stroke-width="1.5"/>'
        f'\n    <polyline points="5,{height-bl-5} 5,{height-5} {bl+5},{height-5}" fill="none" stroke="{bk}" stroke-width="1.5"/>'
        f'\n    <polyline points="{width-bl-5},{height-5} {width-5},{height-5} {width-5},{height-bl-5}" fill="none" stroke="{bk}" stroke-width="1.5"/>'
        f'\n  </g>',
        f'  <text x="30" y="38" fill="{theme["text_faint"]}" font-size="11" '
        f'font-family="monospace" letter-spacing="3">FEATURED SYSTEMS</text>',
        f'  <circle cx="218" cy="34" r="3" fill="{cyan}" opacity="0.8">'
        f'<animate attributeName="opacity" values="0.4;1;0.4" dur="2s" repeatCount="indefinite"/>'
        f'</circle>',
        f'  <text x="{width - 30}" y="38" fill="{theme["text_faint"]}" font-size="10" '
        f'font-family="monospace" text-anchor="end" opacity="0.5">SYS {n}/{n} ONLINE</text>',
    ]
    return "\n".join(parts)


def _build_project_card(i, proj, arm, color, card_width, card_x, card_y, theme):
    card_cx = card_x + card_width / 2
    repo_name = proj["repo"].split("/")[-1] if "/" in proj["repo"] else proj["repo"]
    desc = proj.get("description", "")
    max_chars = int(card_width / 7.5)
    desc_lines = wrap_text(desc, max_chars)
    delay = f"{i * 0.2}s"

    # y offsets relative to card_y
    ring_cy   = card_y + 30
    name_y    = card_y + 56
    desc1_y   = card_y + 74
    desc2_y   = card_y + 89
    tag_y     = card_y + 108
    tag_text_y = card_y + 120

    parts = [f'  <g opacity="0" style="animation: card-appear 0.6s ease {delay} forwards">']

    parts.append(
        f'    <rect x="{card_x:.1f}" y="{card_y:.1f}" width="{card_width:.1f}" height="{CARD_H}" '
        f'rx="8" ry="8" fill="url(#card-bg-{i})" stroke="{theme["star_dust"]}" stroke-width="1"/>'
    )

    parts.append(f'    <g clip-path="url(#card-clip-{i})">')
    parts.append(
        f'      <circle cx="{card_x + card_width * 0.3:.1f}" cy="{card_y + 35:.1f}" r="50" '
        f'fill="{color}" opacity="0.025" filter="url(#card-nebula)"/>'
    )
    parts.append(
        f'      <circle cx="{card_x + card_width * 0.7:.1f}" cy="{card_y + 95:.1f}" r="40" '
        f'fill="{color}" opacity="0.03" filter="url(#card-nebula)"/>'
    )
    parts.append('    </g>')

    parts.append(
        f'    <circle cx="{card_cx:.1f}" cy="{ring_cy}" r="14" fill="none" '
        f'stroke="{color}" stroke-width="0.8" stroke-dasharray="4,3" opacity="0.5">'
        f'<animateTransform attributeName="transform" type="rotate" '
        f'from="0 {card_cx:.1f} {ring_cy}" to="360 {card_cx:.1f} {ring_cy}" '
        f'dur="12s" repeatCount="indefinite"/></circle>'
    )
    parts.append(
        f'    <circle cx="{card_cx:.1f}" cy="{ring_cy}" r="8" fill="{color}" '
        f'opacity="0.15" filter="url(#proj-glow-{i})"/>'
    )
    parts.append(
        f'    <circle cx="{card_cx:.1f}" cy="{ring_cy}" r="5" fill="{color}" opacity="0.7">'
        f'<animate attributeName="opacity" values="0.5;0.9;0.5" dur="3s" begin="{delay}" repeatCount="indefinite"/>'
        f'<animate attributeName="r" values="4.5;5.5;4.5" dur="3s" begin="{delay}" repeatCount="indefinite"/>'
        f'</circle>'
    )
    parts.append(f'    <circle cx="{card_cx:.1f}" cy="{ring_cy}" r="2" fill="#ffffff" opacity="0.9"/>')

    parts.append(
        f'    <text x="{card_cx:.1f}" y="{name_y}" fill="{theme["text_bright"]}" '
        f'font-size="13" font-weight="bold" font-family="sans-serif" '
        f'text-anchor="middle">{esc(repo_name)}</text>'
    )

    for j, line in enumerate(desc_lines[:2]):
        y_pos = desc1_y + j * 15
        parts.append(
            f'    <text x="{card_cx:.1f}" y="{y_pos}" fill="{theme["text_dim"]}" '
            f'font-size="10" font-family="sans-serif" '
            f'text-anchor="middle">{esc(line)}</text>'
        )

    tag_text = arm["name"]
    tag_width = len(tag_text) * 7 + 16
    tag_x = card_cx - tag_width / 2
    parts.append(
        f'    <rect x="{tag_x:.1f}" y="{tag_y}" width="{tag_width}" height="18" '
        f'rx="9" ry="9" fill="{color}" opacity="0.12"/>'
    )
    parts.append(
        f'    <text x="{card_cx:.1f}" y="{tag_text_y}" fill="{color}" '
        f'font-size="9" font-family="monospace" text-anchor="middle" '
        f'opacity="0.85">{esc(tag_text)}</text>'
    )

    parts.append('  </g>')
    return "\n".join(parts)


def render(projects: list, galaxy_arms: list, theme: dict) -> str:
    all_arm_colors = resolve_arm_colors(galaxy_arms, theme)
    n = len(projects)

    if n == 0:
        h = _svg_height(1)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{h}" '
            f'viewBox="0 0 {WIDTH} {h}">'
            f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{h-1}" rx="12" ry="12" '
            f'fill="{theme["nebula"]}" stroke="{theme["star_dust"]}" stroke-width="1"/>'
            f'<text x="{WIDTH/2}" y="{h/2}" fill="{theme["text_faint"]}" font-size="12" '
            f'font-family="monospace" text-anchor="middle" dominant-baseline="middle">'
            f'No featured projects configured</text></svg>'
        )

    height = _svg_height(n)
    card_width = _card_width()
    positions = _card_positions(n)

    card_arms   = [min(p.get("arm", 0), len(galaxy_arms) - 1) for p in projects]
    card_colors = [all_arm_colors[a] for a in card_arms]

    defs_str  = _build_defs(n, positions, card_width, card_colors, theme)
    bg        = (
        f'  <rect x="0.5" y="0.5" width="{WIDTH-1}" height="{height-1}" rx="12" ry="12" '
        f'fill="{theme["nebula"]}" stroke="{theme["star_dust"]}" stroke-width="1"/>'
    )
    stars_str = _build_starfield(n, WIDTH, height, card_colors, theme)
    grid_str  = _build_grid_overlay(WIDTH, height, theme)
    conn_str  = _build_connections(n, positions, card_width)
    title_str = _build_title_area(n, WIDTH, height, theme)

    cards = [
        _build_project_card(
            i, projects[i], galaxy_arms[card_arms[i]], card_colors[i],
            card_width, positions[i][0], positions[i][1], theme,
        )
        for i in range(n)
    ]
    cards_str = "\n".join(cards)

    cyan = theme.get("synapse_cyan", "#00d4ff")
    scan_line = (
        f'  <rect x="12" y="50" width="{WIDTH-24}" height="1.5" '
        f'fill="{cyan}" opacity="0.06">'
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="0 0" to="0 {height-50}" dur="8s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <defs>
{defs_str}
  </defs>

  <!-- Background -->
{bg}

  <!-- Star field -->
{stars_str}

  <!-- Grid overlay -->
{grid_str}

  <!-- Connection lines -->
{conn_str}

  <!-- Title area -->
{title_str}

  <!-- Project cards -->
{cards_str}

  <!-- Global scan line -->
{scan_line}
</svg>'''
