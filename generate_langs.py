import os
import math
import requests

TOKEN = os.environ['METRICS_TOKEN']
USERNAME = 'Yuurisan-N1'

LANG_COLORS = {
    'C++': '#f34b7d',
    'C': '#555555',
    'Python': '#3572A5',
    'Assembly': '#6E4C13',
    'Unix Assembly': '#6E4C13',
    'Rust': '#dea584',
    'CUDA': '#3A4E3A',
    'Go': '#00ADD8',
    'Ruby': '#701516',
    'JavaScript': '#f1e05a',
    'TypeScript': '#2b7489',
    'Shell': '#89e051',
    'Solidity': '#AA6746',
    'PHP': '#4F5D95',
    'Java': '#b07219',
    'OpenCL': '#ed2e2d',
    'Makefile': '#427819',
}

IGNORED = {'Markdown', 'Text', 'JSON', 'YAML', 'TOML', 'XML', 'HTML', 'CSS', 'CMake', 'Dockerfile'}

DEFAULT_COLOR = '#8b8b8b'

QUERY = '''
query($login: String!, $cursor: String) {
  user(login: $login) {
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false) {
      nodes {
        languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node { name color }
          }
        }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}
'''


def fetch_languages():
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json',
    }
    langs = {}
    cursor = None

    while True:
        resp = requests.post(
            'https://api.github.com/graphql',
            headers=headers,
            json={'query': QUERY, 'variables': {'login': USERNAME, 'cursor': cursor}}
        )
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


def donut_arc(cx, cy, R, r, start_deg, end_deg):
    sa = math.radians(start_deg - 90)
    ea = math.radians(end_deg - 90)
    x1 = cx + R * math.cos(sa)
    y1 = cy + R * math.sin(sa)
    x2 = cx + R * math.cos(ea)
    y2 = cy + R * math.sin(ea)
    x3 = cx + r * math.cos(ea)
    y3 = cy + r * math.sin(ea)
    x4 = cx + r * math.cos(sa)
    y4 = cy + r * math.sin(sa)
    large = 1 if (end_deg - start_deg) > 180 else 0
    return f"M{x1:.2f} {y1:.2f} A{R} {R} 0 {large} 1 {x2:.2f} {y2:.2f} L{x3:.2f} {y3:.2f} A{r} {r} 0 {large} 0 {x4:.2f} {y4:.2f}Z"


def generate_svg(langs_data):
    sorted_langs = sorted(langs_data.items(), key=lambda x: x[1]['size'], reverse=True)[:16]
    total = sum(v['size'] for _, v in sorted_langs)
    if total == 0:
        return None

    items = []
    for name, data in sorted_langs:
        pct = data['size'] / total * 100
        color = LANG_COLORS.get(name, data['color'])
        items.append({'name': name, 'pct': pct, 'color': color, 'size': data['size']})

    W, H = 900, 240

    cx, cy, R, r = 130, 125, 90, 58

    arcs = []
    angle = 0
    gap = 1.2
    for item in items:
        sweep = item['pct'] / 100 * 360
        end = angle + sweep - gap
        if sweep > gap:
            arcs.append(f'<path d="{donut_arc(cx, cy, R, r, angle, end)}" fill="{item["color"]}" />')
        angle += sweep

    col_start_x = 250
    col_gap = 20
    col_w = (W - col_start_x - col_gap - 20) // 2

    label_w = 110
    pct_w = 42
    bar_w = col_w - label_w - pct_w - 10

    row_h = 26
    start_y = 22

    rows = []
    for i, item in enumerate(items):
        col = i // 8
        row = i % 8
        x = col_start_x + col * (col_w + col_gap)
        y = start_y + row * row_h
        filled = item['pct'] / 100 * bar_w
        rows.append(
            f'<circle cx="{x + 5}" cy="{y + 5}" r="4" fill="{item["color"]}"/>'
            f'<text x="{x + 15}" y="{y + 9}" font-size="11" fill="#c9d1d9">{item["name"]}</text>'
            f'<text x="{x + label_w + bar_w + 8}" y="{y + 9}" font-size="11" fill="#8b949e" text-anchor="end">{item["pct"]:.1f}%</text>'
            f'<rect x="{x + label_w}" y="{y + 13}" width="{bar_w:.1f}" height="4" rx="2" fill="#21262d"/>'
            f'<rect x="{x + label_w}" y="{y + 13}" width="{filled:.1f}" height="4" rx="2" fill="{item["color"]}"/>'
        )

    nl = '\n'
    svg = f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}</style>
<rect width="{W}" height="{H}" rx="6" fill="#0d1117"/>
<text x="16" y="18" font-size="12" fill="#8b949e">Most used languages</text>
{''.join(arcs)}
<text x="{cx}" y="{cy + 7}" font-size="22" font-weight="bold" fill="#c9d1d9" text-anchor="middle">{len(items)}</text>
<text x="{cx}" y="{cy + 22}" font-size="9" fill="#8b949e" text-anchor="middle">languages</text>
{nl.join(rows)}
</svg>'''

    return svg


def main():
    langs = fetch_languages()
    svg = generate_svg(langs)
    if svg:
        with open('metrics.langs.svg', 'w', encoding='utf-8') as f:
            f.write(svg)
        print("Generated metrics.langs.svg successfully")
    else:
        print("No language data found")


if __name__ == '__main__':
    main()