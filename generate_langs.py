import os
import math
import requests

TOKEN = os.environ['METRICS_TOKEN']
USERNAME = 'Yuurisan-N1'

LANG_COLORS = {
    'C++': '#f34b7d', 'C': '#555555', 'Python': '#3572A5',
    'Assembly': '#6E4C13', 'Unix Assembly': '#6E4C13', 'Rust': '#dea584',
    'CUDA': '#3A4E3A', 'Go': '#00ADD8', 'Ruby': '#701516',
    'JavaScript': '#f1e05a', 'TypeScript': '#2b7489', 'Shell': '#89e051',
    'Solidity': '#AA6746', 'PHP': '#4F5D95', 'Java': '#b07219',
    'OpenCL': '#ed2e2d', 'Makefile': '#427819', 'Elixir': '#6e4a7e',
    'Batchfile': '#C1F12E', 'PowerShell': '#012456', 'Metal': '#A97842',
    'Dart': '#00B4AB', 'C#': '#178600',
}
IGNORED = {'Markdown', 'Text', 'JSON', 'YAML', 'TOML', 'XML', 'HTML', 'CSS', 'CMake', 'Dockerfile'}
DEFAULT_COLOR = '#8b8b8b'

QUERY_BYTES = '''
query($login: String!, $cursor: String) {
  user(login: $login) {
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false) {
      nodes {
        languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}
'''

QUERY_REPOS = '''
query($login: String!, $cursor: String) {
  user(login: $login) {
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false) {
      nodes {
        primaryLanguage { name color }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}
'''

def fetch_bytes():
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    langs = {}
    cursor = None
    while True:
        resp = requests.post('https://api.github.com/graphql', headers=headers,
            json={'query': QUERY_BYTES, 'variables': {'login': USERNAME, 'cursor': cursor}})
        data = resp.json()['data']['user']['repositories']
        for repo in data['nodes']:
            for edge in repo['languages']['edges']:
                name = edge['node']['name']
                if name in IGNORED:
                    continue
                size = edge['size']
                color = edge['node']['color'] or DEFAULT_COLOR
                if name not in langs:
                    langs[name] = {'size': 0, 'color': color}
                langs[name]['size'] += size
        if not data['pageInfo']['hasNextPage']:
            break
        cursor = data['pageInfo']['endCursor']
    return langs

def fetch_repo_counts():
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    counts = {}
    cursor = None
    while True:
        resp = requests.post('https://api.github.com/graphql', headers=headers,
            json={'query': QUERY_REPOS, 'variables': {'login': USERNAME, 'cursor': cursor}})
        data = resp.json()['data']['user']['repositories']
        for repo in data['nodes']:
            pl = repo.get('primaryLanguage')
            if not pl:
                continue
            name = pl['name']
            if name in IGNORED:
                continue
            color = pl['color'] or DEFAULT_COLOR
            if name not in counts:
                counts[name] = {'count': 0, 'color': color}
            counts[name]['count'] += 1
        if not data['pageInfo']['hasNextPage']:
            break
        cursor = data['pageInfo']['endCursor']
    return counts

def donut_arc(cx, cy, R, r, start_deg, end_deg):
    sa = math.radians(start_deg - 90)
    ea = math.radians(end_deg - 90)
    x1 = cx + R*math.cos(sa); y1 = cy + R*math.sin(sa)
    x2 = cx + R*math.cos(ea); y2 = cy + R*math.sin(ea)
    x3 = cx + r*math.cos(ea); y3 = cy + r*math.sin(ea)
    x4 = cx + r*math.cos(sa); y4 = cy + r*math.sin(sa)
    large = 1 if (end_deg - start_deg) > 180 else 0
    return f"M{x1:.2f} {y1:.2f} A{R} {R} 0 {large} 1 {x2:.2f} {y2:.2f} L{x3:.2f} {y3:.2f} A{r} {r} 0 {large} 0 {x4:.2f} {y4:.2f}Z"

