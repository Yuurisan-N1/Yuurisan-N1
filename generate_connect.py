import re
import requests

USERNAME = 'Yuurisan-N1'


def fetch_views():
    try:
        resp = requests.get(
            f'https://komarev.com/ghpvc/?username={USERNAME}&abbreviated=false',
            timeout=10
        )
        match = re.search(r'>(\d[\d,]*)<', resp.text)
        if match:
            return int(match.group(1).replace(',', ''))
    except Exception as e:
        print(f"Warning: {e}")
    return 0


def x_icon(cx, cy, size=13, color="#ffffff"):
    s = size / 16
    ox, oy = cx - 8*s, cy - 8*s
    return (
        f'<g transform="translate({ox:.1f},{oy:.1f}) scale({s:.3f})">'
        f'<path d="M12.6 2h2.45L9.73 7.93 16 14h-4.44l-3.42-4.47L4.37 14H1.92l5.63-6.44L1 2h4.56l3.09 4.04L12.6 2z" fill="{color}"/>'
        f'</g>'
    )


def telegram_icon(cx, cy, size=14, color="#229ED9"):
    s = size / 24
    ox, oy = cx - 12*s, cy - 12*s
    return (
        f'<g transform="translate({ox:.1f},{oy:.1f}) scale({s:.3f})">'
        f'<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" fill="{color}"/>'
        f'<path d="M17.64 7.29l-1.77 8.34c-.13.6-.48.74-.97.46l-2.69-1.98-1.3 1.25c-.14.14-.27.27-.55.27l.19-2.73 4.99-4.51c.22-.19-.05-.3-.33-.11L7.26 13.4 4.6 12.58c-.58-.18-.59-.58.12-.86l12.43-4.79c.49-.17.91.12.49.36z" fill="white"/>'
        f'</g>'
    )


def eye_icon(cx, cy, size=14, color="#ff2d8d"):
    s = size / 24
    ox, oy = cx - 12*s, cy - 12*s
    return (
        f'<g transform="translate({ox:.1f},{oy:.1f}) scale({s:.3f})">'
        f'<path d="M12 5C7 5 2.73 8.11 1 12.5 2.73 16.89 7 20 12 20s9.27-3.11 11-7.5C21.27 8.11 17 5 12 5zm0 12.5c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="{color}"/>'
        f'</g>'
    )


def generate_svg(views):
    W, H = 860, 118
    views_str = f'{views:,}' if views > 0 else '-'

    parts = []
    parts.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">')
    parts.append('<style>text{font-family:ui-monospace,"SFMono-Regular",monospace}</style>')
    parts.append(f'<rect width="{W}" height="{H}" rx="8" fill="#0d1117"/>')
    parts.append(
        f'<line x1="40" y1="1" x2="{W-40}" y2="1" stroke="#6d28d9" stroke-width="1">'
        f'<animate attributeName="opacity" values="0.3;0.7;0.3" dur="5s" repeatCount="indefinite"/>'
        f'</line>'
    )

    cols = [
        (W//6,   x_icon,        '#e7e9ea', 'X / Twitter',  '@Yuurisan_N1'),
        (W//2,   telegram_icon, '#229ED9', 'Telegram',      'Y3YuYuYo'),
        (W*5//6, eye_icon,      '#ff2d8d', 'Profile Views', views_str),
    ]

    for cx, icon_fn, color, sub, label in cols:
        parts.append(icon_fn(cx, 32))
        parts.append(f'<text x="{cx}" y="57" font-size="8.5" fill="#4b5563" text-anchor="middle" letter-spacing="1">{sub}</text>')
        parts.append(
            f'<text x="{cx}" y="76" font-size="17" fill="{color}" text-anchor="middle" font-weight="bold">{label}'
            + (f'<animate attributeName="opacity" values="1;0.75;1" dur="4s" repeatCount="indefinite"/>' if color == '#ff2d8d' else '')
            + '</text>'
        )

    parts.append(f'<line x1="40" y1="90" x2="{W-40}" y2="90" stroke="#1e2a1e" stroke-width="1"/>')
    parts.append(f'<text x="{W//2}" y="108" font-size="9" fill="#374151" text-anchor="middle" letter-spacing="3">BUILD WITH INTENTION · IMPROVE EVERY DAY</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def main():
    print("Fetching profile views from komarev.com...")
    views = fetch_views()
    print(f"Profile views: {views:,}")
    svg = generate_svg(views)
    with open('metrics.connect.svg', 'w', encoding='utf-8') as f:
        f.write(svg)
    print("Generated metrics.connect.svg successfully")


if __name__ == '__main__':
    main()