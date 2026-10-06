import math

W, H = 860, 320
cx, cy = 185, H // 2
R = 130

axes = [
    ('Languages',  0.95, '#f34b7d'),
    ('Web / TS',   0.82, '#2b7489'),
    ('Infra',      0.78, '#89e051'),
    ('Blockchain', 0.68, '#AA6746'),
    ('Databases',  0.72, '#336791'),
    ('Systems',    0.91, '#dea584'),
]
n = len(axes)

cat_techs = [
    ('Languages',  '#f34b7d', [
        ('Python', '#3572A5'), ('Rust',     '#dea584'),
        ('C++',    '#f34b7d'), ('Go',       '#00ADD8'),
        ('Ruby',   '#701516'), ('Assembly', '#6E4C13'),
    ]),
    ('Web / TS',   '#2b7489', [
        ('React',      '#61DAFB'), ('Vue',    '#42b883'),
        ('TypeScript', '#2b7489'), ('Node.js','#339933'),
        ('Next.js',    '#ffffff'), ('Svelte', '#FF3E00'),
    ]),
    ('Infra',      '#89e051', [
        ('Docker',     '#2496ED'), ('Linux',      '#FCC624'),
        ('Nginx',      '#009639'), ('Git',        '#F05032'),
        ('Bash',       '#89e051'), ('Cloudflare', '#F38020'),
    ]),
    ('Blockchain', '#AA6746', [
        ('Solidity', '#AA6746'), ('Web3.js', '#F16822'),
        ('Ethers',   '#6651FF'), ('Hardhat', '#FFF100'),
        ('IPFS',     '#65C2CB'),
    ]),
    ('Databases',  '#336791', [
        ('PostgreSQL', '#336791'), ('MongoDB', '#47A248'),
        ('Redis',      '#DC382D'), ('MySQL',   '#4479A1'),
        ('SQLite',     '#003B57'),
    ]),
    ('Systems',    '#dea584', [
        ('CUDA',    '#3A4E3A'), ('Shell',   '#89e051'),
        ('Makefile','#427819'), ('OpenCL',  '#ed2e2d'),
        ('Nuitka',  '#dea584'), ('Cargo',   '#CE4A00'),
    ]),
]


def pt(i, scale=1.0, extra_r=0):
    a = math.radians(i * 360 / n - 90)
    return (cx + (R * scale + extra_r) * math.cos(a),
            cy + (R * scale + extra_r) * math.sin(a))