def draw_section(items, label, cy_offset, W, col_val_fn):
    cx, cy = 130, cy_offset + 120
    R, r = 82, 54
    nl = '\n'
    rows = []

    total = sum(v for _, v, _ in items)

    arcs = []
    angle = 0
    gap = 1.5
    for name, val, color in items:
        sweep = val / total * 360
        end = angle + sweep - gap
        if sweep > gap:
            arcs.append(f'<path d="{donut_arc(cx, cy, R, r, angle, end)}" fill="{color}"/>')
        angle += sweep

    bar_x = 215
    col_gap = 20
    col_w = (W - bar_x - col_gap - 20) // 2
    label_w = 110
    bar_w_max = col_w - label_w - 52
    row_h = 26
    start_y = cy_offset + 22

    for i, (name, val, color) in enumerate(items):
        col = i // 8
        row = i % 8
        x = bar_x + col * (col_w + col_gap)
        y = start_y + row * row_h
        filled = val / total * bar_w_max
        val_str = col_val_fn(name, val, total)
        rows.append(
            f'<circle cx="{x+5}" cy="{y+5}" r="4" fill="{color}"/>'
            f'<text x="{x+15}" y="{y+9}" font-size="11" fill="#c9d1d9">{name}</text>'
            f'<text x="{x+label_w+bar_w_max+8}" y="{y+9}" font-size="11" fill="#8b949e" text-anchor="end">{val_str}</text>'
            f'<rect x="{x+label_w}" y="{y+13}" width="{bar_w_max:.1f}" height="4" rx="2" fill="#21262d"/>'
            f'<rect x="{x+label_w}" y="{y+13}" width="{filled:.1f}" height="4" rx="2" fill="{color}"/>'
        )

    return (
        f'<text x="16" y="{cy_offset+18}" font-size="11" fill="#8b949e">{label}</text>'
        + nl.join(arcs)
        + f'<text x="{cx}" y="{cy+6}" font-size="20" font-weight="bold" fill="#c9d1d9" text-anchor="middle">{len(items)}</text>'
        + f'<text x="{cx}" y="{cy+20}" font-size="9" fill="#8b949e" text-anchor="middle">languages</text>'
        + nl.join(rows)
    )

def generate_svg(bytes_langs, repo_counts):
    W = 900
    H_section = 240
    H_total = H_section * 2 + 8
    nl = '\n'

    sorted_bytes = sorted(bytes_langs.items(), key=lambda x: x[1]['size'], reverse=True)[:16]
    bytes_items = [(n, d['size'], LANG_COLORS.get(n, d['color'])) for n, d in sorted_bytes]

    sorted_repos = sorted(repo_counts.items(), key=lambda x: x[1]['count'], reverse=True)[:16]
    repo_items = [(n, d['count'], LANG_COLORS.get(n, d['color'])) for n, d in sorted_repos]

    def bytes_val(name, val, total):
        return f"{val/total*100:.1f}%"

    def repo_val(name, val, total):
        return f"{val} repos"

    parts = [
        f'<svg width="{W}" height="{H_total}" viewBox="0 0 {W} {H_total}" xmlns="http://www.w3.org/2000/svg">',
        '<style>text{font-family:ui-monospace,"SFMono-Regular",monospace}</style>',
        f'<rect width="{W}" height="{H_total}" rx="8" fill="#0d1117"/>',
        draw_section(bytes_items, 'Most used languages code volume', 0, W, bytes_val),
        f'<line x1="20" y1="{H_section+4}" x2="{W-20}" y2="{H_section+4}" stroke="#21262d" stroke-width="1"/>',
        draw_section(repo_items, 'Most used languages repo count', H_section+8, W, repo_val),
        '</svg>',
    ]
    return nl.join(parts)

def main():
    print("Fetching language bytes...")
    bytes_langs = fetch_bytes()
    print("Fetching repo counts...")
    repo_counts = fetch_repo_counts()
    svg = generate_svg(bytes_langs, repo_counts)
    with open('metrics.langs.svg', 'w', encoding='utf-8') as f:
        f.write(svg)
    print("Generated metrics.langs.svg successfully")

if __name__ == '__main__':
    main()