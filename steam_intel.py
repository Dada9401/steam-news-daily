import feedparser
import datetime
import re
import time
import random

# ==========================================
# 核心配置：2026 活动数据库 (务必确保 URL 正确)
# ==========================================
STEAM_EVENTS_2026 = [
    {"name": "棋盘游戏节", "start": "20260126", "end": "20260202", "type": "fest", "url": "https://store.steampowered.com/category/tabletop"},
    {"name": "再来一局游戏节 (Tiny Roguelikes)", "start": "20260130", "end": "20260206", "type": "fest", "url": "https://store.steampowered.com/developer/rogueduck/sale/TinyRoguelikes2026"},
    {"name": "打字节 (焦点节)", "start": "20260205", "end": "20260209", "type": "spotlight", "url": "https://store.steampowered.com/category/typing"},
    {"name": "PvP 游戏节", "start": "20260209", "end": "20260216", "type": "fest", "url": "https://store.steampowered.com/category/pvp"},
    {"name": "Steam 新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest", "url": "https://store.steampowered.com/sale/nextfest"},
    {"name": "Steam 春季特卖", "start": "20260319", "end": "20260326", "type": "major", "url": "https://store.steampowered.com/sale/springsale"},
    {"name": "Steam 夏季特卖", "start": "20260625", "end": "20260709", "type": "major", "url": "https://store.steampowered.com/sale/summersale"},
]

THIRD_PARTY_EVENTS = [
    {"name": "GDS GameDev Summit", "start": "20260203", "end": "20260205", "url": "https://gamedevsummit.com/"},
    {"name": "GDC 2026", "start": "20260309", "end": "20260313", "url": "https://gdconf.com/"},
]

