import requests
import datetime
import time
import feedparser

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"开始同步任务: {now_time}")

    # --- 1. 抓取行业简报 (GameSpot) ---
    ticker_text = "Global Gaming News Stream Online..."
    try:
        print("正在抓取行业简报...")
        feed = feedparser.parse("https://www.gamespot.com/feeds/news/")
        if feed.entries:
            ticker_text = " • ".join([f"【{e.title}】" for e in feed.entries[:12]])
            print("行业简报抓取成功")
    except Exception as e:
        print(f"行业简报抓取失败: {e}")

    # --- 2. 抓取 Steam 数据的函数 (带兜底) ---
    def get_content(clan_id, label):
        print(f"正在抓取 Steam {label} 板块...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        api_url = f"https://store.steampowered.com/events/ajaxgetadjacentevents/?appid=0&clanid={clan_id}&count=10&l=schinese&t={int(time.time())}"
        
        html = ""
        try:
            r = requests.get(api_url, headers=headers, timeout=15)
            if r.status_code == 200:
                events = r.json().get('events', [])
                print(f"{label} 成功获取到 {len(events)} 条数据")
                for e in events:
                    gid = e.get('announcement_body', {}).get('gid', '')
                    img = e.get('jsondata', {}).get('image_url', '')
                    img_url = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/0/events/{gid}/{img}" if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/594650/capsule_617x353.jpg"
                    html += f'''
                    <div class="swiper-slide cursor-pointer" onclick="window.open('https://store.steampowered.com/news/view/{gid}', '_blank')">
                        <div class="relative h-full w-full overflow-hidden rounded-3xl bg-slate-900 border border-white/10 group">
                            <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-50 group-hover:scale-110 transition-duration-500">
                            <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
                            <div class="absolute bottom-0 p-6 w-full"><h2 class="text-lg font-bold text-white line-clamp-2">{e.get('event_name', 'Steam News')}</h2></div>
                        </div>
                    </div>'''
            else:
                print(f"{label} 请求被拒绝，状态码: {r.status_code}")
        except Exception as e:
            print(f"{label} 过程中发生错误: {e}")
        
        # 如果还是没内容，显示一个漂亮的占位卡片
        if not html:
            html = f'''
            <div class="swiper-slide">
                <div class="h-full w-full rounded-3xl bg-slate-900/50 border border-dashed border-white/20 flex items-center justify-center p-10 text-center">
                    <p class="text-gray-500 text-sm italic">Steam {label}数据连接受限<br>正在尝试自动重连...</p>
                </div>
            </div>'''
        return html

    featured_html = get_content("39154431", "精选")
    official_html = get_content("4", "官方")

    # --- 3. 生成完整 HTML ---
    full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STEAM MONITOR 2026</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: #020408; color: white; font-family: system-ui; overflow-x: hidden; padding-bottom: 100px; }}
        .swiper {{ width: 100%; height: 350px; padding: 20px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 400px; opacity: 0.3; transition: 0.5s; transform: scale(0.8); }}
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
                <h1 class="text-5xl font-black italic text-blue-500 tracking-tighter">STEAM MONITOR</h1>
                <p class="text-xs text-blue-400 font-mono mt-2 tracking-[0.3em]">VERSION 2026.01.23 // SECURE</p>
            </div>
            <div class="text-right font-mono text-[10px] text-gray-500 uppercase">SYNC: {now_time}</div>
        </header>

        <h2 class="text-xl font-black mb-8 flex items-center gap-4"><span class="bg-blue-600 w-2 h-6"></span> FEATURED 精选</h2>
        <div class="swiper mySwiper"><div class="swiper-wrapper">{featured_html}</div></div>

        <h2 class="text-xl font-black mb-8 mt-16 flex items-center gap-4 text-blue-400"><span class="bg-blue-400 w-2 h-6"></span> OFFICIAL 官方</h2>
        <div class="swiper mySwiper"><div class="swiper-wrapper">{official_html}</div></div>
    </div>

    <div class="ticker-wrap"><div class="ticker">GLOBAL NEWS BRIEF: {ticker_text}</div></div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.mySwiper').forEach(el => {{
            new Swiper(el, {{
                effect: "coverflow", grabCursor: true, centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: {{ delay: 3000 }}, coverflowEffect: {{ rotate: 0, stretch: 0, depth: 150, modifier: 2, slideShadows: false }}
            }});
        }});
    </script>
</body>
</html>'''

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("网页生成成功！")

if __name__ == "__main__":
    update_web()
