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
    html = '<div class="flex flex-nowrap gap-4 overflow-x-auto pb-6 mb-10 no-scrollbar select-none">'
    upcoming = [e for e in STEAM_EVENTS_2026 if int(e['end']) >= curr_int][:8]
    for e in upcoming:
        active = int(e['start']) <= curr_int <= int(e['end'])
        color = {"major": "red-500", "nextfest": "emerald-500", "spotlight": "purple-500"}.get(e['type'], "blue-500")
        html += f'''
        <div class="flex-shrink-0 w-60 p-5 rounded-2xl bg-white/80 dark:bg-slate-900/40 backdrop-blur-xl border border-slate-200 dark:border-white/5 transition-all shadow-sm">
            <div class="flex justify-between items-center mb-3">
                <span class="text-[9px] font-black tracking-tighter {'text-emerald-500 animate-pulse' if active else 'text-slate-400'} uppercase">{'● ACTIVE' if active else '○ PENDING'}</span>
                <span class="text-[10px] font-mono text-slate-400">{e['start'][4:6]}-{e['start'][6:]}</span>
            </div>
            <div class="text-sm font-bold text-slate-800 dark:text-slate-100 truncate mb-3">{e['name']}</div>
            <div class="h-1 w-full bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                <div class="h-full bg-{color} {'shadow-[0_0_8px] shadow-'+color if active else 'opacity-20'}" style="width: {'100%' if active else '20%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def get_steam_rss_data(mode):
    source_map = {
        "featured": ["https://store.steampowered.com/feeds/news/collection/featured/?l=schinese"],
        "official": [
            "https://store.steampowered.com/feeds/news/collection/steam/?l=schinese",
            "https://store.steampowered.com/feeds/news/group/39049601/?l=schinese"
        ]
    }
    
    entries = []
    seen_links = set()
    timestamp = int(time.time())

    for url in source_map.get(mode, []):
        try:
            # 引入随机版本号，彻底击穿缓存
            feed = feedparser.parse(f"{url}&refresh={timestamp}&v={random.random()}")
            for e in feed.entries:
                if e.link not in seen_links:
                    entries.append(e)
                    seen_links.add(e.link)
        except: continue

    # 核心：加权排序算法
    def get_sort_score(entry):
        pub_time = time.mktime(entry.get('published_parsed', time.gmtime(0)))
        title = entry.title.lower()
        # 关键词权重识别
        is_fest = any(k in title for k in ["游戏节", "festival", "fest", "新品节"])
        # 如果是游戏节，权重级别提升 (10^10)，确保其在顶端，同时在顶端内仍按时间排序
        return (10000000000 if is_fest and mode == "featured" else 0) + pub_time

    entries.sort(key=get_sort_score, reverse=True)

    slides_html = ""
    for e in entries[:10]:
        title, link = e.title, e.link
        content = e.get('summary', '') or e.get('description', '')
        img = re.search(r'<img [^>]*src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        pub_time = time.strftime("%m-%d %H:%M", e.published_parsed) if hasattr(e, 'published_parsed') else "RECENT"
        
        # 游戏节高亮标签
        is_fest = any(k in title.lower() for k in ["游戏节", "festival", "fest"])
        fest_tag = '<span class="bg-emerald-500 text-white text-[9px] px-2 py-0.5 rounded mr-2 animate-pulse">FESTIVAL</span>' if is_fest else ""
        
        slides_html += f'''
        <div class="swiper-slide group cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-[420px] w-full overflow-hidden rounded-[2.5rem] bg-white dark:bg-[#1a1f26] border { "border-emerald-500/50 shadow-[0_0_30px_rgba(16,185,129,0.2)]" if is_fest else "border-slate-200 dark:border-white/5" } transition-all duration-500">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-90 dark:opacity-40 transition-transform duration-1000 group-hover:scale-110">
                <div class="absolute inset-0 bg-gradient-to-t from-slate-50 dark:from-[#0b0e14] via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <div class="flex items-center gap-2 mb-3">
                        {fest_tag}
                        <span class="text-[10px] font-mono text-blue-600 dark:text-blue-400 font-bold uppercase tracking-widest">{pub_time} SYNC</span>
                    </div>
                    <h2 class="text-2xl font-black text-slate-900 dark:text-white line-clamp-2 leading-tight tracking-tighter italic">{title}</h2>
                </div>
            </div>
        </div>'''
    return slides_html

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    timeline = generate_timeline_html()
    feat = get_steam_rss_data("featured")
    offi = get_steam_rss_data("official")

    template = f'''<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
    <meta charset="UTF-8">
    <title>STEAM INTEL CENTER</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{ darkMode: 'class' }}
        function toggleTheme() {{
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('steam_theme', isDark ? 'dark' : 'light');
        }}
    </script>
    <style>
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .swiper {{ width: 100%; height: 520px; padding: 20px 0 100px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 550px; opacity: 0.1; transition: 0.8s cubic-bezier(0.2, 1, 0.3, 1); transform: scale(0.8); filter: blur(10px); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); filter: blur(0); z-index: 20; }}
        body {{ transition: background-color 0.6s ease; }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#0b0e14] text-slate-900 dark:text-slate-100 p-6 md:p-16 min-h-screen">
    <div class="max-w-[1500px] mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-center mb-20 gap-8">
            <div class="text-center md:text-left">
                <h1 class="text-7xl font-black italic tracking-tighter uppercase leading-none text-slate-900 dark:text-white">Steam<span class="text-blue-600">Intel</span></h1>
                <p class="text-[11px] text-blue-600 dark:text-blue-500 font-mono mt-4 tracking-[0.5em] uppercase font-bold opacity-80">Terminal Hub // {now_time}</p>
            </div>
            <button onclick="toggleTheme()" class="group px-8 py-4 bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-white/10 transition-all hover:scale-105 active:scale-95">
                <span class="dark:hidden font-black text-xs tracking-widest text-slate-600">DARK MODE</span>
                <span class="hidden dark:inline font-black text-xs tracking-widest text-blue-400">LIGHT MODE</span>
            </button>
        </header>

        <section class="mb-24">
            <div class="flex items-center gap-4 mb-10">
                <span class="px-4 py-1 bg-blue-600 text-white text-[10px] font-black rounded-full uppercase">Operational Roadmap</span>
                <div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div>
            </div>
            {timeline}
        </section>

        <main class="space-y-32">
            <section>
                <h2 class="text-4xl font-black italic uppercase mb-12 tracking-tighter">Featured <span class="text-blue-600">精选资讯</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{feat}</div><div class="swiper-pagination"></div></div>
            </section>
            
            <section>
                <h2 class="text-4xl font-black italic uppercase mb-12 tracking-tighter text-blue-600">Official <span class="dark:text-white">官方公告</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{offi}</div><div class="swiper-pagination"></div></div>
            </section>
        </main>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        if (localStorage.getItem('steam_theme') === 'light') document.documentElement.classList.remove('dark');
        document.querySelectorAll('.mySwiper').forEach(el => {{
            new Swiper(el, {{
                effect: "coverflow", centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: {{ delay: 6000, disableOnInteraction: false }},
                coverflowEffect: {{ rotate: 0, stretch: 100, depth: 150, modifier: 1.5, slideShadows: false }},
                pagination: {{ el: el.querySelector('.swiper-pagination'), clickable: true }}
            }});
        }});
    </script>
</body>
</html>'''
    with open("index.html", "w", encoding="utf-8") as f: f.write(template)

if __name__ == "__main__":
    update_web()
    print("Optimization Complete: Festival Priority Active.")
