import feedparser
import datetime
import re
import time

# --- 2026 Steam 活动节点（核心数据） ---
STEAM_EVENTS_2026 = [
    {"name": "棋盘游戏节", "start": "20260126", "end": "20260202", "type": "fest"},
    {"name": "打字节 (焦点节)", "start": "20260205", "end": "20260209", "type": "spotlight"},
    {"name": "PvP 游戏节", "start": "20260209", "end": "20260216", "type": "fest"},
    {"name": "Steam 新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest", "appid": "3985950"},
    {"name": "Steam 春季特卖", "start": "20260319", "end": "20260326", "type": "major"},
]

def generate_timeline_html():
    now_int = int(datetime.datetime.now().strftime("%Y%m%d"))
    html = '<div class="flex flex-nowrap gap-4 overflow-x-auto pb-6 mb-10 no-scrollbar">'
    upcoming = [e for e in STEAM_EVENTS_2026 if int(e['end']) >= now_int][:8]
    for e in upcoming:
        is_live = int(e['start']) <= now_int <= int(e['end'])
        color = "green-500" if is_live else "blue-500"
        if e['type'] == "nextfest": color = "yellow-500"
        
        html += f'''
        <div class="flex-shrink-0 w-60 p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-white/5 shadow-lg transition-all">
            <div class="flex justify-between items-center mb-2">
                <span class="text-[10px] font-black text-{color} tracking-widest uppercase">{'● ACTIVE' if is_live else '○ UPCOMING'}</span>
                <span class="text-[10px] font-mono text-slate-400">{e['start'][4:6]}/{e['start'][6:]}</span>
            </div>
            <div class="text-sm font-bold text-slate-800 dark:text-white truncate mb-3">{e['name']}</div>
            <div class="h-1.5 w-full bg-slate-100 dark:bg-white/10 rounded-full">
                <div class="h-full bg-{color} {'animate-pulse' if is_live else 'opacity-30'}" style="width: {'100%' if is_live else '20%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def get_steam_content(mode):
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if mode == "featured":
        # 抓取多个源来确保“游戏节”新闻不漏掉
        urls = [
            "https://store.steampowered.com/feeds/news/collection/featured/?l=schinese",
            "https://store.steampowered.com/feeds/news/collection/all/?l=schinese"
        ]
    else:
        urls = [
            "https://steamcommunity.com/groups/steam/rss/", # 官方最快源
            "https://store.steampowered.com/feeds/news/app/3985950/?l=schinese" # 2月新品节定向
        ]

    entries = []
    seen = set()
    for url in urls:
        try:
            feed = feedparser.parse(f"{url}?cache={time.time()}")
            for e in feed.entries:
                if e.link not in seen:
                    entries.append(e)
                    seen.add(e.link)
        except: continue

    # --- 权重算法核心 ---
    def calculate_score(entry):
        score = 0
        title = entry.title
        # 1. 基础时间分（发布越晚分越高）
        pub_ts = time.mktime(entry.published_parsed) if hasattr(entry, 'published_parsed') else 0
        score += pub_ts / 1000000 
        
        # 2. 关键词加权：精选资讯里的“游戏节”
        if mode == "featured":
            if any(k in title for k in ["游戏节", "Fest", "新品节"]):
                score += 5000
                # 如果是今天发布的，再给 10000 分，确保排在第一
                pub_date = time.strftime("%Y-%m-%d", entry.published_parsed) if hasattr(entry, 'published_parsed') else ""
                if pub_date == today_str:
                    score += 10000
        
        # 3. 官方板块加权：Steam 官方字样
        if mode == "official":
            if "Steam" in title or "公告" in title:
                score += 2000
        return score

    entries.sort(key=calculate_score, reverse=True)

    html = ""
    for e in entries[:10]:
        title, link = e.title, e.link
        content = e.get('summary', '') or e.get('description', '')
        img = re.search(r'src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        
        ts = e.get('published_parsed', (2026, 2, 2, 0, 0, 0))
        date_str = f"{ts[1]:02d}-{ts[2]:02d} {ts[3]:02d}:{ts[4]:02d}"
        
        is_fest = any(k in title for k in ["游戏节", "Fest"])
        
        html += f'''
        <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-full w-full rounded-[2.5rem] overflow-hidden bg-white dark:bg-slate-900 border-2 {"border-yellow-400 shadow-[0_0_25px_rgba(250,204,21,0.3)]" if is_fest else "border-transparent dark:border-white/5"} transition-all duration-500 group">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-90 dark:opacity-40 group-hover:scale-110 transition-transform duration-1000">
                <div class="absolute inset-0 bg-gradient-to-t from-white/95 dark:from-black via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <div class="flex items-center gap-2 mb-2">
                        <span class="text-[10px] font-black text-blue-600 dark:text-blue-400 tracking-widest">{date_str}</span>
                        { '<span class="px-2 py-0.5 bg-yellow-400 text-black text-[9px] font-black rounded">HOT FEST</span>' if is_fest else '' }
                    </div>
                    <h3 class="text-2xl font-black text-slate-900 dark:text-white line-clamp-2 leading-tight tracking-tighter uppercase italic">{title}</h3>
                </div>
            </div>
        </div>'''
    return html

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    timeline = generate_timeline_html()
    feat = get_steam_content("featured")
    offi = get_steam_content("official")

    template = f'''<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
    <meta charset="UTF-8">
    <title>STEAM INTEL 2026</title>
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
        .swiper {{ width: 100%; height: 520px; padding: 20px 0 100px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 580px; opacity: 0.1; transition: 0.8s cubic-bezier(0.2, 1, 0.3, 1); transform: scale(0.8); filter: blur(10px); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); filter: blur(0); z-index: 50; }}
        body {{ transition: background 0.8s; }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#020408] text-slate-900 dark:text-white p-6 md:p-16 min-h-screen">
    <div class="max-w-[1700px] mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-end mb-20 gap-8">
            <div class="border-l-[12px] border-blue-600 pl-8">
                <h1 class="text-8xl font-black italic tracking-tighter uppercase leading-none">News Console</h1>
                <p class="text-[12px] text-blue-600 font-mono mt-4 tracking-[0.8em] font-black uppercase">Active // {now_time}</p>
            </div>
            <button onclick="toggleMode()" class="px-10 py-5 bg-white dark:bg-slate-800 rounded-full shadow-2xl border border-slate-200 dark:border-white/10 transition-all active:scale-95">
                <span class="dark:hidden font-black text-xs text-slate-700">🌙 NIGHT MODE</span>
                <span class="hidden dark:inline font-black text-xs text-blue-400">☀️ LIGHT MODE</span>
            </button>
        </header>

        <section class="mb-20">
            <div class="flex items-center gap-4 mb-8">
                <span class="px-3 py-1 bg-blue-600 text-white text-[10px] font-black rounded-sm uppercase tracking-widest">Steam Roadmap</span>
                <div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div>
            </div>
            {timeline}
        </section>

        <main class="space-y-40">
            <section>
                <h2 class="text-4xl font-black italic uppercase mb-12 tracking-tighter">Featured <span class="text-blue-600 italic">精选资讯 (游戏节优先)</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{feat}</div><div class="swiper-pagination"></div></div>
            </section>
            
            <section>
                <h2 class="text-4xl font-black italic uppercase mb-12 tracking-tighter text-blue-600 dark:text-blue-400">Official <span class="dark:text-white">官方动态</span></h2>
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
