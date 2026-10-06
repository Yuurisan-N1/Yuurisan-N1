import os
import math
import requests
from datetime import datetime, timedelta, timezone

TOKEN    = os.environ['METRICS_TOKEN']
USERNAME = 'Yuurisan-N1'

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json',
}

QUERY = '''
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
'''

def fetch_contributions():
    resp = requests.post(
        'https://api.github.com/graphql',
        headers=HEADERS,
        json={'query': QUERY, 'variables': {'login': USERNAME}}
    )
    weeks = resp.json()['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    days = {}
    for week in weeks:
        for day in week['contributionDays']:
            days[day['date']] = day['contributionCount']
    return days


def calc_streak(days):
    today = datetime.now(timezone.utc).date()
    start = today if days.get(str(today), 0) > 0 else today - timedelta(days=1)

    current_streak = 0
    d = start
    while True:
        count = days.get(str(d), 0)
        if count == 0:
            break
        current_streak += 1
        d -= timedelta(days=1)

    longest_streak = 0
    run = 0
    for date_str in sorted(days.keys()):
        if days[date_str] > 0:
            run += 1
            longest_streak = max(longest_streak, run)
        else:
            run = 0

    last14 = []
    for i in range(13, -1, -1):
        d2 = today - timedelta(days=i)
        last14.append(1 if days.get(str(d2), 0) > 0 else 0)

    total_contributions = sum(days.values())
    return current_streak, longest_streak, last14, total_contributions


def generate_svg(streak, longest, last14, total):
    W, H = 860, 160
    max_goal = max(longest + 10, 100)
    fx, fy = 100, H - 20
    flame_h = int(40 + min(streak / max_goal, 1.0) * 85)
    fw = 50

    parts = []
    parts.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">')
    parts.append('<style>text{font-family:ui-monospace,"SFMono-Regular",monospace}</style>')
    parts.append(
        f'<defs>'
        f'<radialGradient id="flameGlow" cx="50%" cy="80%" r="60%">'
        f'<stop offset="0%" stop-color="#ff6b00" stop-opacity="0.4"/>'
        f'<stop offset="100%" stop-color="#ff6b00" stop-opacity="0"/>'
        f'</radialGradient>'
        f'<linearGradient id="flameFill" x1="0%" y1="100%" x2="0%" y2="0%">'
        f'<stop offset="0%" stop-color="#ff2d00"/>'
        f'<stop offset="40%" stop-color="#ff6b00"/>'
        f'<stop offset="100%" stop-color="#ffd700" stop-opacity="0.8"/>'
        f'</linearGradient>'
        f'<linearGradient id="barGrad" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="#ff2d00"/>'
        f'<stop offset="100%" stop-color="#ffd700"/>'
        f'</linearGradient>'
        f'</defs>'
    )
    parts.append(f'<rect width="{W}" height="{H}" rx="8" fill="#0d1117"/>')

    parts.append(f'<ellipse cx="{fx}" cy="{fy-2}" rx="{int(fw*0.6)}" ry="8" fill="url(#flameGlow)"/>')

    flame_path = (
        f"M{fx},{fy} "
        f"C{fx-fw//2},{fy-flame_h*0.3} {fx-fw//3},{fy-flame_h*0.6} {fx},{fy-flame_h} "
        f"C{fx+fw//4},{fy-flame_h*0.7} {fx+fw//2},{fy-flame_h*0.5} {fx+fw//3},{fy-flame_h*0.2} "
        f"C{fx+fw//2},{fy-flame_h*0.1} {fx+fw//3},{fy} {fx},{fy} Z"
    )
    parts.append(
        f'<path d="{flame_path}" fill="url(#flameFill)" opacity="0.9">'
        f'<animateTransform attributeName="transform" type="scale"'
        f' values="1 1;1.04 1.06;0.97 0.98;1 1" dur="1.2s" repeatCount="indefinite"'
        f' additive="sum" transformOrigin="{fx} {fy}"/>'
        f'</path>'
    )

    iw = fw * 0.55
    ih = flame_h * 0.65
    inner_path = (
        f"M{fx},{fy-5} "
        f"C{fx-iw//2},{fy-ih*0.3} {fx-iw//3},{fy-ih*0.65} {fx},{fy-ih} "
        f"C{fx+iw//4},{fy-ih*0.7} {fx+iw//2},{fy-ih*0.45} {fx+iw//3},{fy-ih*0.15} "
        f"C{fx+iw//2},{fy-5} {fx+iw//3},{fy-5} {fx},{fy-5} Z"
    )
    parts.append(
        f'<path d="{inner_path}" fill="#ffd700" opacity="0.7">'
        f'<animateTransform attributeName="transform" type="scale"'
        f' values="1 1;0.96 0.94;1.03 1.05;1 1" dur="1.2s" repeatCount="indefinite"'
        f' additive="sum" transformOrigin="{fx} {fy}"/>'
        f'</path>'
    )

    parts.append(f'<text x="{fx}" y="{fy-flame_h//2+8}" font-size="26" font-weight="bold" fill="#fff" text-anchor="middle">{streak}</text>')
    parts.append(f'<text x="{fx}" y="{fy-flame_h//2+22}" font-size="9" fill="#ffd700" text-anchor="middle">day streak</text>')

    sx = 185
    parts.append(f'<text x="{sx}" y="22" font-size="11" fill="#4b5563">Commit Streak</text>')

    parts.append(f'<text x="{sx}" y="60" font-size="44" font-weight="bold" fill="#ff6b00">{streak}</text>')
    parts.append(f'<text x="{sx+58}" y="60" font-size="15" fill="#6b7280"> days</text>')

    parts.append(f'<text x="{sx+140}" y="38" font-size="9" fill="#4b5563">longest streak</text>')
    parts.append(f'<text x="{sx+140}" y="56" font-size="20" font-weight="bold" fill="#9ca3af">{longest}</text>')
    parts.append(f'<text x="{sx+140+28}" y="56" font-size="10" fill="#4b5563"> days</text>')

    parts.append(f'<text x="{sx+280}" y="38" font-size="9" fill="#4b5563">total contributions</text>')
    parts.append(f'<text x="{sx+280}" y="56" font-size="20" font-weight="bold" fill="#9ca3af">{total:,}</text>')

    milestone = ((streak // 10) + 1) * 10
    progress = streak % 10
    bar_w = 600
    filled = int(progress / 10 * bar_w)
    parts.append(f'<text x="{sx}" y="82" font-size="9" fill="#4b5563">next milestone: {milestone} days</text>')
    parts.append(f'<rect x="{sx}" y="90" width="{bar_w}" height="7" rx="3" fill="#1e2a1e"/>')
    parts.append(
        f'<rect x="{sx}" y="90" width="0" height="7" rx="3" fill="url(#barGrad)">'
        f'<animate attributeName="width" from="0" to="{filled}" dur="1s" begin="0.3s" fill="freeze"'
        f' calcMode="spline" keySplines="0.4 0 0.2 1"/>'
        f'</rect>'
    )
    parts.append(f'<text x="{sx+filled+6}" y="98" font-size="8" fill="#ff6b00">{progress}/10</text>')

    # last 14 days mini heatmap
    parts.append(f'<text x="{sx}" y="118" font-size="9" fill="#4b5563">last 14 days</text>')
    for i, has in enumerate(last14):
        rx2 = sx + i * 19
        color = "#ff6b00" if has else "#1e2a1e"
        delay = round(i * 0.04, 2)
        parts.append(
            f'<rect x="{rx2}" y="124" width="15" height="15" rx="3" fill="{color}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.2s" begin="{delay}s" fill="freeze"/>'
            f'</rect>'
        )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    print("Fetching contributions from GitHub...")
    days = fetch_contributions()
    streak, longest, last14, total = calc_streak(days)
    print(f"Current streak: {streak} days | Longest: {longest} | Total: {total}")
    svg = generate_svg(streak, longest, last14, total)
    with open('metrics.streak.svg', 'w', encoding='utf-8') as f:
        f.write(svg)
    print("Generated metrics.streak.svg successfully")


if __name__ == '__main__':
    main()
