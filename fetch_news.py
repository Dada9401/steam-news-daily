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
        <div class="flex-shrink-0 w-64 p-6 rounded-[2rem] bg-white dark:bg-slate-900 shadow-xl border border-slate-100 dark:border-white/5 transition-all">
            <div class="flex justify-between items-center mb-3">
                <span class="text-[10px] font-black text-{color} tracking-widest uppercase">{'● ACTIVE' if active else '○ READY'}</span>
                <span class="text-[10px] font-mono text-slate-400 dark:text-gray-500">{e['start'][4:6]}/{e['start'][6:]}</span>
            </div>
            <div class="text-sm font-black text-slate-800 dark:text-white truncate mb-4 uppercase italic tracking-tighter">{e['name']}</div>
            <div class="h-1.5 w-full bg-slate-100 dark:bg-white/10 rounded-full overflow-hidden">
                <div class="h-full bg-{color} {'animate-pulse' if active else 'opacity-30'}" style="width: {'100%' if active else '25%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def get_steam_rss_data(mode):
    # 物理隔离数据源：精选抓商店，官方抓社区博客
    if mode == "featured":
        urls = ["https://store.steampowered.com/feeds/news/collection/featured/?l=schinese"]
    else:
        urls = ["https://steamcommunity.com/groups/steam/rss/"]

    entries = []
    seen_links = set()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    for url in urls:
        try:
            feed = feedparser.parse(f"{url}?t={int(time.time())}")
            for e in feed.entries:
                if e.link not in seen_links:
                    entries.append(e)
                    seen_links.add(e.link)
        except: continue

    # ==========================================
    # 核心权重算法：解决“游戏节”置顶问题
    # ==========================================
    def calculate_score(entry):
        score = 0
        # 1. 基础时间分（秒级时间戳）
        pub_ts = time.mktime(entry.published_parsed) if hasattr(entry, 'published_parsed') else 0
        score += pub_ts
        
        # 2. 关键词加权逻辑 (针对精选板块)
        if mode == "featured":
            title = entry.title.lower()
            if any(k in title for k in ["游戏节", "fest", "新品节", "festival"]):
                score += 10**12  # 给一个天文数字权重
                
                # 3. 如果是今天(2月2日)发布的游戏节，再额外加权
                pub_date = time.strftime("%Y-%m-%d", entry.published_parsed) if hasattr(entry, 'published_parsed') else ""
                if pub_date == today_str:
                    score += 10**13
        return score

    entries.sort(key=calculate_score, reverse=True)

    slides_html = ""
    for e in entries[:10]:
        title, link = e.title, e.link
        content = e.get('summary', '') or e.get('description', '')
        img = re.search(r'src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        
        pub_time = time.strftime("%m-%d %H:%M", e.published_parsed) if hasattr(e, 'published_parsed') else "RECENT"
        is_fest = any(k in title.lower() for k in ["游戏节", "fest", "新品节"])
        
        slides_html += f'''
        <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-full w-full overflow-hidden rounded-[2.5rem] bg-white dark:bg-slate-900 border-2 {"border-yellow-400 shadow-[0_0_30px_rgba(250,204,21,0.2)]" if is_fest else "border-transparent dark:border-white/5"} group transition-all duration-500">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-90 dark:opacity-40 transition-transform duration-1000 group-hover:scale-110">
                <div class="absolute inset-0 bg-gradient-to-t from-white/95 dark:from-[#020408] via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <div class="flex items-center gap-2 mb-2">
                        <span class="text-[10px] font-mono text-blue-600 dark:text-blue-400 font-bold uppercase tracking-widest">{pub_time} SYNC</span>
                        { '<span class="px-2 py-0.5 bg-yellow-400 text-black text-[9px] font-black rounded italic">FESTIVAL PRIOR</span>' if is_fest else "" }
                    </div>
                    <h2 class="text-2xl font-black text-slate-900 dark:text-white line-clamp-2 leading-[1.1] tracking-tighter italic uppercase">{title}</h2>
                </div>
            </div>
        </div>'''
    return slides_html

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    timeline = generate_timeline_html()
    feat_content = get_steam_rss_data("featured")
    offi_content = get_steam_rss_data("official")

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
        .swiper {{ width: 100%; height: 500px; padding: 20px 0 100px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 560px; opacity: 0.05; transition: 0.8s cubic-bezier(0.2, 1, 0.3, 1); transform: scale(0.8); filter: blur(12px); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); filter: blur(0); z-index: 50; }}
        body {{ transition: background-color 0.8s; }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#020408] text-slate-900 dark:text-white p-6 md:p-16 min-h-screen">
    <div class="max-w-[1700px] mx-auto">
        <header class="flex justify-between items-end mb-20 border-l-[12px] border-blue-600 pl-10">
            <div>
                <h1 class="text-8xl font-black italic tracking-tighter uppercase leading-none">News Console</h1>
                <p class="text-[12px] text-blue-600 font-mono mt-4 tracking-[0.8em] font-black uppercase italic">2026.02.02 // {now_time}</p>
            </div>
            <button onclick="toggleTheme()" class="px-10 py-5 bg-white dark:bg-slate-800 rounded-full shadow-2xl border border-slate-200 dark:border-white/10 active:scale-95 transition-all">
                <span class="dark:hidden font-black text-xs text-slate-700">🌙 DARK MODE</span>
                <span class="hidden dark:inline font-black text-xs text-blue-400">☀️ LIGHT MODE</span>
            </button>
        </header>

        <section class="mb-24">
            <div class="flex items-center gap-4 mb-10">
                <span class="px-4 py-1.5 bg-blue-600 text-white text-[10px] font-black uppercase tracking-[0.3em]">Pipeline</span>
                <div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div>
            </div>
            {timeline}
        </section>

        <main class="space-y-40">
            <section>
                <h2 class="text-4xl font-black italic uppercase mb-12 tracking-tighter">Featured <span class="text-blue-600 italic">精选资讯 (游戏节置顶)</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{feat_content}</div><div class="swiper-pagination"></div></div>
            </section>
            
            <section>
                <h2 class="text-4xl font-black italic uppercase mb-12 tracking-tighter text-blue-600">Official <span class="dark:text-white italic">官方实时公告</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{offi_content}</div><div class="swiper-pagination"></div></div>
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
                coverflowEffect: {{ rotate: 0, stretch: 80, depth: 300, modifier: 1, slideShadows: false }},
                pagination: {{ el: el.querySelector('.swiper-pagination'), clickable: true }}
            }});
        }});
    </script>
</body>
</html>'''
    with open("index.html", "w", encoding="utf-8") as f: f.write(template)

if __name__ == "__main__":
    update_web()
