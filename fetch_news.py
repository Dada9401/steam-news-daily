import feedparser
import datetime
import re
import time

# --- 2026 Steam 官方活动【校准版】 ---
STEAM_EVENTS_2026 = [
    {"name": "即时战略 (RTS) 游戏节", "start": "20260119", "end": "20260126", "type": "fest"},
    {"name": "自走棋与牌组构建节", "start": "20260126", "end": "20260202", "type": "fest"},
    {"name": "Steam 新品节 (2月版)", "start": "20260202", "end": "20260209", "type": "nextfest"},
    {"name": "农历新年大促 (Spring Festival)", "start": "20260212", "end": "20260219", "type": "major"},
    {"name": "恐龙游戏节", "start": "20260223", "end": "20260302", "type": "fest"},
    {"name": "Steam 春季大促", "start": "20260319", "end": "20260326", "type": "major"},
    {"name": "FPS 游戏节", "start": "20260413", "end": "20260420", "type": "fest"},
]

def generate_timeline_html():
    now = datetime.datetime.now()
    current_date_int = int(now.strftime("%Y%m%d"))
    
    html = '<div class="flex flex-nowrap gap-4 overflow-x-auto pb-4 mb-8 no-scrollbar">'
    
    # 获取距离现在最近且未结束的活动
    upcoming_events = [e for e in STEAM_EVENTS_2026 if int(e['end']) >= current_date_int][:5]
    
    for event in upcoming_events:
        is_active = int(event['start']) <= current_date_int <= int(event['end'])
        
        # 颜色逻辑
        theme_color = "blue-500"
        if event['type'] == 'major': theme_color = "red-500"
        if event['type'] == 'nextfest': theme_color = "yellow-500"
        if is_active: theme_color = "green-400"

        date_str = f"{event['start'][4:6]}/{event['start'][6:]} - {event['end'][4:6]}/{event['end'][6:]}"
        status_label = "● ACTIVE NOW" if is_active else "○ STANDBY"
        
        html += f'''
        <div class="flex-shrink-0 w-64 p-4 rounded-xl bg-slate-900/60 border-t-2 border-{theme_color} backdrop-blur-md">
            <div class="flex justify-between items-center mb-1">
                <span class="text-[9px] font-black text-{theme_color} tracking-widest">{status_label}</span>
                <span class="text-[9px] font-mono text-gray-500">{date_str}</span>
            </div>
            <div class="text-sm font-bold text-white truncate">{event['name']}</div>
            <div class="w-full bg-gray-800 h-[2px] mt-3">
                <div class="h-full bg-{theme_color} {'animate-pulse' if is_active else ''}" style="width: {'100%' if is_active else '15%'}"></div>
            </div>
        </div>'''
    
    html += '</div>'
    return html

# ... [get_steam_rss_data 函数保持不变] ...

