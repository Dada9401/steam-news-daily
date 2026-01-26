import feedparser
import datetime
import re
import time

def get_steam_rss_data(url_type):
    rss_url = f"https://store.steampowered.com/feeds/news/collection/{url_type}/?l=schinese"
    slides_html = ""
    try:
        feed = feedparser.parse(rss_url)
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
                    <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-60 transition-all duration-700 group-hover:scale-110">
                    <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
                    <div class="absolute bottom-0 p-6 w-full"><h2 class="text-xl font-bold text-white line-clamp-2">{title}</h2></div>
                </div>
            </div>'''
        return slides_html
    except: return ""

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

    # 使用普通字符串模板，避免 f-string 的大括号转义问题
    template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>STEAM 2026 MONITOR</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #020408; color: white; font-family: system-ui; overflow-x: hidden; padding-bottom: 120px; }
        .swiper { width: 100%; height: 400px; padding: 20px 0 60px 0; overflow: visible !important; }
        .swiper-slide { width: 420px; opacity: 0.3; transition: 0.5s; transform: scale(0.8); }
        .swiper-slide-active { opacity: 1; transform: scale(1); }
        
        /* 分页器小圆点美化 */
        .swiper-pagination-bullets { bottom: 15px !important; }
        .swiper-pagination-bullet { 
            background: #3b82f6; 
            opacity: 0.3; 
            width: 12px; 
            height: 12px; 
            margin: 0 6px !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .swiper-pagination-bullet-active { 
            background: #60a5fa !important; 
            opacity: 1; 
            width: 35px; 
            border-radius: 6px; 
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.8);
        }

        .ticker-wrap { position: fixed; bottom: 0; left: 0; width: 100%; background: #2563eb; color: white; padding: 15px 0; z-index: 100; }
        .ticker { display: inline-block; white-space: nowrap; animation: scroll 80s linear infinite; font-weight: bold; }
        @keyframes scroll { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
</head>
<body class="p-6 md:p-12 text-slate-200">
    <div class="max-w-7xl mx-auto">
        <header class="flex justify-between items-end border-b border-blue-900/40 pb-6 mb-12">
            <div>
                <h1 class="text-5xl font-black italic text-blue-500 tracking-tighter uppercase">Monitor</h1>
                <p class="text-xs text-blue-400 font-mono mt-2 tracking-[0.3em]">INTERACTIVE HUB // SYNC: {now_time}</p>
            </div>
        </header>

        <section class="mb-16">
            <h2 class="text-xl font-black mb-6 flex items-center gap-4 text-white"><span class="bg-blue-600 w-2 h-6"></span> FEATURED 精选</h2>
            <div class="swiper mySwiper">
                <div class="swiper-wrapper">{featured_html}</div>
                <div class="swiper-pagination"></div>
            </div>
        </section>

        <section>
            <h2 class="text-xl font-black mb-6 flex items-center gap-4 text-blue-400"><span class="bg-blue-400 w-2 h-6"></span> OFFICIAL 官方</h2>
            <div class="swiper mySwiper">
                <div class="swiper-wrapper">{official_html}</div>
                <div class="swiper-pagination"></div>
            </div>
        </section>
    </div>

    <div class="ticker-wrap"><div class="ticker">INDUSTRY UPDATE: {ticker_text}</div></div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.mySwiper').forEach(el => {
            const swiper = new Swiper(el, {
                effect: "coverflow",
                grabCursor: true,
                centeredSlides: true,
                slidesPerView: "auto",
                loop: true,
                autoplay: { delay: 4000, disableOnInteraction: false },
                coverflowEffect: { rotate: 0, stretch: 0, depth: 150, modifier: 2, slideShadows: false },
                pagination: {
                    el: el.querySelector('.swiper-pagination'),
                    clickable: true
                }
            });

            // 核心逻辑：鼠标移入小圆点即切换窗口
            el.addEventListener('mouseover', function(e) {
                if (e.target.classList.contains('swiper-pagination-bullet')) {
                    // 获取当前圆点的索引
                    const bullets = Array.from(el.querySelectorAll('.swiper-pagination-bullet'));
                    const index = bullets.indexOf(e.target);
                    if (index !== -1) {
                        swiper.slideToLoop(index); // 切换到对应卡片
                    }
                }
            });
        });
    </script>
</body>
</html>'''

    # 手动替换变量，避开 f-string 报错
    full_html = template.replace("{now_time}", now_time)\
                        .replace("{featured_html}", featured_html)\
                        .replace("{official_html}", official_html)\
                        .replace("{ticker_text}", ticker_text)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    update_web()
