import feedparser
import datetime
import re
import time
from urllib.parse import quote

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
        is_active = int(e['start']) <= curr_int <= int(e['end'])
        color_class = {
            "major": "from-red-500 to-orange-600", 
            "nextfest": "from-emerald-400 to-cyan-500", 
            "spotlight": "from-purple-500 to-indigo-600"
        }.get(e['type'], "from-blue-500 to-indigo-500")
        
        status_text = "● IN PROGRESS" if is_active else "○ UPCOMING"
        glow_effect = "shadow-[0_0_20px_rgba(52,211,153,0.3)]" if is_active else ""
        
        html += f'''
        <div class="flex-shrink-0 w-64 p-5 rounded-2xl bg-white dark:bg-slate-900/50 backdrop-blur-xl border border-slate-200 dark:border-white/10 {glow_effect} transition-all duration-500">
            <div class="flex justify-between items-center mb-4">
                <span class="text-[9px] font-black {'text-emerald-500' if is_active else 'text-slate-400'} tracking-widest uppercase">{status_text}</span>
                <span class="text-[10px] font-mono text-slate-400">{e['start'][4:6]}/{e['start'][6:]}</span>
            </div>
            <div class="text-base font-bold text-slate-800 dark:text-white truncate mb-4">{e['name']}</div>
            <div class="h-2 w-full bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden p-[1px]">
                <div class="h-full bg-gradient-to-r {color_class} rounded-full {'animate-pulse' if is_active else 'opacity-40'}" style="width: {'100%' if is_active else '15%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def get_steam_rss_data(mode):
    # 核心优化：直接使用 Steam Collection 接口，这是更新最快的源
    if mode == "featured":
        urls = ["https://store.steampowered.com/feeds/news/collection/featured/?l=schinese"]
    else:
        # 这里整合了官方新闻集合、Steamworks 开发者新闻以及新品节专页
        urls = [
            "https://store.steampowered.com/feeds/news/collection/steam/?l=schinese", # 最核心的 Steam 官方新闻
            "https://store.steampowered.com/feeds/news/group/4145017/?l=schinese",     # Steamworks 动态
            "https://store.steampowered.com/feeds/news/app/3985950/?l=schinese",      # 2月新品节 AppID 动态
        ]

    entries = []
    seen_links = set()
    timestamp = int(time.time())

    for url in urls:
        try:
            feed = feedparser.parse(f"{url}&t={timestamp}")
            for e in feed.entries:
                if e.link not in seen_links:
                    # 降低过滤门槛，改为按权重排序，确保官方内容优先
                    entries.append(e)
                    seen_links.add(e.link)
        except: continue

    def get_pub_time(entry):
        if hasattr(entry, 'published_parsed'):
            return time.mktime(entry.published_parsed)
        return 0

    # 严格按时间戳降序排序，确保“最鲜”
    entries.sort(key=get_pub_time, reverse=True)

    slides_html = ""
    for e in entries[:10]:
        title = e.title
        link = e.link
        content = e.get('summary', '') or e.get('description', '')
        
        # 优化配图抓取：优先抓取大图
        img_match = re.search(r'<img [^>]*src="([^"]+)"', content)
        if img_match:
            img_url = img_match.group(1)
        else:
            # 备用图使用 2026 新品节的高清 Capsule
            img_url = "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/library_capsule_300x450.jpg"

        pub_time = time.strftime("%Y.%m.%d %H:%M", e.published_parsed) if hasattr(e, 'published_parsed') else ""
        
        # 官方标签逻辑优化
        is_official = any(k in title for k in ["公告", "新品节", "Steam", "Next Fest", "Update"])
        tag_html = '<span class="px-2 py-0.5 rounded bg-blue-600 text-white text-[9px] font-bold mr-2">OFFICIAL</span>' if is_official else ""

        slides_html += f'''
        <div class="swiper-slide group">
            <div class="relative h-[400px] w-full overflow-hidden rounded-[2rem] bg-slate-900 border border-white/5 transition-all duration-500 group-hover:border-blue-500/50 shadow-2xl" onclick="window.open('{link}', '_blank')">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105 opacity-60 group-hover:opacity-80">
                <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-900/40 to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full transform transition-transform duration-500 group-hover:-translate-y-2">
                    <div class="flex items-center gap-3 mb-3">
                        <span class="text-[10px] font-mono text-blue-400 bg-blue-400/10 px-2 py-1 rounded">DATA_SYNC // {pub_time}</span>
                    </div>
                    <h2 class="text-2xl font-black text-white leading-tight tracking-tight mb-2">
                        {tag_html}{title}
                    </h2>
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STEAM INTEL CENTER 2026</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
        body {{ font-family: 'Inter', sans-serif; scroll-behavior: smooth; }}
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .swiper {{ padding: 20px 50px 80px 50px !important; overflow: visible !important; }}
        .swiper-slide {{ transition: all 0.6s cubic-bezier(0.22, 1, 0.36, 1); filter: blur(4px) scale(0.9); opacity: 0.4; }}
        .swiper-slide-active {{ filter: blur(0) scale(1.05); opacity: 1; z-index: 50; }}
        .text-glow {{ text-shadow: 0 0 15px rgba(59, 130, 246, 0.5); }}
    </style>
