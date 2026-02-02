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
        <div class="flex-shrink-0 w-60 p-5 rounded-2xl bg-white/80 dark:bg-slate-900/50 backdrop-blur-md border border-slate-200 dark:border-white/10 transition-all duration-500 shadow-sm">
            <div class="flex justify-between items-center mb-3">
                <span class="text-[9px] font-black tracking-tighter {'text-emerald-500 animate-pulse' if active else 'text-slate-400'} uppercase">{'● LIVE NOW' if active else '○ SCHEDULED'}</span>
                <span class="text-[10px] font-mono text-slate-400">{e['start'][4:6]}-{e['start'][6:]}</span>
            </div>
            <div class="text-sm font-bold text-slate-800 dark:text-slate-100 truncate mb-3">{e['name']}</div>
            <div class="h-1.5 w-full bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                <div class="h-full bg-{color} {'shadow-[0_0_8px] shadow-'+color if active else 'opacity-20'}" style="width: {'100%' if active else '20%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def get_steam_rss_data(mode):
    # 使用多个冗余源确保“最新”
    source_map = {
        "featured": [
            "https://store.steampowered.com/feeds/news/collection/featured/?l=schinese"
        ],
        "official": [
            "https://store.steampowered.com/feeds/news/collection/steam/?l=schinese",
            "https://store.steampowered.com/feeds/news/group/39049601/?l=schinese", # 官方博客
            "https://store.steampowered.com/feeds/news/group/4145017/?l=schinese"  # Steamworks
        ]
    }
    
    urls = source_map.get(mode, [])
    entries = []
    seen_links = set()
    
    # 随机化参数击穿缓存
    timestamp = int(time.time())
    nonce = random.randint(1000, 9999)

    for url in urls:
        try:
            # 模拟浏览器请求头在部分 feedparser 版本中需配合 urllib 使用，这里直接在 URL 后加参数最有效
            feed = feedparser.parse(f"{url}&nocache={timestamp}&v={nonce}")
            for e in feed.entries:
                if e.link not in seen_links:
                    entries.append(e)
                    seen_links.add(e.link)
        except: continue

    # 排序逻辑：将具有 published_parsed 的项按时间戳倒序排列
    entries.sort(key=lambda x: x.get('published_parsed', time.gmtime(0)), reverse=True)

    slides_html = ""
    for e in entries[:10]:
        title = e.title
        link = e.link
        content = e.get('summary', '') or e.get('description', '')
        
        # 配图提取
        img = re.search(r'<img [^>]*src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        
        # 转换发布时间
        pub_time = time.strftime("%m/%d %H:%M", e.published_parsed) if hasattr(e, 'published_parsed') else "RECENT"
        
        slides_html += f'''
        <div class="swiper-slide group cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-[420px] w-full overflow-hidden rounded-[2rem] bg-slate-200 dark:bg-slate-800 border border-slate-300/50 dark:border-white/5 transition-all duration-500 group-hover:border-blue-500/50">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-80 dark:opacity-50 transition-transform duration-700 group-hover:scale-105">
                <div class="absolute inset-0 bg-gradient-to-t from-slate-100 dark:from-slate-950 via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="px-2 py-0.5 rounded-md bg-blue-500 text-white text-[9px] font-bold tracking-widest uppercase">Steam Feed</span>
                        <span class="text-[10px] font-mono text-slate-500 dark:text-blue-400 font-bold">{pub_time}</span>
                    </div>
                    <h2 class="text-2xl font-black text-slate-900 dark:text-white line-clamp-2 leading-tight tracking-tighter">{title}</h2>
                </div>
            </div>
        </div>'''
    return slides_html

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    timeline = generate_timeline_html()
    feat_slides = get_steam_rss_data("featured")
    offi_slides = get_steam_rss_data("official")

    template = f'''<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
    <meta charset="UTF-8">
    <title>STEAM INTEL NODE // 2026</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{ darkMode: 'class' }}
        function toggleTheme() {{
            const html = document.documentElement;
            const isDark = html.classList.toggle('dark');
            localStorage.setItem('steam_theme', isDark ? 'dark' : 'light');
        }}
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
        body {{ font-family: 'Space Grotesk', sans-serif; transition: background-color 0.5s ease; }}
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .swiper {{ width: 100%; padding: 20px 0 80px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 500px; opacity: 0.15; filter: blur(10px) scale(0.85); transition: 0.8s cubic-bezier(0.2, 1, 0.3, 1); }}
        .swiper-slide-active {{ opacity: 1; filter: blur(0) scale(1); z-index: 20; }}
        .swiper-pagination-bullet {{ background: #3b82f6 !important; }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 min-h-screen p-6 md:p-16">
    <div class="max-w-[1400px] mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-start md:items-center mb-16">
            <div class="border-l-4 border-blue-600 pl-6">
                <h1 class="text-5xl font-black tracking-tighter uppercase italic text-slate-900 dark:text-white">Steam<span class="text-blue-600">Intel</span></h1>
                <p class="text-[10px] font-mono text-blue-500 mt-2 tracking-[0.4em] uppercase font-bold">Node Connected // {now_time}</p>
            </div>
            <button onclick="toggleTheme()" class="mt-6 md:mt-0 group flex items-center gap-3 px-6 py-3 bg-white dark:bg-slate-900 rounded-full shadow-lg border border-slate-200 dark:border-white/5 transition-all hover:scale-105 active:scale-95">
                <div class="w-2 h-2 rounded-full bg-blue-600 animate-pulse"></div>
                <span class="text-xs font-black tracking-widest uppercase dark:hidden">Switch to Dark</span>
                <span class="text-xs font-black tracking-widest uppercase hidden dark:inline text-blue-400">Switch to Light</span>
            </button>
        </header>

        <section class="mb-20">
            <div class="flex items-center gap-4 mb-8">
                <h2 class="text-xs font-black text-blue-600 uppercase tracking-widest">2026 Roadmap</h2>
                <div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div>
            </div>
            {timeline}
        </section>

        <main class="space-y-24">
            <section>
                <h3 class="text-3xl font-black italic uppercase mb-8 tracking-tighter">Featured <span class="text-blue-600">精选资讯</span></h3>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{feat_slides}</div><div class="swiper-pagination"></div></div>
            </section>
            
            <section>
                <h3 class="text-3xl font-black italic uppercase mb-8 tracking-tighter text-blue-600">Official <span class="text-slate-900 dark:text-white">官方公告</span></h3>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{offi_slides}</div><div class="swiper-pagination"></div></div>
            </section>
        </main>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        // 初始化主题
        if (localStorage.getItem('steam_theme') === 'light') document.documentElement.classList.remove('dark');
        
        // 初始化所有轮播图
        document.querySelectorAll('.mySwiper').forEach(el => {{
            new Swiper(el, {{
                effect: "coverflow",
                centeredSlides: true,
                slidesPerView: "auto",
                loop: true,
                speed: 1000,
                autoplay: {{ delay: 5000, disableOnInteraction: false }},
                coverflowEffect: {{ rotate: 0, stretch: 80, depth: 150, modifier: 1, slideShadows: false }},
                pagination: {{ el: el.querySelector('.swiper-pagination'), clickable: true }}
            }});
        }});
    </script>
</body>
</html>'''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(template)

if __name__ == "__main__":
    update_web()
    print("Web Page Updated with Latest Data.")
