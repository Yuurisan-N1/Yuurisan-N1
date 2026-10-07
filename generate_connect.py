import os
import json
import math
import random
import requests
from datetime import datetime, timezone

USERNAME = 'Yuurisan-N1'
TOKEN = os.environ['METRICS_TOKEN']
CACHE_FILE = 'views_cache.json'
INITIAL_VIEWS = 1295

def fetch_traffic_views():
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Accept': 'application/vnd.github+json',
    }
    try:
        resp = requests.get(
            f'https://api.github.com/repos/{USERNAME}/{USERNAME}/traffic/views',
            headers=headers,
            timeout=10
        )
        data = resp.json()
        views_by_date = {}
        for item in data.get('views', []):
            views_by_date[item['timestamp'][:10]] = item['count']
        return views_by_date
    except Exception as e:
        print(f"Warning: could not fetch traffic: {e}")
        return {}

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {'total': INITIAL_VIEWS, 'last_dates': {}}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def update_views():
    cache = load_cache()
    new_views = fetch_traffic_views()
    added = 0
    for date, count in new_views.items():
        if date not in cache['last_dates']:
            cache['total'] += count
            cache['last_dates'][date] = count
            added += count
    # keep only last 60 days in cache to avoid file bloat
    if len(cache['last_dates']) > 60:
        sorted_dates = sorted(cache['last_dates'].keys())
        for old_date in sorted_dates[:-60]:
            del cache['last_dates'][old_date]
    save_cache(cache)
    print(f"Added {added} new views. Total: {cache['total']:,}")
    return cache['total']

random.seed(42)

def sakura_petal_flower(cx, cy, angle, size, opacity):
    a = math.radians(angle)
    px = cx + math.cos(a) * size * 0.5
    py = cy + math.sin(a) * size * 0.5
    return (f'<ellipse cx="{px:.1f}" cy="{py:.1f}" '
            f'rx="{size*0.55:.1f}" ry="{size*0.3:.1f}" '
            f'fill="#ffb7c5" opacity="{opacity}" '
            f'transform="rotate({angle},{px:.1f},{py:.1f})"/>')

