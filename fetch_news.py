import feedparser
import datetime
import re
import time

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
        color = {"major": "red-500", "nextfest": "yellow-500", "spotlight": "purple-500"}.get(e['type'], "blue-500")
        if active: color = "green-500"
        
        html += f'''
        <div class="flex-shrink-0 w-60 p-5 rounded-3xl bg-white dark:bg-slate-900 shadow-xl dark:shadow-none border border-slate-100 dark:border-white/5 transition-all duration-500">
            <div class="flex justify-between items-center mb-2">
                <span class="text-[10px] font-black text-{color} tracking-widest uppercase">{'● LIVE' if active else '○ READY'}</span>
                <span class="text-[10px] font-mono text-slate-400 dark:text-gray-500">{e['start'][4:6]}/{e['start'][6:]}</span>
            </div>
            <div class="text-sm font-bold text-slate-800 dark:text-white truncate mb-3">{e['name']}</div>
            <div class="h-1.5 w-full bg-slate-100 dark:bg-white/10 rounded-full overflow-hidden">
                <div class="h-full bg-{color} {'animate-pulse shadow-[0_0_8px]' if active else 'opacity-30'}" style="width: {'100%' if active else '25%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def get_steam_rss_data(mode):
    # 官方源矩阵：锁定博客原地址，确保第一手资讯
    if mode == "featured":
        urls = ["https://store.steampowered.com/feeds/news/collection/featured/?l=schinese"]
    else:
        urls = [
            "https://store.steampowered.com/feeds/news/group/39049601/?l=schinese", # 官方博客
            "https://store.steampowered.com/feeds/news/group/4145017/?l=schinese", # Steamworks
            "https://store.steampowered.com/feeds/news/app/3985950/?l=schinese",   # 2月新品节专页
        ]

    entries = []
    seen_links = set()
    timestamp = int(time.time())

    for url in urls:
        try:
            # 加上 t 参数击穿 CDN 缓存，抓取秒级更新
            feed = feedparser.parse(f"{url}&t={timestamp}")
            for e in feed.entries:
                if e.link not in seen_links:
                    if mode == "official":
                        # 严格过滤：只保留 Valve 官方发布的、带关键字的核心内容
                        if any(k in e.title for k in ["Steam", "新品节", "Next Fest", "公告", "2026", "新鲜出炉"]):
                            entries.append(e)
                            seen_links.add(e.link)
                    else:
                        entries.append(e)
                        seen_links.add(e.link)
        except: continue

    # 按发布时间戳进行绝对降序排列
    def get_pub_time(entry):
        if hasattr(entry, 'published_parsed'):
            return time.mktime(entry.published_parsed)
        return 0

    entries.sort(key=get_pub_time, reverse=True)

    slides_html = ""
    for e in entries[:10]:
        title, link = e.title, e.link
        content = e.get('summary', '') or e.get('description', '')
        img = re.search(r'<img [^>]*src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        
        pub_time_str = time.strftime("%m-%d %H:%M", e.published_parsed) if hasattr(e, 'published_parsed') else ""
        
        is_official_alert = any(k in title for k in ["新品节", "Next Fest", "公告"])
        tag = '<span class="bg-yellow-400 text-black text-[10px] px-2 py-0.5 rounded font-black mr-2 shadow-sm">LATEST OFFICIAL</span>' if is_official_alert else ""
        
        slides_html += f'''
        <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-full w-full overflow-hidden rounded-[2.5rem] bg-slate-100 dark:bg-slate-900 border {"border-yellow-400/60 shadow-2xl" if is_official_alert else "border-slate-200 dark:border-white/5"} group transition-all duration-500">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-90 dark:opacity-40 transition-transform duration-1000 group-hover:scale-110">
                <div class="absolute inset-0 bg-gradient-to-t from-white/95 dark:from-[#020408] via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <div class="text-[10px] font-mono text-blue-600 dark:text-blue-400 mb-2 font-bold uppercase tracking-widest">{pub_time_str} SYNCED</div>
                    <h2 class="text-2xl font-black text-slate-900 dark:text-white line-clamp-2 leading-[1.1] tracking-tighter italic">{tag}{title}</h2>
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
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        }}
    </script>
    <style>
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .swiper {{ width: 100%; height: 450px; padding: 20px 0 100px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 550px; opacity: 0.1; transition: 0.7s cubic-bezier(0.2, 1, 0.3, 1); transform: scale(0.85); filter: blur(8px); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); filter: blur(0); z-index: 20; }}
        body {{ transition: background-color 0.6s cubic-bezier(0.4, 0, 0.2, 1); }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#020408] text-slate-900 dark:text-white p-6 md:p-16 min-h-screen">
    <div class="max-w-[1600px] mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-start md:items-center mb-20 gap-8">
            <div class="border-l-8 border-blue-600 pl-8">
                <h1 class="text-7xl font-black italic tracking-tighter uppercase leading-none text-slate-900 dark:text-white">Steam Intel</h1>
                <p class="text-[11px] text-blue-600 dark:text-blue-500 font-mono mt-4 tracking-[0.6em] uppercase font-bold">Terminal Connected // {now_time}</p>
            </div>
            <button onclick="toggleTheme()" class="group relative px-8 py-4 bg-white dark:bg-slate-800 rounded-full shadow-2xl border border-slate-200 dark:border-white/10 transition-all hover:scale-105 active:scale-95">
                <span class="dark:hidden font-black text-sm text-slate-700 tracking-tighter">🌙 ENTER NIGHT MODE</span>
                <span class="hidden dark:inline font-black text-sm text-blue-400 tracking-tighter">☀️ ACTIVATE DAYLIGHT</span>
            </button>
        </header>

        <section class="mb-20">
            <div class="flex items-center gap-4 mb-8">
                <span class="px-3 py-1 bg-blue-600 text-white text-[10px] font-black rounded-sm uppercase tracking-widest">Roadmap</span>
                <div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div>
            </div>
            {timeline}
        </section>

        <main class="space-y-32">
            <section>
                <h2 class="text-4xl font-black italic uppercase mb-10 tracking-tighter">Featured <span class="text-blue-600 dark:text-blue-500">精选资讯</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{feat}</div><div class="swiper-pagination"></div></div>
            </section>
            
            <section>
                <h2 class="text-4xl font-black italic uppercase mb-10 tracking-tighter text-blue-600 dark:text-blue-400">Official <span class="dark:text-white">官方公告</span></h2>
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
                autoplay: {{ delay: 5000, disableOnInteraction: false }},
                coverflowEffect: {{ rotate: 0, stretch: 120, depth: 200, modifier: 1, slideShadows: false }},
                pagination: {{ el: el.querySelector('.swiper-pagination'), clickable: true }}
            }});
        }});
    </script>
</body>
</html>'''
    with open("index.html", "w", encoding="utf-8") as f: f.write(template)

if __name__ == "__main__":
    update_web()