</head>
<body class="bg-[#05070a] text-slate-200 min-h-screen">
    <div class="fixed top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_-20%,#1e293b,transparent)] pointer-events-none"></div>

    <div class="max-w-[1400px] mx-auto px-6 py-12 relative z-10">
        <header class="flex flex-col md:flex-row justify-between items-end mb-16 gap-6">
            <div class="border-l-4 border-blue-500 pl-6">
                <h1 class="text-6xl font-black italic tracking-tighter text-white uppercase leading-none">Steam<span class="text-blue-500">Intel</span></h1>
                <p class="text-[10px] text-blue-400 font-mono mt-3 tracking-[0.5em] uppercase opacity-70 italic">Industry Surveillance System // {now_time}</p>
            </div>
            <div class="flex gap-4">
                <div class="text-right">
                    <div class="text-[10px] font-bold text-slate-500 uppercase tracking-widest">System Status</div>
                    <div class="text-xs font-mono text-emerald-400 font-bold leading-none">● ONLINE_ENCRYPTED</div>
                </div>
            </div>
        </header>

        <section class="mb-20">
            <div class="flex items-center gap-4 mb-8">
                <h3 class="text-xs font-black text-blue-500 uppercase tracking-[0.3em]">Operational Roadmap</h3>
                <div class="h-[1px] flex-1 bg-gradient-to-r from-blue-500/50 to-transparent"></div>
            </div>
            {timeline}
        </section>

        <main class="space-y-24">
            <section>
                <div class="flex items-center justify-between mb-6 px-12">
                    <h2 class="text-3xl font-black italic uppercase tracking-tighter text-white">Featured <span class="text-blue-500">精选资讯</span></h2>
                    <div class="text-xs font-mono text-slate-500">TOP_SENSITIVITY_RANK_10</div>
                </div>
                <div class="swiper newsSwiper"><div class="swiper-wrapper">{feat}</div><div class="swiper-pagination"></div></div>
            </section>
            
            <section>
                <div class="flex items-center justify-between mb-6 px-12">
                    <h2 class="text-3xl font-black italic uppercase tracking-tighter text-blue-500">Official <span class="text-white font-black">官方公告</span></h2>
                    <div class="text-xs font-mono text-slate-500">VALVE_DIRECT_FEED</div>
                </div>
                <div class="swiper newsSwiper"><div class="swiper-wrapper">{offi}</div><div class="swiper-pagination"></div></div>
            </section>
        </main>

        <footer class="mt-32 pt-8 border-t border-white/5 text-center">
            <p class="text-[10px] font-mono text-slate-600 uppercase tracking-widest">Designed for Steam Activity Node // 2026</p>
        </footer>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.newsSwiper').forEach(el => {{
            new Swiper(el, {{
                effect: "coverflow",
                centeredSlides: true,
                slidesPerView: "auto",
                initialSlide: 1,
                grabCursor: true,
                loop: true,
                speed: 800,
                autoplay: {{ delay: 4000, disableOnInteraction: false }},
                coverflowEffect: {{ rotate: 5, stretch: 0, depth: 100, modifier: 2, slideShadows: false }},
                pagination: {{ el: el.querySelector('.swiper-pagination'), clickable: true }}
            }});
        }});
    </script>
</body>
</html>'''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(template)
    print(f"Update Success: {now_time}")

if __name__ == "__main__":
    update_web()
