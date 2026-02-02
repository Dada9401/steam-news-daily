import feedparser
import datetime
import re
import time
import random

# ==========================================
# 核心配置：2026 Steam 官方活动数据库
# ==========================================
STEAM_EVENTS_2026 = [
    {"name": "棋盘游戏节", "start": "20260126", "end": "20260202", "type": "fest"},
    {"name": "打字节 (焦点节)", "start": "20260205", "end": "20260209", "type": "spotlight"},
    {"name": "PvP 游戏节", "start": "20260209", "end": "20260216", "type": "fest"},
    {"name": "Steam 新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest", "appid": "3985950"},
    {"name": "Steam 春季特卖", "start": "20260319", "end": "20260326", "type": "major"},
    {"name": "Steam 新品节 (6月版)", "start": "20260615", "end": "20260622", "type": "nextfest"},
    {"name": "Steam 夏季特卖", "start": "20260625", "end": "20260709", "type": "major"},
]
def generate_timeline_html():
    now = datetime.datetime.now()
    curr_int = int(now.strftime("%Y%m%d"))
    steam_events = [e for e in ALL_EVENTS_2026 if e['type'] == 'steam' and int(e['end']) >= curr_int]
    steam_events.sort(key=lambda x: x['start'])
    
    html = '<div class="flex flex-nowrap gap-4 overflow-x-auto pb-6 mb-10 no-scrollbar select-none">'
    for e in steam_events[:8]:
        active = int(e['start']) <= curr_int <= int(e['end'])
        color = "emerald-500" if active else "blue-500"
        html += f'''
        <div class="flex-shrink-0 w-60 p-5 rounded-2xl bg-white/80 dark:bg-slate-900/40 backdrop-blur-xl border border-slate-200 dark:border-white/5 shadow-sm">
            <div class="flex justify-between items-center mb-3">
                <span class="text-[9px] font-black tracking-tighter {'text-emerald-500 animate-pulse' if active else 'text-slate-400'} uppercase">{'● ACTIVE' if active else '○ PENDING'}</span>
                <span class="text-[10px] font-mono text-slate-400">{e['start'][4:6]}-{e['start'][6:]}</span>
            </div>
            <div class="text-sm font-bold text-slate-800 dark:text-slate-100 truncate mb-3">{e['name']}</div>
            <div class="h-1 w-full bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                <div class="h-full bg-{color}" style="width: {'100%' if active else '20%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def generate_active_ticker():
    now = datetime.datetime.now()
    curr_int = int(now.strftime("%Y%m%d"))
    active_events = []
    for e in ALL_EVENTS_2026:
        is_active = int(e['start']) <= curr_int <= int(e['end'])
        is_upcoming_steam = e['type'] == 'steam' and (0 < int(e['start']) - curr_int <= 3)
        if is_active or is_upcoming_steam:
            active_events.append(e)
    
    if not active_events: return ""
    contents = [f"{('🔥 正在进行' if int(e['start']) <= curr_int else '⏳ 即将开始')}: [{ 'Steam' if e['type']=='steam' else '第三方' }] {e['name']} | <a href='{e['url']}' target='_blank' class='underline decoration-wavy'>详情</a>" for e in active_events]
    ticker_text = " ——— ".join(contents)
    return f'''
    <div class="fixed bottom-0 left-0 w-full bg-blue-700 text-white py-2 z-[100] overflow-hidden whitespace-nowrap border-t border-white/20 shadow-2xl">
        <div class="inline-block animate-marquee px-4">
            <span class="font-black italic text-xs tracking-[0.2em] uppercase">{ticker_text} ——— {ticker_text}</span>
        </div>
    </div>'''

def get_steam_rss_data(mode, exclude_links=None):
    if exclude_links is None: exclude_links = set()
    source_map = {
        "featured": ["https://store.steampowered.com/feeds/news/collection/featured/?l=schinese"],
        "official": ["https://store.steampowered.com/feeds/news/collection/steam/?l=schinese"]
    }
    entries = []
    now_date = datetime.datetime.now().strftime("%m-%d")

    for url in source_map.get(mode, []):
        try:
            feed = feedparser.parse(f"{url}&v={random.random()}")
            for e in feed.entries:
                if e.link not in exclude_links:
                    entries.append(e)
                    exclude_links.add(e.link)
        except: continue

    def get_priority_score(entry):
        score = time.mktime(entry.get('published_parsed', time.gmtime(0)))
        title = entry.title.lower()
        pub_date = time.strftime("%m-%d", entry.published_parsed) if hasattr(entry, 'published_parsed') else ""
        is_fest = any(k in title for k in ["游戏节", "festival", "fest", "新品节"])
        if is_fest:
            score += 10**10
            if pub_date == now_date: score += 10**11
        return score

    entries.sort(key=get_priority_score, reverse=True)
    slides_html = ""
    for e in entries[:10]:
        title, link = e.title, e.link
        content = e.get('summary', '') or e.get('description', '')
        img = re.search(r'<img [^>]*src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        pub_time = time.strftime("%m-%d %H:%M", e.published_parsed) if hasattr(e, 'published_parsed') else "RECENT"
        is_fest = any(k in title.lower() for k in ["游戏节", "festival", "fest"])
        is_today = (time.strftime("%m-%d", e.published_parsed) == now_date) if hasattr(e, 'published_parsed') else False
        
        highlight = "ring-4 ring-emerald-500 shadow-[0_0_30px_rgba(16,185,129,0.5)] animate-pulse" if is_fest and is_today else ""
        slides_html += f'''
        <div class="swiper-slide group cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-[420px] w-full overflow-hidden rounded-[2.5rem] bg-[#1a1f26] border border-slate-200 dark:border-white/5 {highlight}">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-90 transition-transform duration-1000 group-hover:scale-110">
                <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent opacity-90"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <div class="flex items-center gap-2 mb-2">
                        {"<span class='bg-emerald-500 text-white text-[9px] px-2 py-0.5 rounded italic font-black'>TODAY FESTIVAL</span>" if is_fest and is_today else ""}
                        <span class="font-mono text-[10px] text-blue-400 font-bold tracking-widest">{pub_time}</span>
                    </div>
                    <h2 class="text-xl font-black text-white line-clamp-2 leading-tight italic">{title}</h2>
                </div>
            </div>
        </div>'''
    return slides_html

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    timeline = generate_timeline_html()
    ticker = generate_active_ticker()
    
    # 获取数据
    exclude = set()
    feat_html = get_steam_rss_data("featured", exclude)
    offi_html = get_steam_rss_data("official", exclude)

    template = f'''<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
    <meta charset="UTF-8">
    <title>STEAM INTEL CENTER</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{ 
            darkMode: 'class',
            theme: {{ extend: {{ animation: {{ 'marquee': 'marquee 35s linear infinite' }}, keyframes: {{ marquee: {{ '0%': {{ transform: 'translateX(0%)' }}, '100%': {{ transform: 'translateX(-50%)' }} }} }} }} }}
        }}
        function toggleTheme() {{
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('steam_theme', isDark ? 'dark' : 'light');
        }}
    </script>
    <style>
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .swiper {{ width: 100%; height: 500px; padding: 20px 0 80px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 550px; opacity: 0.1; transition: 0.8s; transform: scale(0.85); filter: blur(4px); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); filter: blur(0); z-index: 20; }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#0b0e14] text-slate-900 dark:text-slate-100 p-6 md:p-16 min-h-screen pb-32">
    <div class="max-w-[1500px] mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-center mb-16 gap-8 text-center md:text-left">
            <div>
                <h1 class="text-7xl font-black italic tracking-tighter uppercase leading-none">Steam<span class="text-blue-600">Intel</span></h1>
                <p class="text-[11px] text-blue-600 font-mono mt-4 tracking-[0.5em] uppercase font-bold">Syncing Sector // {now_time}</p>
            </div>
            <button onclick="toggleTheme()" class="px-8 py-4 bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-white/10 transition-all hover:scale-105 active:scale-95">
                <span class="dark:hidden font-black text-xs tracking-widest text-slate-600">DARK MODE</span>
                <span class="hidden dark:inline font-black text-xs tracking-widest text-blue-400">LIGHT MODE</span>
            </button>
        </header>

        <section class="mb-20">
            <div class="flex items-center gap-4 mb-10">
                <span class="px-4 py-1 bg-blue-600 text-white text-[10px] font-black rounded-full uppercase italic">Official Roadmap</span>
                <div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div>
            </div>
            {timeline}
        </section>

        <main class="space-y-32">
            <section>
                <h2 class="text-5xl font-black italic uppercase mb-8 tracking-tighter">Featured <span class="text-blue-600">精选资讯</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{feat_html}</div><div class="swiper-pagination"></div></div>
            </section>
            <section class="py-16 px-4 md:px-10 rounded-[3rem] border border-slate-200 dark:border-white/5 bg-slate-100/50 dark:bg-white/5">
                <h2 class="text-5xl font-black italic uppercase mb-8 tracking-tighter text-blue-600">Official <span class="dark:text-white">官方公告</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{offi_html}</div><div class="swiper-pagination"></div></div>
            </section>
        </main>
    </div>
    {ticker}
    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        if (localStorage.getItem('steam_theme') === 'light') document.documentElement.classList.remove('dark');
        document.querySelectorAll('.mySwiper').forEach(el => {{
            new Swiper(el, {{
                effect: "coverflow", centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: {{ delay: 6000, disableOnInteraction: false }},
                coverflowEffect: {{ rotate: 0, stretch: 80, depth: 150, modifier: 1.2, slideShadows: false }},
                pagination: {{ el: el.querySelector('.swiper-pagination'), clickable: true }}
            }});
        }});
    </script>
</body>
</html>'''
    with open("index.html", "w", encoding="utf-8") as f: f.write(template)

if __name__ == "__main__":
    update_web()
