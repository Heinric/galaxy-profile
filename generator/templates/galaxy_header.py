"""SVG template: Galaxy Header — the signature spiral galaxy banner (850x280)."""

import math
from generator.utils import spiral_points, deterministic_random, esc, resolve_arm_colors

# ── Module-level constants ──
WIDTH, HEIGHT = 850, 280
CENTER_X, CENTER_Y = 425, 155
MAX_RADIUS = 220
SPIRAL_TURNS = 0.85
NUM_POINTS = 30
X_SCALE, Y_SCALE = 1.5, 0.38


def _build_glow_filters(galaxy_arms, arm_colors):
    glow_filters = []
    for i, arm in enumerate(galaxy_arms):
        color = arm_colors[i]
        glow_filters.append(
            f'    <filter id="star-glow-{i}" x="-100%" y="-100%" width="300%" height="300%">\n'
            f'      <feGaussianBlur stdDeviation="3" result="blur"/>\n'
            f'      <feFlood flood-color="{color}" flood-opacity="0.5" result="color"/>\n'
            f'      <feComposite in="color" in2="blur" operator="in" result="glow"/>\n'
            f'      <feMerge>\n'
            f'        <feMergeNode in="glow"/>\n'
            f'        <feMergeNode in="SourceGraphic"/>\n'
            f'      </feMerge>\n'
            f'    </filter>'
        )
    return "\n".join(glow_filters)


def _points_to_path(points):
    d = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
    for j in range(1, len(points)):
        px, py = points[j - 1]
        x, y = points[j]
        cpx = (px + x) / 2
        cpy = (py + y) / 2
        d += f" Q {px:.1f} {py:.1f} {cpx:.1f} {cpy:.1f}"
    d += f" L {points[-1][0]:.1f} {points[-1][1]:.1f}"
    return d


def _build_spiral_arms(galaxy_arms, arm_colors, all_arm_points):
    arm_paths = []
    arm_particles = []

    segment_count = 4
    opacity_steps = [0.50, 0.40, 0.30, 0.20]
    width_steps = [2.0, 1.7, 1.4, 1.1]

    for arm_idx, arm in enumerate(galaxy_arms):
        color = arm_colors[arm_idx]
        points = all_arm_points[arm_idx]

        if len(points) < 2:
            continue

        full_path_d = _points_to_path(points)
        pts_per_seg = len(points) // segment_count

        for seg in range(segment_count):
            start_i = seg * pts_per_seg
            end_i = min(start_i + pts_per_seg + 1, len(points))
            seg_pts = points[start_i:end_i]

            if len(seg_pts) < 2:
                continue

            seg_d = _points_to_path(seg_pts)
            op = opacity_steps[seg]
            sw = width_steps[seg]

            arm_paths.append(
                f'    <path d="{seg_d}" fill="none" stroke="{color}" '
                f'stroke-width="{sw:.1f}" opacity="{op:.2f}" stroke-linecap="round"/>'
            )

        for p_idx in range(2):
            delay = arm_idx * 4 + p_idx * 6
            arm_particles.append(
                f'    <circle r="1.5" fill="{color}" opacity="0.6">\n'
                f'      <animateMotion dur="12s" begin="{delay}s" repeatCount="indefinite" '
                f'path="{full_path_d}"/>\n'
                f'    </circle>'
            )

    return "\n".join(arm_paths), "\n".join(arm_particles)


def render(config: dict, theme: dict, galaxy_arms: list, projects: list) -> str:
    username = config.get("username", "user")
    profile = config.get("profile", {})
    name = profile.get("name", username)
    tagline = profile.get("tagline", "")
    philosophy = profile.get("philosophy", "")
    initial = name[0].upper() if name else "?"

    arm_colors = resolve_arm_colors(galaxy_arms, theme)

    # ─────────────────────────────────────────────
    # 🔥 NEW: Dynamic spiral geometry (fix overlap)
    # ─────────────────────────────────────────────

    arm_count = len(galaxy_arms)
    angle_step = 360 / arm_count

    all_arm_points = []

    for arm_idx in range(arm_count):
        base_angle = arm_idx * angle_step + 20

        dynamic_max_radius = MAX_RADIUS - (arm_idx * 12)
        dynamic_x_scale = X_SCALE + (arm_idx * 0.07)
        dynamic_y_scale = Y_SCALE + (arm_idx * 0.03)

        points = spiral_points(
            CENTER_X,
            CENTER_Y,
            base_angle,
            NUM_POINTS,
            dynamic_max_radius,
            SPIRAL_TURNS,
            dynamic_x_scale,
            dynamic_y_scale,
        )

        all_arm_points.append(points)

    arm_paths_str, arm_particles_str = _build_spiral_arms(
        galaxy_arms, arm_colors, all_arm_points
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="12" ry="12" fill="{theme['void']}"/>

{arm_paths_str}
{arm_particles_str}

  <circle cx="{CENTER_X}" cy="{CENTER_Y}" r="40" fill="{theme['synapse_cyan']}" opacity="0.08"/>
  <circle cx="{CENTER_X}" cy="{CENTER_Y}" r="20" fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="0.5"/>
  <text x="{CENTER_X}" y="{CENTER_Y + 5}" text-anchor="middle" fill="{theme['synapse_cyan']}" font-size="14" font-family="monospace">{initial}</text>

  <text x="{CENTER_X}" y="26" text-anchor="middle" fill="{theme['text_bright']}" font-size="20" font-weight="bold" font-family="sans-serif">{esc(name)}</text>
  <text x="{CENTER_X}" y="44" text-anchor="middle" fill="{theme['text_dim']}" font-size="12" font-family="sans-serif">{esc(tagline)}</text>
  <text x="{CENTER_X}" y="{HEIGHT - 12}" text-anchor="middle" fill="{theme['text_faint']}" font-size="11" font-family="monospace" font-style="italic">{esc(philosophy)}</text>
</svg>'''