def generate_timeline_html():
    now = datetime.datetime.now()
    curr_int = int(now.strftime("%Y%m%d"))
    # 显示所有未来和当前的活动
    upcoming = [e for e in sorted(STEAM_EVENTS_2026, key=lambda x: x['start']) if int(e['end']) >= curr_int]
    
    html = '<div class="flex flex-nowrap gap-4 overflow-x-auto pb-6 mb-10 no-scrollbar select-none">'
    for e in upcoming:
        active = int(e['start']) <= curr_int <= int(e['end'])
        color = "emerald-500" if active else "blue-600"
        html += f'''
        <div class="flex-shrink-0 w-64 p-6 rounded-3xl bg-white/80 dark:bg-slate-900/40 backdrop-blur-xl border border-slate-200 dark:border-white/5 shadow-sm">
            <div class="flex justify-between items-center mb-4">
                <span class="text-[10px] font-black tracking-widest {'text-emerald-500 animate-pulse' if active else 'text-slate-400'} uppercase">{'● ACTIVE' if active else '○ PENDING'}</span>
                <span class="text-[10px] font-mono text-slate-400">{e['start'][4:6]}/{e['start'][6:]}</span>
            </div>
            <div class="text-base font-bold text-slate-800 dark:text-slate-100 truncate mb-4">{e['name']}</div>
            <div class="h-1.5 w-full bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                <div class="h-full bg-{color}" style="width: {'100%' if active else '20%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def generate_active_ticker():
    now = datetime.datetime.now()
    curr_int = int(now.strftime("%Y%m%d"))
    contents = []
    # 逻辑：必须是已开展的活动
    for e in STEAM_EVENTS_2026 + THIRD_PARTY_EVENTS:
        if int(e['start']) <= curr_int <= int(e['end']):
            tag = "[STEAM官方]" if "type" in e else "[第三方]"
            url = e.get('url', 'https://store.steampowered.com/news/')
            # 简化 HTML 结构，确保链接在移动端和桌面端都容易点中
            contents.append(f"<span>🔥 正在开展: {tag} {e['name']}</span> | <a href='{url}' target='_blank' class='text-yellow-400 font-bold hover:underline cursor-pointer px-2'>[进入会场]</a>")

    if not contents: return ""
    ticker_text = " ——— ".join(contents)
    return f'''
    <div id="ticker-bar" class="fixed bottom-0 left-0 w-full bg-blue-900 text-white py-4 z-[9999] overflow-hidden whitespace-nowrap border-t border-white/20 shadow-[0_-5px_20px_rgba(0,0,0,0.5)]">
        <div class="inline-block animate-marquee px-4">
            <span class="font-bold italic text-sm tracking-wide uppercase">{ticker_text} ——— {ticker_text}</span>
        </div>
    </div>'''

def get_steam_rss_data(mode, exclude_links):
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

    # 排序逻辑区分
    def sort_logic(entry):
        pub_time = time.mktime(entry.get('published_parsed', time.gmtime(0)))
        if mode == "official":
            return pub_time # 官方板块严格按时间排序
        
        # 精选板块逻辑：游戏节提权
        title = entry.title.lower()
        is_fest = any(k in title for k in ["游戏节", "festival", "fest", "roguelike"])
        if is_fest:
            return pub_time + 10**10
        return pub_time

    entries.sort(key=sort_logic, reverse=True)
    
    html_slides = ""
    for e in entries[:10]:
        content = e.get('summary', '') or e.get('description', '')
        img = re.search(r'<img [^>]*src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        pub_time = time.strftime("%m-%d %H:%M", e.published_parsed) if hasattr(e, 'published_parsed') else "RECENT"
        is_fest = any(k in e.title.lower() for k in ["游戏节", "festival", "fest", "roguelike"])
        
        # 精选板块的游戏节加高亮，官方板块保持简洁
        glow = "ring-4 ring-emerald-500 shadow-[0_0_30px_rgba(16,185,129,0.5)]" if (is_fest and mode == "featured") else ""
        
        html_slides += f'''
        <div class="swiper-slide cursor-pointer" onclick="window.open('{e.link}', '_blank')">
            <div class="relative h-[440px] w-full overflow-hidden rounded-[2.5rem] bg-[#1a1f26] border border-white/5 transition-all {glow}">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-80 transition-transform duration-1000 group-hover:scale-110">
                <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <div class="flex items-center gap-3 mb-3">
                        { "<span class='bg-emerald-500 text-white text-[9px] px-2 py-1 rounded italic font-black'>FESTIVAL</span>" if is_fest else "" }
                        <span class="font-mono text-[10px] text-blue-400 font-bold tracking-widest uppercase">{pub_time}</span>
                    </div>
                    <h2 class="text-2xl font-black text-white line-clamp-2 italic leading-tight uppercase">{e.title}</h2>
                </div>
            </div>
        </div>'''
    return html_slides

# ==========================================
# 静态 HTML 模板逻辑
# ==========================================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
    <meta charset="UTF-8">
    <title>STEAM INTEL CENTER</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: { extend: { animation: { 'marquee': 'marquee 40s linear infinite' }, keyframes: { marquee: { '0%': { transform: 'translateX(0%)' }, '100%': { transform: 'translateX(-50%)' } } } } }
        }
    </script>
    <style>
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .swiper { width: 100%; height: 540px; padding: 20px 0 100px 0; overflow: visible !important; }
        .swiper-slide { width: 580px; opacity: 0.15; transition: 0.8s; transform: scale(0.8); filter: blur(4px); }
        .swiper-slide-active { opacity: 1; transform: scale(1); filter: blur(0); z-index: 20; }
        /* 确保链接点击区域 */
        #ticker-bar a { position: relative; z-index: 10000; pointer-events: auto !important; }
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#0b0e14] text-slate-900 dark:text-slate-100 p-6 md:p-16 min-h-screen pb-40">
    <div class="max-w-[1500px] mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-center mb-16 gap-8">
            <div class="text-center md:text-left">
                <h1 class="text-7xl font-black italic tracking-tighter uppercase leading-none">Steam<span class="text-blue-600">Intel</span></h1>
                <p class="text-[11px] text-blue-600 font-mono mt-4 tracking-[0.5em] uppercase font-bold">Sector Monitoring // @@NOW_TIME@@</p>
            </div>
            <button onclick="document.documentElement.classList.toggle('dark')" class="px-8 py-4 bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-white/10 font-bold text-xs">MODE SWITCH</button>
        </header>

        <section class="mb-24">
            <div class="flex items-center gap-4 mb-10">
                <span class="px-4 py-1 bg-blue-600 text-white text-[10px] font-black rounded-full uppercase italic">Official Roadmap</span>
                <div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div>
            </div>
            @@TIMELINE@@
        </section>

        <main class="space-y-40">
            <section>
                <h2 class="text-5xl font-black italic uppercase mb-10 tracking-tighter italic">Featured <span class="text-blue-600">精选资讯</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">@@FEAT_HTML@@</div><div class="swiper-pagination"></div></div>
            </section>
            
            <section class="py-20 px-8 md:px-12 rounded-[4rem] border border-slate-200 dark:border-white/5 bg-slate-100/50 dark:bg-white/5">
                <h2 class="text-5xl font-black italic uppercase mb-10 tracking-tighter text-blue-600 italic">Official <span class="dark:text-white">官方公告</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">@@OFFI_HTML@@</div><div class="swiper-pagination"></div></div>
            </section>
        </main>
    </div>
    @@TICKER@@
    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.mySwiper').forEach(el => {
            new Swiper(el, {
                effect: "coverflow", centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: { delay: 6000, disableOnInteraction: false },
                coverflowEffect: { rotate: 0, stretch: 80, depth: 150, modifier: 1.2, slideShadows: false },
                pagination: { el: el.querySelector('.swiper-pagination'), clickable: true }
            });
        });
    </script>
</body>
</html>
'''

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    exclude = set()
    timeline = generate_timeline_html()
    ticker = generate_active_ticker()
    feat = get_steam_rss_data("featured", exclude)
    offi = get_steam_rss_data("official", exclude)

    output = HTML_TEMPLATE.replace("@@NOW_TIME@@", now_time)
    output = output.replace("@@TIMELINE@@", timeline)
    output = output.replace("@@FEAT_HTML@@", feat)
    output = output.replace("@@OFFI_HTML@@", offi)
    output = output.replace("@@TICKER@@", ticker)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    update_web()
