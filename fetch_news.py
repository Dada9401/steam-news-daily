import feedparser
import datetime
import re
import time

def get_steam_rss_data(url_type):
    """使用 RSS 绕过 Steam 的 API 封锁"""
    # 构造 RSS 地址 (精选 featured / 官方 official)
    rss_url = f"https://store.steampowered.com/feeds/news/collection/{url_type}/?l=schinese"
    print(f"尝试抓取 RSS: {rss_url}")
    
    slides_html = ""
    try:
        # 解析 RSS
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            print(f"警告: {url_type} 板块未发现任何新闻。")
            return ""

        for entry in feed.entries[:10]:
            title = entry.title
            link = entry.link
            # 从摘要中尝试匹配大图链接
            content = entry.get('summary', '') or entry.get('description', '')
            img_match = re.search(r'<img [^>]*src="([^"]+)"', content)
            
            # 如果没图，用 Steam 默认背景图
            img_url = img_match.group(1) if img_match else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/594650/capsule_617x353.jpg"
            
            slides_html += f'''
            <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
                <div class="relative h-full w-full overflow-hidden rounded-3xl bg-slate-900 border border-white/10 group">
                    <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-60 transition-transform duration-700 group-hover:scale-110">
                    <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
                    <div class="absolute bottom-0 p-6 w-full">
                        <h2 class="text-xl font-bold text-white line-clamp-2 drop-shadow-lg">{title}</h2>
                    </div>
                </div>
            </div>'''
        return slides_html
    except Exception as e:
        print(f"RSS 解析出错 ({url_type}): {e}")
        return ""

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 1. 行业简报
    ticker_text = "行业实时情报同步中..."
    try:
        industry_feed = feedparser.parse("https://www.gamespot.com/feeds/news/")
        if industry_feed.entries:
            ticker_text = " • ".join([f"【{e.title}】" for e in industry_feed.entries[:12]])
    except: pass

    # 2. 抓取板块内容
    featured_html = get_steam_rss_data("featured")
    official_html = get_steam_rss_data("official")

    # 3. 生成 HTML
    full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>STEAM 2026 MONITOR</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: #020408; color: white; font-family: system-ui; overflow-x: hidden; padding-bottom: 100px; }}
        .swiper {{ width: 100%; height: 350px; padding: 20px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 420px; opacity: 0.3; transition: 0.5s; transform: scale(0.8); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); }}
        .ticker-wrap {{ position: fixed; bottom: 0; left: 0; width: 100%; background: #2563eb; color: white; padding: 15px 0; z-index: 100; }}
        .ticker {{ display: inline-block; white-space: nowrap; animation: scroll 60s linear infinite; font-weight: bold; font-size: 14px; }}
        @keyframes scroll {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    </style>
</head>
<body class="p-6 md:p-12">
    <div class="max-w-7xl mx-auto">
        <header class="flex justify-between items-end border-b border-blue-900/40 pb-6 mb-12">
            <div>
                <h1 class="text-5xl font-black italic text-blue-500 tracking-tighter">NEWS MONITOR</h1>
                <p class="text-xs text-blue-400 font-mono mt-2 tracking-[0.3em]">RSS STABLE CHANNEL // JAN 2026</p>
            </div>
            <div class="text-right font-mono text-[10px] text-gray-500 uppercase">SYNC: {now_time}</div>
        </header>

        <h2 class="text-xl font-black mb-8 flex items-center gap-4"><span class="bg-blue-600 w-2 h-6"></span> FEATURED 精选资讯</h2>
        <div class="swiper mySwiper"><div class="swiper-wrapper">{featured_html if featured_html else '<div class="p-10 text-gray-500 italic">精选源同步中...</div>'}</div></div>

        <h2 class="text-xl font-black mb-8 mt-16 flex items-center gap-4 text-blue-400"><span class="bg-blue-400 w-2 h-6"></span> OFFICIAL 官方公告</h2>
        <div class="swiper mySwiper"><div class="swiper-wrapper">{official_html if official_html else '<div class="p-10 text-gray-500 italic">官方源同步中...</div>'}</div></div>
    </div>

    <div class="ticker-wrap"><div class="ticker">GLOBAL NEWS: {ticker_text}</div></div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.mySwiper').forEach(el => {{
            new Swiper(el, {{
                effect: "coverflow", grabCursor: true, centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: {{ delay: 4000 }}, coverflowEffect: {{ rotate: 0, stretch: 0, depth: 150, modifier: 2, slideShadows: false }}
            }});
        }});
    </script>
</body>
</html>'''

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    update_web()