def get_steam_rss_data(url_type):
    rss_url = f"https://store.steampowered.com/feeds/news/collection/{url_type}/?l=schinese"
    slides_html = ""
    try:
        feed = feedparser.parse(rss_url)
        if not feed.entries and url_type != "all": return get_steam_rss_data("all")
        for entry in feed.entries[:8]:
            title, link = entry.title, entry.link
            content = entry.get('summary', '') or entry.get('description', '')
            img_match = re.search(r'<img [^>]*src="([^"]+)"', content)
            img_url = img_match.group(1) if img_match else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/594650/capsule_617x353.jpg"
            slides_html += f'''
            <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
                <div class="relative h-full w-full overflow-hidden rounded-3xl bg-slate-900 border border-white/10 group">
                    <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-60 transition-all duration-700 group-hover:scale-110">
                    <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
                    <div class="absolute bottom-0 p-6 w-full text-left">
                        <h2 class="text-xl font-bold text-white line-clamp-2">{title}</h2>
                    </div>
                </div>
            </div>'''
        return slides_html
    except: return ""

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    timeline_html = generate_timeline_html()
    
    try:
        industry_feed = feedparser.parse("https://www.gamespot.com/feeds/news/")
        ticker_text = " • ".join([f"【{e.title}】" for e in industry_feed.entries[:12]]) if industry_feed.entries else "情报中心正常运转中..."
    except: ticker_text = "数据链路连接稳定..."

    featured_html = get_steam_rss_data("featured")
    official_html = get_steam_rss_data("steam")

    template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>STEAM 2026 MONITOR</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #020408; color: white; font-family: system-ui; overflow-x: hidden; padding-bottom: 120px; }
        .swiper { width: 100%; height: 380px; padding: 10px 0 60px 0; overflow: visible !important; }
        .swiper-slide { width: 400px; opacity: 0.3; transition: 0.5s; transform: scale(0.8); }
        .swiper-slide-active { opacity: 1; transform: scale(1); }
        .swiper-pagination-bullet { background: #3b82f6; opacity: 0.3; transition: all 0.4s; }
        .swiper-pagination-bullet-active { background: #60a5fa !important; opacity: 1; width: 30px; border-radius: 6px; box-shadow: 0 0 15px #3b82f6; }
        .ticker-wrap { position: fixed; bottom: 0; left: 0; width: 100%; background: #2563eb; color: white; padding: 15px 0; z-index: 100; }
        .ticker { display: inline-block; white-space: nowrap; animation: scroll 80s linear infinite; font-weight: bold; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        @keyframes scroll { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
        <header class="flex justify-between items-end border-b border-blue-900/40 pb-6 mb-8">
            <div>
                <h1 class="text-5xl font-black italic text-blue-500 tracking-tighter uppercase leading-none">News Console</h1>
                <p class="text-[10px] text-blue-400 font-mono mt-2 tracking-[0.4em]">STABLE INTELLIGENCE SYNC // {now_time}</p>
            </div>
        </header>

        <div class="mb-4 text-[9px] font-bold text-gray-500 uppercase tracking-[0.3em] flex items-center gap-2">
            <span class="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse"></span> Mission Timeline / 节点
        </div>
        {timeline_html}

        <main>
            <section class="mb-8">
                <h2 class="text-xl font-black mb-2 flex items-center gap-4 text-white uppercase"><span class="bg-blue-600 w-2 h-6"></span> Featured 精选资讯</h2>
                <div class="swiper mySwiper">
                    <div class="swiper-wrapper">{featured_html}</div>
                    <div class="swiper-pagination"></div>
                </div>
            </section>
            <section>
                <h2 class="text-xl font-black mb-2 flex items-center gap-4 text-blue-400 uppercase"><span class="bg-blue-400 w-2 h-6"></span> Official 官方公告</h2>
                <div class="swiper mySwiper">
                    <div class="swiper-wrapper">{official_html}</div>
                    <div class="swiper-pagination"></div>
                </div>
            </section>
        </main>
    </div>
    <div class="ticker-wrap"><div class="ticker">GLOBAL INTEL: {ticker_text}</div></div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.mySwiper').forEach(el => {
            const swiper = new Swiper(el, {
                effect: "coverflow", grabCursor: true, centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: { delay: 4000, disableOnInteraction: false },
                coverflowEffect: { rotate: 0, stretch: 0, depth: 150, modifier: 2, slideShadows: false },
                pagination: { el: el.querySelector('.swiper-pagination'), clickable: true }
            });
            el.addEventListener('mouseover', function(e) {
                if (e.target.classList.contains('swiper-pagination-bullet')) {
                    const bullets = Array.from(el.querySelectorAll('.swiper-pagination-bullet'));
                    const index = bullets.indexOf(e.target);
                    if (index !== -1) swiper.slideToLoop(index);
                }
            });
        });
    </script>
</body>
</html>'''

    full_html = template.replace("{now_time}", now_time)\
                        .replace("{featured_html}", featured_html)\
                        .replace("{official_html}", official_html)\
                        .replace("{ticker_text}", ticker_text)\
                        .replace("{timeline_html}", timeline_html)

    with open("index.html", "w", encoding="utf-8") as f: f.write(full_html)

if __name__ == "__main__":
    update_web()
