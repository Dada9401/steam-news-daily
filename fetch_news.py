import feedparser
import datetime
import re
import calendar

# --- 2026 Steam 官方活动数据库 ---
STEAM_EVENTS_2026 = [
    {"name": "侦探游戏节", "start": "20260112", "end": "20260119", "type": "fest"},
    {"name": "桌游节", "start": "20260126", "end": "20260202", "type": "fest"},
    {"name": "打字游戏节", "start": "20260205", "end": "20260209", "type": "spotlight"},
    {"name": "PvP 游戏节", "start": "20260209", "end": "20260216", "type": "fest"},
    {"name": "新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest"},
    {"name": "塔防游戏节", "start": "20260309", "end": "20260316", "type": "fest"},
    {"name": "Steam 春季大促", "start": "20260319", "end": "20260326", "type": "major"},
    {"name": "建造与生活节", "start": "20260330", "end": "20260406", "type": "fest"},
    {"name": "中世纪游戏节", "start": "20260420", "end": "20260427", "type": "fest"},
    {"name": "牌组构建游戏节", "start": "20260504", "end": "20260511", "type": "fest"},
    {"name": "海洋游戏节", "start": "20260518", "end": "20260525", "type": "fest"},
    {"name": "弹幕射击节", "start": "20260608", "end": "20260615", "type": "fest"},
    {"name": "新品节 (6月版)", "start": "20260615", "end": "20260622", "type": "nextfest"},
    {"name": "Steam 夏季大促", "start": "20260625", "end": "20260709", "type": "major"},
    {"name": "赛博朋克节", "start": "20260803", "end": "20260810", "type": "fest"},
    {"name": "生存工匠节", "start": "20260831", "end": "20260907", "type": "fest"},
    {"name": "Steam 秋季大促", "start": "20261001", "end": "20261008", "type": "major"},
    {"name": "新品节 (10月版)", "start": "20261019", "end": "20261026", "type": "nextfest"},
    {"name": "万圣节尖叫祭", "start": "20261026", "end": "20261102", "type": "fest"},
    {"name": "Steam 冬季大促", "start": "20261217", "end": "20270104", "type": "major"},
]

def generate_calendar_html():
    now = datetime.datetime.now()
    year, month = now.year, now.month
    cal = calendar.monthcalendar(year, month)
    month_name = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"][month-1]
    
    html = f'<div class="bg-slate-900/50 border border-blue-500/20 rounded-2xl p-4 font-mono">'
    html += f'<div class="flex justify-between items-center mb-4 text-blue-400 font-black text-xl"><span>{month_name}</span><span>{year}</span></div>'
    html += '<div class="grid grid-cols-7 gap-1 text-center text-[10px] text-gray-500 mb-2">'
    for day in ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]: html += f'<div>{day}</div>'
    html += '</div>'
    
    # 获取本月所有活动日期
    active_days = {}
    current_date_int = int(now.strftime("%Y%m%d"))
    
    for event in STEAM_EVENTS_2026:
        start, end = int(event['start']), int(event['end'])
        for d in range(1, 32):
            try:
                this_date = int(f"{year}{month:02d}{d:02d}")
                if start <= this_date <= end:
                    color = "#3b82f6" if event['type'] == 'major' else "#10b981"
                    if event['type'] == 'nextfest': color = "#f59e0b"
                    active_days[d] = {"color": color, "name": event['name']}
            except: continue

    html += '<div class="grid grid-cols-7 gap-1 text-center font-bold">'
    for week in cal:
        for day in week:
            if day == 0:
                html += '<div></div>'
            else:
                style = ""
                bg_class = "text-gray-400"
                if day in active_days:
                    bg_class = "text-white bg-opacity-100"
                    style = f'background-color: {active_days[day]["color"]}; border-radius: 4px; box-shadow: 0 0 8px {active_days[day]["color"]}88;'
                elif day == now.day:
                    bg_class = "text-blue-400 border border-blue-400 rounded"
                html += f'<div class="py-1 {bg_class}" style="{style}">{day}</div>'
    html += '</div>'
    
    # 日历下方列出本月活动
    html += '<div class="mt-6 space-y-3">'
    has_event = False
    for event in STEAM_EVENTS_2026:
        if event['start'].startswith(f"{year}{month:02d}") or event['end'].startswith(f"{year}{month:02d}"):
            has_event = True
            is_active = int(event['start']) <= current_date_int <= int(event['end'])
            status_dot = "🔴" if is_active else "⚪"
            html += f'<div class="text-[11px] flex items-start gap-2 {"text-blue-300" if is_active else "text-gray-500"}">'
            html += f'<span>{status_dot}</span>'
            html += f'<div><div class="font-bold">{event["name"]}</div><div class="opacity-50 text-[9px]">{event["start"][6:]}-{event["end"][6:]}</div></div></div>'
    if not has_event: html += '<div class="text-[10px] text-gray-600 italic">本月暂无重大节日</div>'
    html += '</div></div>'
    return html

