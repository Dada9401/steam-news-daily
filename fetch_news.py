import feedparser
import datetime
import re
import time

# --- 2026 Steam 活动节点 ---
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
        active = int(e['start']) <= now_int <= int(e['end'])
        color = "green-500" if active else "blue-500"
        if e['type'] == "nextfest": color = "yellow-500"
        html += f'''
        <div class="flex-shrink-0 w-60 p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-white/5 shadow-xl transition-all duration-500">
            <div class="flex justify-between items-center mb-2">
                <span class="text-[10px] font-black text-{color} tracking-widest uppercase">{'● ACTIVE' if active else '○ READY'}</span>
                <span class="text-[10px] font-mono text-slate-400">{e['start'][4:6]}/{e['start'][6:]}</span>
            </div>
            <div class="text-sm font-bold text-slate-800 dark:text-white truncate mb-3">{e['name']}</div>
            <div class="h-1.5 w-full bg-slate-100 dark:bg-white/10 rounded-full overflow-hidden">
                <div class="h-full bg-{color} {'animate-pulse' if active else 'opacity-30'}" style="width: {'100%' if active else '20%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def get_news_html(mode):
    # 彻底分开数据源
    if mode == "featured":
        # 精选流：使用商店集合源，方便抓取各类游戏节资讯
        urls = ["https://store.steampowered.com/feeds/news/collection/featured/?l=schinese"]
    else:
        # 官方流：只锁定官方社区组 RSS，绝不掺杂任何游戏广告
        urls = ["https://steamcommunity.com/groups/steam/rss/"]

    entries = []
    seen = set()
    today_str = datetime.datetime.now().strftime("%m-%d")

    for url in urls:
        try:
            feed = feedparser.parse(f"{url}?t={time.time()}")
            for e in feed.entries:
                if e.link not in seen:
                    entries.append(e)
                    seen.add(e.link)
        except: continue

    # --- 精确排序逻辑 ---
    if mode == "featured":
        # 规则：游戏节关键词 > 发布时间
        def featured_sort(x):
            score = 0
            t_str = x.title.lower()
            # 关键词加分
            if any(k in t_str for k in ["游戏节", "fest", "新品节"]): score += 10000000000
            # 时间加分（秒级时间戳）
            if hasattr(x, 'published_parsed'): score += time.mktime(x.published_parsed)
            return score
        entries.sort(key=featured_sort, reverse=True)
    else:
        # 规则：纯时间倒序，不加任何权重
        entries.sort(key=lambda x: x.get('published_parsed', 0), reverse=True)

    html = ""
    for e in entries[:10]:
        title = e.title
        link = e.link
        content = e.get('summary', '') or e.get('description', '')
        img = re.search(r'src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        
        # 格式化时间
        ts = e.get('published_parsed', (2026, 2, 2, 0, 0, 0))
        date_str = f"{ts[1]:02d}-{ts[2]:02d} {ts[3]:02d}:{ts[4]:02d}"
        
        # 标识游戏节
        is_fest = any(k in title for k in ["游戏节", "Fest", "Next Fest"])
        tag = '<span class="px-2 py-0.5 bg-yellow-400 text-black text-[9px] font-black rounded mr-2">GAME FEST</span>' if is_fest else ""
        
        html += f'''
        <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-full w-full rounded-[2.5rem] overflow-hidden bg-white dark:bg-slate-900 border-2 {"border-yellow-500 shadow-2xl" if is_fest else "border-transparent dark:border-white/5"} transition-all duration-500 group">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-90 dark:opacity-40 group-hover:scale-105 transition-transform duration-1000">
                <div class="absolute inset-0 bg-gradient-to-t from-white/95 dark:from-[#020408] via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <div class="text-[10px] font-mono text-blue-600 dark:text-blue-400 mb-2 font-bold">{date_str} SYNC</div>
                    <h3 class="text-2xl font-black text-slate-900 dark:text-white line-clamp-2 leading-tight tracking-tighter italic uppercase">{tag}{title}</h3>
                </div>
            </div>
        </div>'''
    return html

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    timeline = generate_timeline_html()
    feat_content = get_news_html("featured")
    offi_content = get_news_html("official")

    template = f'''<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
    <meta charset="UTF-8">
    <title>STEAM INTEL 2026</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{ darkMode: 'class' }}
        function toggleTheme() {{
            document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
        }}
    </script>
    <style>
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .swiper {{ width: 100%; height: 500px; padding: 20px 0 100px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 560px; opacity: 0.1; transition: 0.7s; transform: scale(0.85); filter: blur(8px); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); filter: blur(0); z-index: 50; }}
        body {{ transition: background 0.8s; }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#020408] text-slate-900 dark:text-white p-6 md:p-16 min-h-screen">
    <div class="max-w-[1700px] mx-auto">
        <header class="flex justify-between items-end mb-16 border-l-[12px] border-blue-600 pl-10">
            <div>
                <h1 class="text-8xl font-black italic tracking-tighter uppercase leading-none text-slate-900 dark:text-white">INTEL</h1>
                <p class="text-[12px] text-blue-600 dark:text-blue-500 font-mono mt-4 tracking-[0.8em] font-black uppercase">COMMUNITY SYNC // {now_time}</p>
            </div>
            <button onclick="toggleTheme()" class="px-8 py-4 bg-white dark:bg-slate-800 rounded-full shadow-2xl border border-slate-200 dark:border-white/10 active:scale-95 transition-all">
                <span class="dark:hidden font-black text-xs text-slate-700">🌙 NIGHT MODE</span>
                <span class="hidden dark:inline font-black text-xs text-blue-400">☀️ LIGHT MODE</span>
            </button>
        </header>

        <section class="mb-20">
            <div class="flex items-center gap-4 mb-8"><span class="px-3 py-1 bg-blue-600 text-white text-[10px] font-black uppercase">Pipeline</span><div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div></div>
            {timeline}
        </section>

        <main class="space-y-40">
            <section>
                <h2 class="text-4xl font-black italic uppercase mb-10 tracking-tighter">Featured <span class="text-blue-600 italic">精选资讯 (游戏节置顶)</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{feat_content}</div><div class="swiper-pagination"></div></div>
            </section>
            
            <section>
                <h2 class="text-4xl font-black italic uppercase mb-10 tracking-tighter text-blue-600">Official <span class="dark:text-white">官方社区实时动态</span></h2>
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