def generate_svg():
    grid = []
    for lvl in [0.25, 0.5, 0.75, 1.0]:
        pts = " ".join(f"{pt(i, lvl)[0]:.2f},{pt(i, lvl)[1]:.2f}" for i in range(n))
        grid.append(f'<polygon points="{pts}" fill="none" stroke="#1e2a1e" stroke-width="1"/>')

    axis_els = []
    for i, (label, val, color) in enumerate(axes):
        ex, ey = pt(i, 1.0)
        axis_els.append(f'<line x1="{cx}" y1="{cy}" x2="{ex:.2f}" y2="{ey:.2f}" stroke="#1e2a1e" stroke-width="1"/>')
        lx, ly = pt(i, 1.0, 20)
        anchor = "middle"
        if lx < cx - 8: anchor = "end"
        elif lx > cx + 8: anchor = "start"
        axis_els.append(
            f'<text x="{lx:.2f}" y="{ly:.2f}" font-size="9.5" fill="#6b7280"'
            f' text-anchor="{anchor}" dominant-baseline="middle" font-family="monospace">{label}</text>'
        )

    pts_zero = " ".join(f"{cx},{cy}" for _ in range(n))
    pts_full = " ".join(f"{pt(i, axes[i][1])[0]:.2f},{pt(i, axes[i][1])[1]:.2f}" for i in range(n))
    area = (
        f'<polygon points="{pts_zero}" fill="#6d28d9" fill-opacity="0.18" stroke="#a855f7" stroke-width="1.5">'
        f'<animate attributeName="points" from="{pts_zero}" to="{pts_full}"'
        f' dur="1.2s" begin="0.2s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/>'
        f'</polygon>'
    )

    dot_els = []
    for i, (label, val, color) in enumerate(axes):
        dx, dy = pt(i, val)
        dot_els.append(
            f'<circle cx="{dx:.2f}" cy="{dy:.2f}" r="4" fill="{color}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{0.9+i*0.1:.1f}s" fill="freeze"/>'
            f'</circle>'
        )
        dot_els.append(
            f'<circle cx="{dx:.2f}" cy="{dy:.2f}" r="4" fill="none" stroke="{color}" stroke-width="1" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="0.5" dur="0.3s" begin="{0.9+i*0.1:.1f}s" fill="freeze"/>'
            f'<animate attributeName="r" values="4;10;4" dur="2.5s" begin="{1.5+i*0.2:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.5;0;0.5" dur="2.5s" begin="{1.5+i*0.2:.1f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    scan_els = []
    scan_els.append(
        f'<defs>'
        f'<clipPath id="radarClip"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>'
        f'<filter id="scanGlow" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feGaussianBlur stdDeviation="3" result="blur"/>'
        f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        f'</filter>'
        f'</defs>'
    )

    steps, cone_deg = 40, 70
    slices = []
    for s in range(steps):
        f1, f2 = s / steps, (s + 1) / steps
        a1 = math.radians(-cone_deg * f1 - 90)
        a2 = math.radians(-cone_deg * f2 - 90)
        p1x = cx + R * 1.05 * math.cos(a1); p1y = cy + R * 1.05 * math.sin(a1)
        p2x = cx + R * 1.05 * math.cos(a2); p2y = cy + R * 1.05 * math.sin(a2)
        op = 0.18 * (1 - f1)
        slices.append(
            f'<polygon points="{cx},{cy} {p1x:.2f},{p1y:.2f} {p2x:.2f},{p2y:.2f}"'
            f' fill="#00ff88" opacity="{op:.3f}"/>'
        )
    lead_x = cx + R * 1.05 * math.cos(math.radians(-90))
    lead_y = cy + R * 1.05 * math.sin(math.radians(-90))
    slices.append(
        f'<line x1="{cx}" y1="{cy}" x2="{lead_x:.2f}" y2="{lead_y:.2f}"'
        f' stroke="#00ff88" stroke-width="1.5" opacity="0.9" filter="url(#scanGlow)"/>'
    )
    scan_els.append(
        f'<g clip-path="url(#radarClip)"><g>'
        + "".join(slices)
        + f'<animateTransform attributeName="transform" type="rotate"'
          f' from="0 {cx} {cy}" to="360 {cx} {cy}" dur="4s" repeatCount="indefinite" begin="1.5s"/>'
          f'</g></g>'
    )
    scan_els.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#00ff88" stroke-width="0.8" opacity="0.25"/>')
    scan_els.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="#00ff88" opacity="0.7"/>')
    scan_els.append(
        f'<circle cx="{cx}" cy="{cy}" r="3" fill="none" stroke="#00ff88" stroke-width="1">'
        f'<animate attributeName="r" values="3;8;3" dur="2s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.7;0;0.7" dur="2s" repeatCount="indefinite"/>'
        f'</circle>'
    )

    legend_x = cx + R + 55
    legend_col_w = (W - legend_x - 16) // 3
    col_positions = [legend_x, legend_x + legend_col_w, legend_x + legend_col_w * 2]

    def group_height(cats):
        max_h = 0
        for _, _, items in cats:
            h = 13 + math.ceil(len(items) / 2) * 15
            max_h = max(max_h, h)
        return max_h

    gh0 = group_height(cat_techs[0:3])
    gh1 = group_height(cat_techs[3:6])
    divider_gap = 14
    total_legend_h = gh0 + divider_gap * 2 + gh1
    legend_top = (H - total_legend_h) // 2
    row_start_y = [legend_top, legend_top + gh0 + divider_gap * 2]
    div_y = legend_top + gh0 + divider_gap

    legend_els = []
    legend_els.append(
        f'<line x1="{legend_x}" y1="{div_y}" x2="{W - 10}" y2="{div_y}"'
        f' stroke="#1e2a1e" stroke-width="1"/>'
    )

    for ci, (cat, cat_color, items) in enumerate(cat_techs):
        col = ci % 3
        row = ci // 3
        bx = col_positions[col]
        by = row_start_y[row]
        legend_els.append(
            f'<text x="{bx}" y="{by}" font-size="9.5" fill="{cat_color}"'
            f' font-family="monospace" font-weight="bold">{cat}</text>'
        )
        for ni, (nm, col_c) in enumerate(items):
            ix = bx + (ni % 2) * 80
            iy = by + 14 + (ni // 2) * 15
            legend_els.append(f'<circle cx="{ix+4}" cy="{iy-3}" r="3.5" fill="{col_c}"/>')
            legend_els.append(
                f'<text x="{ix+11}" y="{iy}" font-size="8.5" fill="#9ca3af"'
                f' font-family="monospace">{nm}</text>'
            )

    nl = '\n'
    svg = (
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n'
        f'<style>text{{font-family:ui-monospace,"SFMono-Regular",monospace}}</style>\n'
        f'<rect width="{W}" height="{H}" rx="8" fill="#0d1117"/>\n'
        f'<text x="16" y="16" font-size="11" fill="#4b5563" font-family="monospace">Tech Stack</text>\n'
        + nl.join(grid) + '\n'
        + nl.join(axis_els) + '\n'
        + area + '\n'
        + nl.join(scan_els) + '\n'
        + nl.join(dot_els) + '\n'
        + nl.join(legend_els) + '\n'
        + '</svg>'
    )
    return svg


def main():
    svg = generate_svg()
    with open('metrics.techstack.svg', 'w', encoding='utf-8') as f:
        f.write(svg)
    print("Generated metrics.techstack.svg successfully")


if __name__ == '__main__':
    main()