def get_steam_rss_data(url_type):
    rss_url = f"https://store.steampowered.com/feeds/news/collection/{url_type}/?l=schinese"
    slides_html = ""
    try:
        feed = feedparser.parse(rss_url)
        if not feed.entries and url_type != "all": return get_steam_rss_data("all")
        for entry in feed.entries[:8]:
            title, link = entry.title, entry.link
            content = entry.get('summary', '') or entry.get('description', '')
            img_match = re.search(r'<img [^>]*src="([^"]+)"', content)
            img_url = img_match.group(1) if img_match else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/594650/capsule_617x353.jpg"
            slides_html += f'''
            <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
                <div class="relative h-full w-full overflow-hidden rounded-3xl bg-slate-900 border border-white/10 group">
                    <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-60 transition-all duration-700 group-hover:scale-110">
                    <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
                    <div class="absolute bottom-0 p-6 w-full"><h2 class="text-xl font-bold text-white line-clamp-2">{title}</h2></div>
                </div>
            </div>'''
        return slides_html
    except: return ""

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    calendar_html = generate_calendar_html()
    
    # 行业简报
    ticker_text = "行业实时情报同步中..."
    try:
        industry_feed = feedparser.parse("https://www.gamespot.com/feeds/news/")
        if industry_feed.entries: ticker_text = " • ".join([f"【{e.title}】" for e in industry_feed.entries[:12]])
    except: pass

    featured_html = get_steam_rss_data("featured")
    official_html = get_steam_rss_data("steam")

    template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>STEAM 2026 MONITOR</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #020408; color: white; font-family: system-ui; overflow-x: hidden; padding-bottom: 120px; }
        .swiper { width: 100%; height: 380px; padding: 10px 0 60px 0; overflow: visible !important; }
        .swiper-slide { width: 400px; opacity: 0.3; transition: 0.5s; transform: scale(0.8); }
        .swiper-slide-active { opacity: 1; transform: scale(1); }
        .swiper-pagination-bullet { background: #3b82f6; opacity: 0.3; transition: all 0.4s; }
        .swiper-pagination-bullet-active { background: #60a5fa !important; opacity: 1; width: 30px; border-radius: 6px; box-shadow: 0 0 15px #3b82f6; }
        .ticker-wrap { position: fixed; bottom: 0; left: 0; width: 100%; background: #2563eb; color: white; padding: 15px 0; z-index: 100; }
        .ticker { display: inline-block; white-space: nowrap; animation: scroll 80s linear infinite; font-weight: bold; }
        @keyframes scroll { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
        ::-webkit-scrollbar { width: 0; }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-[1600px] mx-auto flex flex-col lg:flex-row gap-8">
        <div class="flex-1 min-w-0">
            <header class="flex justify-between items-end border-b border-blue-900/40 pb-6 mb-10">
                <div>
                    <h1 class="text-6xl font-black italic text-blue-500 tracking-tighter uppercase">Monitor</h1>
                    <p class="text-xs text-blue-400 font-mono mt-2 tracking-[0.3em]">INTELLIGENCE HUB // SYNC: {now_time}</p>
                </div>
            </header>

            <section class="mb-12">
                <h2 class="text-xl font-black mb-4 flex items-center gap-4 text-white uppercase"><span class="bg-blue-600 w-2 h-6"></span> Featured</h2>
                <div class="swiper mySwiper">
                    <div class="swiper-wrapper">{featured_html}</div>
                    <div class="swiper-pagination"></div>
                </div>
            </section>

            <section>
                <h2 class="text-xl font-black mb-4 flex items-center gap-4 text-blue-400 uppercase"><span class="bg-blue-400 w-2 h-6"></span> Official</h2>
                <div class="swiper mySwiper">
                    <div class="swiper-wrapper">{official_html}</div>
                    <div class="swiper-pagination"></div>
                </div>
            </section>
        </div>

        <div class="w-full lg:w-80 flex-shrink-0">
            <div class="sticky top-8">
                <h2 class="text-sm font-black mb-4 flex items-center gap-2 text-gray-400 uppercase tracking-widest">
                    <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                    Event Calendar
                </h2>
                {calendar_html}
                
                <div class="mt-8 p-6 rounded-2xl bg-gradient-to-br from-blue-900/20 to-transparent border border-blue-500/10">
                    <h3 class="text-xs font-bold text-blue-400 mb-2 uppercase">Legend 图例</h3>
                    <div class="grid grid-cols-2 gap-2 text-[10px]">
                        <div class="flex items-center gap-2"><span class="w-2 h-2 bg-blue-500 rounded-sm"></span> 季节大促</div>
                        <div class="flex items-center gap-2"><span class="w-2 h-2 bg-green-500 rounded-sm"></span> 节日庆典</div>
                        <div class="flex items-center gap-2"><span class="w-2 h-2 bg-yellow-500 rounded-sm"></span> 新品试玩</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="ticker-wrap"><div class="ticker">LIVE INTEL: {ticker_text}</div></div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.mySwiper').forEach(el => {
            const swiper = new Swiper(el, {
                effect: "coverflow", grabCursor: true, centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: { delay: 4000, disableOnInteraction: false },
                coverflowEffect: { rotate: 0, stretch: 0, depth: 150, modifier: 2, slideShadows: false },
                pagination: { el: el.querySelector('.swiper-pagination'), clickable: true }
            });
            el.addEventListener('mouseover', function(e) {
                if (e.target.classList.contains('swiper-pagination-bullet')) {
                    const bullets = Array.from(el.querySelectorAll('.swiper-pagination-bullet'));
                    const index = bullets.indexOf(e.target);
                    if (index !== -1) swiper.slideToLoop(index);
                }
            });
        });
    </script>
</body>
</html>'''

    full_html = template.replace("{now_time}", now_time)\
                        .replace("{featured_html}", featured_html)\
                        .replace("{official_html}", official_html)\
                        .replace("{ticker_text}", ticker_text)\
                        .replace("{calendar_html}", calendar_html)

    with open("index.html", "w", encoding="utf-8") as f: f.write(full_html)

if __name__ == "__main__":
    update_web()
