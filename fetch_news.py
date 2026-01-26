import feedparser
import datetime
import re

# --- 2026 Steam 官方全年度活动数据库（100% 同步官方路线图） ---
STEAM_EVENTS_2026 = [
    {"name": "棋盘游戏节", "start": "20260126", "end": "20260202", "type": "fest"},
    {"name": "打字节 (焦点游戏节)", "start": "20260205", "end": "20260209", "type": "spotlight"},
    {"name": "玩家对战 (PvP) 节", "start": "20260209", "end": "20260216", "type": "fest"},
    {"name": "马儿节 (焦点游戏节)", "start": "20260219", "end": "20260223", "type": "spotlight"},
    {"name": "Steam 新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest"},
    {"name": "塔防节", "start": "20260309", "end": "20260316", "type": "fest"},
    {"name": "Steam 春季特卖 (年度重磅)", "start": "20260319", "end": "20260326", "type": "major"},
    {"name": "房屋与家园节", "start": "20260330", "end": "20260407", "type": "fest"},
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
        color = {"major": "red-500", "nextfest": "yellow-400", "spotlight": "purple-400"}.get(e['type'], "blue-400")
        if active: color = "green-400"
        html += f'''
        <div class="flex-shrink-0 w-60 p-4 rounded-2xl bg-slate-900/60 border border-white/5 backdrop-blur-md">
            <div class="flex justify-between items-center mb-1">
                <span class="text-[9px] font-black text-{color} tracking-widest">{'● LIVE' if active else '○ READY'}</span>
                <span class="text-[9px] font-mono text-gray-500">{e['start'][4:6]}/{e['start'][6:]}</span>
            </div>
            <div class="text-sm font-bold text-white truncate mb-2">{e['name']}</div>
            <div class="h-1 w-full bg-white/10 rounded-full overflow-hidden">
                <div class="h-full bg-{color} {'animate-pulse' if active else 'opacity-30'}" style="width: {'100%' if active else '20%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def get_steam_rss_data(url_type):
    # 建立源矩阵：商店精选、官方组博客、以及多语种接口，防止单一源漏掉重大预告
    sources = [
        f"https://store.steampowered.com/feeds/news/collection/{url_type}/?l=schinese",
        "https://steamcommunity.com/groups/steam/rss/?l=schinese"
    ]
    
    # 针对 Featured 板块，额外增加一个备用频道，专门捕捉“即将推出”的博文
    if url_type == "featured":
        sources.append("https://store.steampowered.com/feeds/news/collection/all/?l=schinese")

    all_entries = []
    seen_links = set()

    for url in sources:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if entry.link not in seen_links:
                    all_entries.append(entry)
                    seen_links.add(entry.link)
        except: continue

    # --- 核心逻辑：权重算法 ---
    # 定义高价值关键词，只要包含这些，无论何时发布的都会被赋予极高权重
    prime_keywords = ["即将推出", "新品节", "Next Fest", "路线图", "Roadmap", "新鲜出炉", "特卖", "公告"]
    
    def get_priority(entry):
        score = 0
        # 关键词匹配
        if any(kw in entry.title for kw in prime_keywords): score += 100
        # 如果包含日期（如 2026），通常是年度路线图，权重极高
        if "2026" in entry.title: score += 50
        return score

    # 根据权重排序，分数相同的按时间排
    all_entries.sort(key=lambda x: (get_priority(x), x.get('published_parsed', 0)), reverse=True)

    slides_html = ""
    for entry in all_entries[:12]:
        title, link = entry.title, entry.link
        content = entry.get('summary', '') or entry.get('description', '')
        img_match = re.search(r'<img [^>]*src="([^"]+)"', content)
        img_url = img_match.group(1) if img_match else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/594650/capsule_617x353.jpg"
        
        # 视觉标签判定
        tag_html = ""
        if any(kw in title for kw in ["新品节", "Next Fest"]):
            tag_html = '<span class="bg-yellow-400 text-black text-[10px] px-2 py-1 rounded font-black mr-2">UPCOMING EVENT</span>'
        elif any(kw in title for kw in ["特卖", "Sale"]):
            tag_html = '<span class="bg-red-500 text-white text-[10px] px-2 py-1 rounded font-black mr-2">MAJOR SALE</span>'
        
        slides_html += f'''
        <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-full w-full overflow-hidden rounded-[2rem] bg-slate-900 border border-white/10 group shadow-2xl">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-60 transition-all duration-700 group-hover:scale-110">
                <div class="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <h2 class="text-2xl font-bold text-white line-clamp-2 leading-tight tracking-tight">{tag_html}{title}</h2>
                </div>
            </div>
        </div>'''
    return slides_html

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    timeline_html = generate_timeline_html()
    featured_html = get_steam_rss_data("featured")
    official_html = get_steam_rss_data("steam")

    template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>STEAM MISSION CONTROL</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #020408; color: white; font-family: system-ui; overflow-x: hidden; padding-bottom: 120px; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .swiper { width: 100%; height: 450px; padding: 20px 0 80px 0; overflow: visible !important; }
        .swiper-slide { width: 520px; opacity: 0.1; transition: 0.6s; transform: scale(0.8); filter: blur(4px); }
        .swiper-slide-active { opacity: 1; transform: scale(1); filter: blur(0); z-index: 10; }
        .swiper-pagination-bullet { background: #3b82f6; width: 10px; height: 10px; transition: 0.4s; }
        .swiper-pagination-bullet-active { background: #60a5fa !important; width: 40px; border-radius: 5px; }
        .ticker-wrap { position: fixed; bottom: 0; left: 0; width: 100%; background: #1d4ed8; color: white; padding: 15px 0; z-index: 100; font-size: 13px; font-weight: 800; border-top: 1px solid rgba(255,255,255,0.1); }
        .ticker { display: inline-block; white-space: nowrap; animation: scroll 80s linear infinite; }
        @keyframes scroll { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
</head>
<body class="p-8 md:p-16 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-[#020408] to-[#020408]">
    <div class="max-w-[1600px] mx-auto">
        <header class="flex justify-between items-end mb-16 border-l-8 border-blue-600 pl-8">
            <div>
                <h1 class="text-7xl font-black italic tracking-tighter uppercase leading-none">News Intel</h1>
                <p class="text-[12px] text-blue-500 font-mono mt-4 tracking-[0.6em] uppercase">Deep Scan Active // Syncing Upcoming Events // {now_time}</p>
            </div>
        </header>

        <section class="mb-16">
            <div class="text-[11px] font-black text-gray-500 uppercase tracking-[0.4em] mb-8 flex items-center gap-3">
                <span class="w-3 h-3 bg-blue-600 rounded-full animate-ping"></span> Roadmap Pipeline / 活动时间轴
            </div>
            {timeline_html}
        </section>

        <main class="space-y-24">
            <section>
                <div class="flex items-center gap-6 mb-8">
                    <h2 class="text-3xl font-black uppercase italic tracking-tighter">Featured & Upcoming / 精选与预告</h2>
                    <div class="h-[1px] flex-1 bg-white/10"></div>
                </div>
                <div class="swiper mySwiper">
                    <div class="swiper-wrapper">{featured_html}</div>
                    <div class="swiper-pagination"></div>
                </div>
            </section>

            <section>
                <div class="flex items-center gap-6 mb-8 text-blue-500">
                    <h2 class="text-3xl font-black uppercase italic tracking-tighter">Official Logs / 官方博文</h2>
                    <div class="h-[1px] flex-1 bg-blue-500/20"></div>
                </div>
                <div class="swiper mySwiper">
                    <div class="swiper-wrapper">{official_html}</div>
                    <div class="swiper-pagination"></div>
                </div>
            </section>
        </main>
    </div>

    <div class="ticker-wrap"><div class="ticker text-uppercase">Scanning official upcoming events... Synchronizing Next Fest 2026 schedules... Real-time news hub operational... </div></div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.mySwiper').forEach(el => {
            new Swiper(el, {
                effect: "coverflow", centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: { delay: 4000, disableOnInteraction: false },
                coverflowEffect: { rotate: 0, stretch: 100, depth: 150, modifier: 1, slideShadows: false },
                pagination: { el: el.querySelector('.swiper-pagination'), clickable: true }
            });
        });
    </script>
</body>
</html>'''

    full_html = template.replace("{now_time}", now_time)\
                        .replace("{featured_html}", featured_html)\
                        .replace("{official_html}", official_html)\
                        .replace("{timeline_html}", timeline_html)

    with open("index.html", "w", encoding="utf-8") as f: f.write(full_html)

if __name__ == "__main__":
    update_web()
