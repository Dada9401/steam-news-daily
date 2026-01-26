import feedparser
import datetime
import re
import time

# --- 2026 Steam 官方活动时间轴数据 ---
STEAM_EVENTS_2026 = [
    {"name": "棋盘游戏节", "start": "20260126", "end": "20260202", "type": "fest"},
    {"name": "打字节 (焦点节)", "start": "20260205", "end": "20260209", "type": "spotlight"},
    {"name": "PvP 游戏节", "start": "20260209", "end": "20260216", "type": "fest"},
    {"name": "Steam 新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest", "appid": "3985950"},
    {"name": "Steam 春季特卖", "start": "20260319", "end": "20260326", "type": "major"},
]

def generate_timeline_html():
    now = datetime.datetime.now()
    curr_int = int(now.strftime("%Y%m%d"))
    html = '<div class="flex flex-nowrap gap-4 overflow-x-auto pb-6 mb-10 no-scrollbar select-none">'
    # 只显示还没结束的活动
    upcoming = [e for e in STEAM_EVENTS_2026 if int(e['end']) >= curr_int][:8]
    for e in upcoming:
        is_live = int(e['start']) <= curr_int <= int(e['end'])
        color = {"major": "red-500", "nextfest": "yellow-500", "spotlight": "purple-500"}.get(e['type'], "blue-500")
        if is_live: color = "green-500"
        
        html += f'''
        <div class="flex-shrink-0 w-60 p-5 rounded-2xl bg-white dark:bg-slate-900 shadow-lg dark:shadow-none border border-slate-100 dark:border-white/5 transition-all">
            <div class="flex justify-between items-center mb-2">
                <span class="text-[10px] font-black text-{color} tracking-widest uppercase">{'● LIVE' if is_live else '○ READY'}</span>
                <span class="text-[10px] font-mono text-slate-400 dark:text-gray-500">{e['start'][4:6]}/{e['start'][6:]}</span>
            </div>
            <div class="text-sm font-bold text-slate-800 dark:text-white truncate mb-3">{e['name']}</div>
            <div class="h-1.5 w-full bg-slate-100 dark:bg-white/10 rounded-full overflow-hidden">
                <div class="h-full bg-{color} {'animate-pulse' if is_live else 'opacity-30'}" style="width: {'100%' if is_live else '25%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def get_steam_data(mode):
    # 使用包含社区原生的 RSS，解决商店延迟问题
    if mode == "featured":
        urls = ["https://store.steampowered.com/feeds/news/collection/featured/?l=schinese"]
    else:
        urls = [
            "https://steamcommunity.com/groups/steam/rss/", 
            "https://store.steampowered.com/feeds/news/group/39049601/?l=schinese"
        ]

    all_entries = []
    seen = set()
    for url in urls:
        try:
            feed = feedparser.parse(f"{url}?t={int(time.time())}")
            for e in feed.entries:
                if e.link not in seen:
                    if mode == "official":
                        # 官方板块过滤逻辑：确保内容与 1月26日 后的官方动态相关
                        if any(k in e.title for k in ["Steam", "新品节", "2026", "公告", "Next Fest"]):
                            all_entries.append(e)
                            seen.add(e.link)
                    else:
                        all_entries.append(e)
                        seen.add(e.link)
        except: continue

    # 核心：绝对时间戳降序排列，1月26日的新闻必在第一张
    all_entries.sort(key=lambda x: x.get('published_parsed', (2026, 1, 1, 0, 0, 0)), reverse=True)

    html = ""
    for e in all_entries[:12]:
        title, link = e.title, e.link
        content = e.get('summary', '') or e.get('description', '')
        img = re.search(r'src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        
        # 处理时间戳显示
        ts = e.get('published_parsed', (2026, 1, 1, 0, 0, 0))
        date_str = f"{ts[1]:02d}-{ts[2]:02d} {ts[3]:02d}:{ts[4]:02d}"
        
        # 24小时内的新闻加闪烁标记
        is_flash = (time.time() - time.mktime(ts)) < 86400

        html += f'''
        <div class="swiper-slide group cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-full w-full rounded-[2.5rem] overflow-hidden bg-white dark:bg-slate-900 border-2 {"border-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.3)]" if is_flash else "border-transparent dark:border-white/5"} transition-all duration-500">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-90 dark:opacity-40 group-hover:scale-105 transition-transform duration-1000">
                <div class="absolute inset-0 bg-gradient-to-t from-white/95 dark:from-[#020408] via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <div class="flex items-center gap-2 mb-2">
                        { '<span class="w-2 h-2 bg-blue-500 rounded-full animate-ping"></span>' if is_flash else '' }
                        <span class="text-[10px] font-black text-blue-600 dark:text-blue-400 tracking-widest uppercase">{date_str} SYNCED</span>
                    </div>
                    <h3 class="text-2xl font-black text-slate-900 dark:text-white line-clamp-2 leading-[1.1] tracking-tighter italic">{title}</h3>
                </div>
            </div>
        </div>'''
    return html

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    timeline = generate_timeline_html()
    feat = get_steam_data("featured")
    offi = get_steam_data("official")

    template = f'''<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
    <meta charset="UTF-8">
    <title>STEAM INTEL CENTER</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{ darkMode: 'class' }}
        function toggleMode() {{
            document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
        }}
    </script>
    <style>
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .swiper {{ width: 100%; height: 500px; padding: 20px 0 100px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 560px; opacity: 0.1; transition: 0.8s cubic-bezier(0.2, 1, 0.3, 1); transform: scale(0.85); filter: blur(10px); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); filter: blur(0); z-index: 50; }}
        body {{ transition: background 0.8s; }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#020408] text-slate-900 dark:text-white p-6 md:p-16 min-h-screen font-sans">
    <div class="max-w-[1700px] mx-auto">
        <header class="flex justify-between items-end mb-16 border-l-[12px] border-blue-600 pl-10">
            <div>
                <h1 class="text-8xl font-black italic tracking-tighter uppercase leading-none">Intel</h1>
                <p class="text-[11px] text-blue-600 dark:text-blue-500 font-mono mt-4 tracking-[0.8em] font-black uppercase">Active Sync // 2026-01-26 // {now_time}</p>
            </div>
            <button onclick="toggleMode()" class="px-8 py-4 bg-white dark:bg-slate-800 rounded-full shadow-2xl border border-slate-200 dark:border-white/10 transition-all active:scale-95">
                <span class="dark:hidden font-black text-xs text-slate-700">🌙 DARK SCAN</span>
                <span class="hidden dark:inline font-black text-xs text-blue-400">☀️ LIGHT SCAN</span>
            </button>
        </header>

        <section class="mb-20">
            <div class="flex items-center gap-4 mb-8">
                <span class="px-3 py-1 bg-blue-600 text-white text-[10px] font-black rounded-sm uppercase tracking-widest">Pipeline</span>
                <div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div>
            </div>
            {timeline}
        </section>

        <main class="space-y-40">
            <section>
                <h2 class="text-4xl font-black italic uppercase mb-10 tracking-tighter">Featured <span class="text-blue-600">精选流</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{feat}</div><div class="swiper-pagination"></div></div>
            </section>
            
            <section>
                <h2 class="text-4xl font-black italic uppercase mb-10 tracking-tighter text-blue-600 dark:text-blue-400">Official <span class="dark:text-white">官方实时</span></h2>
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
                coverflowEffect: {{ rotate: 0, stretch: 100, depth: 300, modifier: 1, slideShadows: false }},
                pagination: {{ el: el.querySelector('.swiper-pagination'), clickable: true }}
            }});
        }});
    </script>
</body>
</html>'''
    with open("index.html", "w", encoding="utf-8") as f: f.write(template)

if __name__ == "__main__":
    update_web()