def generate_svg(views):
    W, H = 860, 200
    ground_y = H - 28
    tx, ty = 95, ground_y
    trunk_h = 55

    nl = '\n'
    parts = []
    parts.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">')
    parts.append('<style>text{font-family:ui-monospace,"SFMono-Regular",monospace}</style>')
    parts.append(f'<defs>'
        f'<linearGradient id="sky" x1="0%" y1="0%" x2="0%" y2="100%">'
        f'<stop offset="0%" stop-color="#0a0514"/>'
        f'<stop offset="100%" stop-color="#1a0820"/>'
        f'</linearGradient>'
        f'<linearGradient id="trunk" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="#2a1010"/>'
        f'<stop offset="50%" stop-color="#3d1a1a"/>'
        f'<stop offset="100%" stop-color="#2a1010"/>'
        f'</linearGradient>'
        f'<radialGradient id="moonGlow" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="#fff5ee" stop-opacity="0.95"/>'
        f'<stop offset="60%" stop-color="#ffe4cc" stop-opacity="0.3"/>'
        f'<stop offset="100%" stop-color="#ffccdd" stop-opacity="0"/>'
        f'</radialGradient>'
        f'</defs>')
    parts.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')

    for _ in range(40):
        sx = random.randint(0, W)
        sy = random.randint(0, H-60)
        sr = round(random.uniform(0.4, 1.2), 1)
        sdur = round(random.uniform(2, 5), 1)
        sdel = round(random.uniform(0, 4), 1)
        parts.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="white" opacity="0.6">'
            f'<animate attributeName="opacity" values="0.6;0.1;0.6" dur="{sdur}s" begin="{sdel}s" repeatCount="indefinite"/>'
            f'</circle>')

    mx, my = 760, 45
    parts.append(f'<circle cx="{mx}" cy="{my}" r="38" fill="url(#moonGlow)" opacity="0.4"/>')
    parts.append(f'<circle cx="{mx}" cy="{my}" r="22" fill="#fff5ee" opacity="0.95">'
        f'<animate attributeName="opacity" values="0.95;0.85;0.95" dur="6s" repeatCount="indefinite"/>'
        f'</circle>')

    parts.append(f'<rect x="0" y="{ground_y}" width="{W}" height="{H-ground_y}" fill="#0d0318" opacity="0.8"/>')
    parts.append(f'<line x1="0" y1="{ground_y}" x2="{W}" y2="{ground_y}" stroke="#ff69b4" stroke-width="0.5" opacity="0.3"/>')

    def branch(x1, y1, x2, y2, w):
        parts.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="url(#trunk)" stroke-width="{w}" stroke-linecap="round"/>')

    bx, by = tx-3, ty-trunk_h
    branch(tx, ty, bx, by, 8)
    branch(bx, by, bx-35, by-30, 5)
    branch(bx, by, bx+25, by-25, 5)
    branch(bx, by, bx-5,  by-38, 4)
    branch(bx-35, by-30, bx-60, by-48, 3)
    branch(bx-35, by-30, bx-18, by-52, 3)
    branch(bx+25, by-25, bx+48, by-46, 3)
    branch(bx+25, by-25, bx+18, by-50, 3)
    branch(bx-5,  by-38, bx-22, by-60, 2.5)
    branch(bx-5,  by-38, bx+12, by-58, 2.5)
    branch(bx-60, by-48, bx-72, by-58, 2)
    branch(bx-60, by-48, bx-50, by-60, 2)
    branch(bx+48, by-46, bx+58, by-58, 2)
    branch(bx-18, by-52, bx-30, by-64, 1.5)
    branch(bx+18, by-50, bx+28, by-62, 1.5)
    branch(bx-22, by-60, bx-32, by-70, 1.5)
    branch(bx+12, by-58, bx+20, by-68, 1.5)

    tips = [
        (bx-72, by-60), (bx-52, by-63), (bx-32, by-68), (bx-22, by-63),
        (bx-12, by-68), (bx+10, by-68), (bx+22, by-63), (bx+30, by-65),
        (bx+58, by-60), (bx+50, by-58), (bx-18, by-55), (bx+18, by-53),
        (bx-48, by-55), (bx+44, by-50), (bx-35, by-48), (bx+25, by-46),
        (bx-8,  by-52), (bx-60, by-50), (bx-25, by-58), (bx+8,  by-56),
        (bx-42, by-62), (bx+35, by-58), (bx-5,  by-45), (bx+15, by-43),
    ]
    blossom_centers = []
    for tcx, tcy in tips:
        for _ in range(random.randint(6, 12)):
            blossom_centers.append((tcx + random.randint(-14, 14), tcy + random.randint(-10, 10)))

    for bcx, bcy in blossom_centers:
        for p in range(5):
            angle = p * 72 + random.randint(-8, 8)
            sz = round(random.uniform(3.5, 5.5), 1)
            op = round(random.uniform(0.55, 0.92), 2)
            parts.append(sakura_petal_flower(bcx, bcy, angle, sz, op))
        parts.append(f'<circle cx="{bcx}" cy="{bcy}" r="1.2" fill="#ff69b4" opacity="0.8"/>')

    for ecx, ecy, er in [(bx-45,by-54,18),(bx+5,by-60,16),(bx+42,by-52,15),(bx-18,by-62,14),(bx+25,by-55,14),(bx-65,by-52,12)]:
        for _ in range(20):
            bx2 = ecx + random.randint(-er, er)
            by2 = ecy + random.randint(-er//2, er//2)
            op = round(random.uniform(0.3, 0.7), 2)
            sz = round(random.uniform(2.5, 4.5), 1)
            parts.append(f'<circle cx="{bx2}" cy="{by2}" r="{sz}" fill="#ffc0cb" opacity="{op}"/>')

    for i in range(25):
        px = random.randint(10, W-10)
        py_start = random.randint(-20, 30)
        py_end = ground_y + 10
        dur = round(random.uniform(4, 10), 1)
        delay = round(random.uniform(0, 8), 1)
        drift = random.randint(-70, 70)
        rot_start = random.randint(0, 360)
        sz = round(random.uniform(3, 5), 1)
        op = round(random.uniform(0.4, 0.75), 2)
        petal_parts = []
        for pp in range(5):
            a = pp * 72
            ar = math.radians(a)
            epx = math.cos(ar) * sz * 0.5
            epy = math.sin(ar) * sz * 0.5
            petal_parts.append(f'<ellipse cx="{epx:.1f}" cy="{epy:.1f}" rx="{sz*0.55:.1f}" ry="{sz*0.3:.1f}" fill="#ffb7c5" opacity="{op}" transform="rotate({a},{epx:.1f},{epy:.1f})"/>')
        petal_parts.append(f'<circle cx="0" cy="0" r="1" fill="#ff80ab" opacity="0.8"/>')
        parts.append(
            f'<g>'+"".join(petal_parts)
            +f'<animateTransform attributeName="transform" type="translate" values="{px},{py_start};{px+drift//2},{(py_start+py_end)//2};{px+drift},{py_end}" dur="{dur}s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>'
            +f'<animateTransform attributeName="transform" type="rotate" values="{rot_start};{rot_start+360}" dur="{dur}s" begin="{delay}s" repeatCount="indefinite" additive="sum"/>'
            +f'</g>'
        )

    tx2 = 285
    views_str = f'{views:,}'
    parts.append(f'<text x="{tx2}" y="38" font-size="9" fill="#b06080" letter-spacing="4">CONNECT</text>')
    parts.append(f'<line x1="{tx2}" y1="44" x2="{W-40}" y2="44" stroke="#ff2d8d" stroke-width="0.4" opacity="0.3"/>')
    parts.append(f'<text x="{tx2}" y="72" font-size="10" fill="#9a7a8a" letter-spacing="2">X / TWITTER</text>')
    parts.append(f'<text x="{tx2}" y="92" font-size="20" fill="#ffffff" font-weight="bold">@Yuurisan_N1</text>')
    parts.append(f'<text x="{tx2+280}" y="72" font-size="10" fill="#9a7a8a" letter-spacing="2">TELEGRAM</text>')
    parts.append(f'<text x="{tx2+280}" y="92" font-size="20" fill="#ffd6ee" font-weight="bold">Y3YuYuYo'
        f'<animate attributeName="opacity" values="1;0.7;1" dur="4s" repeatCount="indefinite"/></text>')
    parts.append(f'<line x1="{tx2}" y1="104" x2="{W-40}" y2="104" stroke="#ff2d8d" stroke-width="0.4" opacity="0.2"/>')
    parts.append(f'<text x="{tx2}" y="128" font-size="10" fill="#9a7a8a" letter-spacing="2">PROFILE VIEWS</text>')
    parts.append(f'<text x="{tx2}" y="160" font-size="40" fill="#ff2d8d" font-weight="bold">{views_str}'
        f'<animate attributeName="opacity" values="1;0.75;1" dur="3s" repeatCount="indefinite"/></text>')
    parts.append(f'<text x="{tx2}" y="{H-10}" font-size="8" fill="#7a4a6a" letter-spacing="3">build with intention · improve every day</text>')
    parts.append('</svg>')
    return nl.join(parts)

def main():
    print("Updating profile views...")
    views = update_views()
    svg = generate_svg(views)
    with open('metrics.connect.svg', 'w', encoding='utf-8') as f:
        f.write(svg)
    print("Generated metrics.connect.svg successfully")

if __name__ == '__main__':
    main()