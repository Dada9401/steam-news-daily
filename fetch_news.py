import feedparser
import datetime
import re
import time

def get_steam_rss_data(url_type):
    rss_url = f"https://store.steampowered.com/feeds/news/collection/{url_type}/?l=schinese"
    slides_html = ""
    try:
        feed = feedparser.parse(rss_url)
        # 如果 steam 频道没内容，尝试抓取全站内容
        if not feed.entries and url_type != "all":
            return get_steam_rss_data("all")

        for entry in feed.entries[:10]:
            title = entry.title
            link = entry.link
            content = entry.get('summary', '') or entry.get('description', '')
            img_match = re.search(r'<img [^>]*src="([^"]+)"', content)
            img_url = img_match.group(1) if img_match else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/594650/capsule_617x353.jpg"
            
            slides_html += f'''
            <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
                <div class="relative h-full w-full overflow-hidden rounded-3xl bg-slate-900 border border-white/10 group">
                    <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-60 transition-transform duration-700 group-hover:scale-110">
                    <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
                    <div class="absolute bottom-0 p-6 w-full">
                        <h2 class="text-xl font-bold text-white line-clamp-2">{title}</h2>
                    </div>
                </div>
            </div>'''
        return slides_html
    except:
        return ""

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    ticker_text = "行业实时情报同步中..."
    try:
        industry_feed = feedparser.parse("https://www.gamespot.com/feeds/news/")
        if industry_feed.entries:
            ticker_text = " • ".join([f"【{e.title}】" for e in industry_feed.entries[:12]])
    except: pass

    featured_html = get_steam_rss_data("featured")
    official_html = get_steam_rss_data("steam")

    # 这里的 HTML 模板增加了分页器结构和样式
    full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>STEAM 2026 MONITOR</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: #020408; color: white; font-family: system-ui; overflow-x: hidden; padding-bottom: 120px; }}
        /* 容器样式 */
        .swiper {{ width: 100%; height: 380px; padding: 20px 0 50px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 420px; opacity: 0.3; transition: 0.5s; transform: scale(0.8); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); }}
        
        /* 自定义小圆点样式 */
        .swiper-pagination-bullets.swiper-pagination-horizontal {{ bottom: 10px; }}
        .swiper-pagination-bullet {{ 
            background: #1e3a8a; 
            opacity: 0.5; 
            width: 10px; 
            height: 10px; 
            transition: all 0.3s;
        }}
        .swiper-pagination-bullet-active {{ 
            background: #3b82f6 !important; 
            opacity: 1; 
            width: 30px; 
            border-radius: 5px; 
            box-shadow: 0 0 10px #3b82f6;
        }}

        .ticker-wrap {{ position: fixed; bottom: 0; left: 0; width: 100%; background: #2563eb; color: white; padding: 15px 0; z-index: 100; }}
        .ticker {{ display: inline-block; white-space: nowrap; animation: scroll 80s linear infinite; font-weight: bold; }}
        @keyframes scroll {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    </style>
</head>
<body class="p-6 md:p-12">
    <div class="max-w-7xl mx-auto">
        <header class="flex justify-between items-end border-b border-blue-900/40 pb-6 mb-12">
            <div>
                <h1 class="text-5xl font-black italic text-blue-500 tracking-tighter">NEWS MONITOR</h1>
                <p class="text-xs text-blue-400 font-mono mt-2 tracking-[0.3em]">INTERACTIVE 3D STACK // SYNC: {now_time}</p>
            </div>
        </header>

        <section class="mb-20">
            <h2 class="text-xl font-black mb-6 flex items-center gap-4"><span class="bg-blue-600 w-2 h-6"></span> FEATURED 精选资讯</h2>
            <div class="swiper mySwiper">
                <div class="swiper-wrapper">{featured_html}</div>
                <div class="swiper-pagination"></div>
            </div>
        </section>

        <section>
            <h2 class="text-xl font-black mb-6 flex items-center gap-4 text-blue-400"><span class="bg-blue-400 w-2 h-6"></span>
