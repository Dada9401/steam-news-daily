import feedparser
import datetime
import re

# --- 2026 Steam 官方全年度活动数据库 ---
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
    html = '<div class="flex flex-nowrap gap-4 overflow-x-auto pb-6 mb-10 no-scrollbar select-none">'
    upcoming = [e for e in STEAM_EVENTS_2026 if int(e['end']) >= curr_int][:8]
    for e in upcoming:
        active = int(e['start']) <= curr_int <= int(e['end'])
        color = {"major": "red-500", "nextfest": "yellow-500", "spotlight": "purple-500"}.get(e['type'], "blue-500")
        if active: color = "green-500"
        
        html += f'''
        <div class="flex-shrink-0 w-60 p-4 rounded-2xl bg-white dark:bg-slate-900 shadow-lg dark:shadow-none border border-slate-100 dark:border-white/5 transition-colors duration-500">
            <div class="flex justify-between items-center mb-1">
                <span class="text-[9px] font-black text-{color} tracking-widest uppercase">{'● LIVE' if active else '○ READY'}</span>
                <span class="text-[9px] font-mono text-slate-400 dark:text-gray-500">{e['start'][4:6]}/{e['start'][6:]}</span>
            </div>
            <div class="text-sm font-bold text-slate-800 dark:text-white truncate mb-2">{e['name']}</div>
            <div class="h-1 w-full bg-slate-100 dark:bg-white/10 rounded-full overflow-hidden">
                <div class="h-full bg-{color} {'animate-pulse' if active else 'opacity-30'}" style="width: {'100%' if active else '20%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def get_steam_rss_data(url_type):
    sources = []
    if url_type == "featured":
        sources = ["https://store.steampowered.com/feeds/news/collection/featured/?l=schinese", "https://store.steampowered.com/feeds/news/collection/all/?l=schinese"]
    else:
        sources = ["https://steamcommunity.com/groups/steam/rss/?l=schinese", "https://store.steampowered.com/feeds/news/app/3985950/?l=schinese", "https://store.steampowered.com/feeds/news/app/594650/?l=schinese"]

    all_entries = []
    seen_links = set()
    for url in sources:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if entry.link not in seen_links:
                    all_entries.append(entry)
                    seen_links.add(entry.link)
        except: continue

    keywords = ["新品节", "Next Fest", "官方公告", "新鲜出炉", "路线图", "特卖"]
    all_entries.sort(key=lambda e: any(kw in e.title for kw in keywords), reverse=True)

    slides_html = ""
    for entry in all_entries[:10]:
        title, link = entry.title, entry.link
        content = entry.get('summary', '') or entry.get('description', '')
        img_match = re.search(r'<img [^>]*src="([^"]+)"', content)
        img_url = img_match.group(1) if img_match else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        
        is_hot = any(kw in title for kw in ["新品节", "Next Fest"])
        tag = '<span class="bg-yellow-400 text-black text-[10px] px-2 py-0.5 rounded font-black mr-2">OFFICIAL</span>' if is_hot else ""
        
        slides_html += f'''
        <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-full w-full overflow-hidden rounded-[2rem] bg-slate-100 dark:bg-slate-900 border {"border-yellow-400/50" if is_hot else "border-slate-200 dark:border-white/5"} group transition-all duration-500">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-80 dark:opacity-50 transition-transform duration-700 group-hover:scale-105">
                <div class="absolute inset-0 bg-gradient-to-t from-white/90 dark:from-black via-transparent to-transparent transition-colors duration-500"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <h2 class="text-xl font-black text-slate-900 dark:text-white line-clamp-2 leading-tight">{tag}{title}</h2>
                </div>
            </div>
        </div>'''
    return slides_html

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    timeline = generate_timeline_html()
    feat = get_steam_rss_data("featured")
    offi = get_steam_rss_data("steam")

    html = f'''<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
    <meta charset="UTF-8">
    <title>STEAM INTEL 2026</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{ darkMode: 'class' }}
        function toggleDark() {{
            document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
        }}
    </script>
    <style>
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .swiper {{ width: 100%; height: 420px; padding: 20px 0 80px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 500px; opacity: 0.15; transition: 0.6s; transform: scale(0.8); filter: blur(4px); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); filter: blur(0); z-index: 10; }}
        body {{ transition: background-color 0.5s, color 0.5s; }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#020408] text-slate-900 dark:text-white p-6 md:p-12">
    <div class="max-w-[1500px] mx-auto">
        <header class="flex justify-between items-center mb-12 border-b border-slate-200 dark:border-white/10 pb-8">
            <div>
                <h1 class="text-5xl font-black italic tracking-tighter uppercase leading-none">News Console</h1>
                <p class="text-[10px] text-blue-600 dark:text-blue-500 font-mono mt-3 tracking-[0.5em] uppercase">Deep Scanning Active // {now_time}</p>
            </div>
            <button onclick="toggleDark()" class="p-3 rounded-full bg-white dark:bg-slate-800 shadow-xl border border-slate-200 dark:border-white/10 hover:scale-110 transition-transform">
                <span class="dark:hidden">🌙 夜间模式</span>
                <span class="hidden dark:inline">☀️ 日间模式</span>
            </button>
        </header>

        <section class="mb-16">
            <div class="text-[10px] font-black text-slate-400 dark:text-gray-500 uppercase tracking-[0.4em] mb-6">2026 Official Pipeline</div>
            {timeline}
        </section>

        <main class="space-y-20">
            <section>
                <h2 class="text-2xl font-black uppercase italic mb-6 border-l-4 border-blue-600 pl-4">Featured / 精选</h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{feat}</div><div class="swiper-pagination"></div></div>
            </section>
            <section>
                <h2 class="text-2xl font-black uppercase italic mb-6 border-l-4 border-blue-500 pl-4">Official / 官方公告</h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{offi}</div><div class="swiper-pagination"></div></div>
            </section>
        </main>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        if (localStorage.getItem('theme') === 'light') document.documentElement.classList.remove('dark');
        document.querySelectorAll('.mySwiper').forEach(el => {{
            new Swiper(el, {{
                effect: "coverflow", centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: {{ delay: 5000 }},
                coverflowEffect: {{ rotate: 0, stretch: 80, depth: 150, modifier: 1, slideShadows: false }},
                pagination: {{ el: el.querySelector('.swiper-pagination'), clickable: true }}
            }});
        }});
    </script>
</body>
</html>'''
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    update_web()
