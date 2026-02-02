import feedparser
import datetime
import re
import time
import random

# ==========================================
# 核心配置：2026 Steam 官方活动数据库
# ==========================================
STEAM_EVENTS_2026 = [
    {"name": "棋盘游戏节", "start": "20260126", "end": "20260202", "type": "fest", "url": "https://store.steampowered.com/category/tabletop"},
    {"name": "打字节 (焦点节)", "start": "20260205", "end": "20260209", "type": "spotlight", "url": "https://store.steampowered.com/category/typing"},
    {"name": "PvP 游戏节", "start": "20260209", "end": "20260216", "type": "fest", "url": "https://store.steampowered.com/category/pvp"},
    {"name": "Steam 新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest", "url": "https://store.steampowered.com/sale/nextfest"},
    {"name": "Steam 春季特卖", "start": "20260319", "end": "20260326", "type": "major", "url": "https://store.steampowered.com/sale/springsale"},
    {"name": "Steam 新品节 (6月版)", "start": "20260615", "end": "20260622", "type": "nextfest", "url": "https://store.steampowered.com/sale/nextfest"},
    {"name": "Steam 夏季特卖", "start": "20260625", "end": "20260709", "type": "major", "url": "https://store.steampowered.com/sale/summersale"},
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

def generate_active_ticker():
    """生成底部滚动提醒条"""
    now = datetime.datetime.now()
    curr_int = int(now.strftime("%Y%m%d"))
    active_events = [e for e in STEAM_EVENTS_2026 if int(e['start']) <= curr_int <= int(e['end'])]
    
    if not active_events:
        return ""

    ticker_content = " ——— ".join([f"🔥 正在进行: {e['name']} | <a href='{e.get('url','#')}' target='_blank' class='underline decoration-wavy'>点击进入会场</a>" for e in active_events])
    # 双重内容实现无缝滚动
    return f'''
    <div class="fixed bottom-0 left-0 w-full bg-blue-600 text-white py-2 z-[100] overflow-hidden whitespace-nowrap border-t border-white/20 shadow-2xl">
        <div class="inline-block animate-marquee px-4">
            <span class="font-black italic text-sm tracking-widest uppercase">{ticker_content} ——— {ticker_content}</span>
        </div>
    </div>
    '''

def get_steam_rss_data(mode, exclude_links=None):
    if exclude_links is None: exclude_links = set()
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
            feed = feedparser.parse(f"{url}&refresh={timestamp}&v={random.random()}")
            for e in feed.entries:
                if e.link not in seen_links and e.link not in exclude_links:
                    entries.append(e)
                    seen_links.add(e.link)
        except: continue

    def get_sort_score(entry):
        pub_time = time.mktime(entry.get('published_parsed', time.gmtime(0)))
        title = entry.title.lower()
        is_fest = any(k in title for k in ["游戏节", "festival", "fest", "新品节"])
        return (10000000000 if is_fest and mode == "featured" else 0) + pub_time

    entries.sort(key=get_sort_score, reverse=True)

    slides_html = ""
    for e in entries[:10]:
        title, link = e.title, e.link
        exclude_links.add(link) # 记录已分发的链接
        content = e.get('summary', '') or e.get('description', '')
        img = re.search(r'<img [^>]*src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        pub_time = time.strftime("%m-%d %H:%M", e.published_parsed) if hasattr(e, 'published_parsed') else "RECENT"
        
        is_fest = any(k in title.lower() for k in ["游戏节", "festival", "fest"])
        fest_tag = '<span class="bg-emerald-500 text-white text-[9px] px-2 py-0.5 rounded mr-2 animate-pulse">FESTIVAL</span>' if is_fest else ""
        
        slides_html += f'''
        <div class="swiper-slide group cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-[400px] w-full overflow-hidden rounded-[2rem] bg-white dark:bg-[#1a1f26] border { "border-emerald-500/50 shadow-[0_0_30px_rgba(16,185,129,0.2)]" if is_fest else "border-slate-200 dark:border-white/5" } transition-all duration-500">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-95 dark:opacity-60 transition-transform duration-1000 group-hover:scale-110">
                <div class="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <div class="flex items-center gap-2 mb-3">
                        {fest_tag}
                        <span class="text-[10px] font-mono text-blue-400 font-bold uppercase tracking-widest">{pub_time}</span>
                    </div>
                    <h2 class="text-xl font-black text-white line-clamp-2 leading-tight tracking-tight">{title}</h2>
                </div>
            </div>
        </div>'''
    return slides_html, exclude_links

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    timeline = generate_timeline_html()
    ticker = generate_active_ticker()
    
    # 逻辑去重
    feat_html, used_links = get_steam_rss_data("featured")
    offi_html, _ = get_steam_rss_data("official", exclude_links=used_links)

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
            theme: {{
                extend: {{
                    animation: {{ 'marquee': 'marquee 25s linear infinite' }},
                    keyframes: {{ marquee: {{ '0%': {{ transform: 'translateX(0%)' }}, '100%': {{ transform: 'translateX(-50%)' }} }} }}
                }}
            }}
        }}
    </script>
    <style>
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .swiper {{ width: 100%; height: 480px; padding: 20px 0 60px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 500px; opacity: 0.3; transition: 0.8s cubic-bezier(0.2, 1, 0.3, 1); transform: scale(0.8); filter: blur(4px); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); filter: blur(0); z-index: 20; }}
        .section-gradient {{ background: linear-gradient(180deg, rgba(30,41,59,0) 0%, rgba(30,41,59,0.3) 100%); }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#0b0e14] text-slate-900 dark:text-slate-100 p-6 md:p-16 min-h-screen mb-20">
    <div class="max-w-[1500px] mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-center mb-16">
            <div class="text-center md:text-left">
                <h1 class="text-6xl font-black italic tracking-tighter uppercase text-slate-900 dark:text-white">Steam<span class="text-blue-600">Intel</span></h1>
                <p class="text-[10px] text-blue-600 dark:text-blue-500 font-mono mt-2 tracking-[0.5em] uppercase font-bold">Industry Pulse Monitoring // {now_time}</p>
            </div>
        </header>

        <section class="mb-20">
            <div class="flex items-center gap-4 mb-8">
                <span class="px-4 py-1 bg-blue-600 text-white text-[10px] font-black rounded-full uppercase">Roadmap</span>
                <div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div>
            </div>
            {timeline}
        </section>

        <section class="mb-32 relative">
            <div class="absolute -left-10 top-0 bottom-0 w-1 bg-blue-600 hidden md:block"></div>
            <h2 class="text-5xl font-black italic uppercase mb-4 tracking-tighter">Featured <span class="text-blue-600">精选资讯</span></h2>
            <p class="text-slate-400 text-xs mb-10 font-mono">// CURATED SELECTIONS FROM STEAM STORE</p>
            <div class="swiper featSwiper"><div class="swiper-wrapper">{feat_html}</div><div class="swiper-pagination"></div></div>
        </section>

        <section class="py-16 px-8 rounded-[3rem] bg-slate-100/50 dark:bg-slate-900/20 border border-slate-200 dark:border-white/5 section-gradient">
            <h2 class="text-5xl font-black italic uppercase mb-4 tracking-tighter text-blue-600">Official <span class="dark:text-white text-slate-900">官方公告</span></h2>
            <p class="text-slate-400 text-xs mb-10 font-mono">// STEAMWORKS & SYSTEM UPDATES</p>
            <div class="swiper offiSwiper"><div class="swiper-wrapper">{offi_html}</div><div class="swiper-pagination"></div></div>
        </section>
    </div>

    {ticker}

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        const swiperOptions = {{
            effect: "coverflow", 
            centeredSlides: true, 
            slidesPerView: "auto", 
            loop: true,
            autoplay: {{ delay: 5000, disableOnInteraction: false }},
            coverflowEffect: {{ rotate: 0, stretch: 80, depth: 120, modifier: 1.5, slideShadows: false }},
            pagination: {{ clickable: true }}
        }};
        
        new Swiper('.featSwiper', {{ ...swiperOptions, pagination: {{ el: '.featSwiper .swiper-pagination' }} }});
        new Swiper('.offiSwiper', {{ ...swiperOptions, autoplay: {{ delay: 7000 }}, pagination: {{ el: '.offiSwiper .swiper-pagination' }} }});
    </script>
</body>
</html>'''
    with open("index.html", "w", encoding="utf-8") as f: f.write(template)

if __name__ == "__main__":
    update_web()
    print("Optimization Complete: Dual-section separation & Ticker active.")
