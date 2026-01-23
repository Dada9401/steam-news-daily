import feedparser
import datetime
import re
import time

def get_steam_rss_data(url_type):
    """
    url_type: 'featured' (精选), 'steam' (平台官方), 'all' (全站)
    """
    # 调整官方板块的 RSS 源，'steam' 频道比 'official' 频道更稳定
    rss_url = f"https://store.steampowered.com/feeds/news/collection/{url_type}/?l=schinese"
    print(f"正在尝试抓取 Steam {url_type} 频道: {rss_url}")
    
    slides_html = ""
    try:
        feed = feedparser.parse(rss_url)
        
        # 如果这个频道没内容，尝试抓取全站内容作为补充
        if not feed.entries and url_type != "all":
            print(f"警告: {url_type} 无内容，切换至全站备用源...")
            return get_steam_rss_data("all")

        for entry in feed.entries[:10]:
            title = entry.title
            link = entry.link
            content = entry.get('summary', '') or entry.get('description', '')
            
            # 提取图片：增加容错，匹配多种图片格式
            img_match = re.search(r'<img [^>]*src="([^"]+)"', content)
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
        print(f"RSS 解析出错: {e}")
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

    # 2. 抓取板块内容 (官方板块换成更稳的 'steam' 源)
    featured_html = get_steam_rss_data("featured")
    official_html = get_steam_rss_data("steam")

    # 3. 最终 HTML 模板
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
        .ticker-wrap {{ position: fixed; bottom: 0; left: 0; width: 100%; background: #2563eb; color: white; padding: 15px 0; z-index: 100; box-shadow: 0 -10px 30px rgba(0,0,0,0.5); }}
        .ticker {{ display: inline-block; white-space: nowrap; animation: scroll 80s linear infinite; font-weight: bold; font-size: 14px; }}
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
        <div class="swiper mySwiper"><div class="swiper-wrapper">{featured_html}</div></div>

        <h2 class="text-xl font-black mb-8 mt-16 flex items-center gap-4 text-blue-400"><span class="bg-blue-400 w-2 h-6"></span> OFFICIAL 官方公告</h2>
        <div class="swiper mySwiper"><div class="swiper-wrapper">{official_html}</div></div>
    </div>

    <div class="ticker-wrap"><div class="ticker">GLOBAL NEWS: {ticker_text}</div></div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.mySwiper').forEach(el => {{
            new Swiper(el, {{
                effect: "coverflow", grabCursor: true, centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: {{ delay: 4000, disableOnInteraction: false }},
                coverflowEffect: {{ rotate: 0, stretch: 0, depth: 150, modifier: 2, slideShadows: false }}
            }});
        }});
    </script>
</body>
</html>'''

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    update_web()
