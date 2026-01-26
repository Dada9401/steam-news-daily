import feedparser
import datetime
import re

# --- 2026 Steam 官方活动时间轴 ---
STEAM_EVENTS_2026 = [
    {"name": "棋盘游戏节", "start": "20260126", "end": "20260202", "type": "fest"},
    {"name": "打字节 (焦点节)", "start": "20260205", "end": "20260209", "type": "spotlight"},
    {"name": "PvP 游戏节", "start": "20260209", "end": "20260216", "type": "fest"},
    {"name": "Steam 新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest", "appid": "3985950"},
    {"name": "Steam 春季特卖", "start": "20260319", "end": "20260326", "type": "major"},
]

def get_steam_rss_data(mode):
    # --- 这里是关键：严格区分源 ---
    if mode == "featured":
        # 精选板块：依然保持多样化，但权重向官方倾斜
        urls = ["https://store.steampowered.com/feeds/news/collection/featured/?l=schinese"]
    else:
        # 官方板块：只锁定 Valve 亲生的官方频道，杜绝乱七八糟的游戏新闻
        urls = [
            "https://store.steampowered.com/feeds/news/group/4145017/?l=schinese", # Steamworks 官方组
            "https://store.steampowered.com/feeds/news/app/3985950/?l=schinese",   # 2026新品节
            "https://store.steampowered.com/feeds/news/group/39049601/?l=schinese", # Steam 官方频道
        ]

    entries = []
    seen = set()
    for url in urls:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries:
                if e.link not in seen:
                    # 只有标题包含核心官方词汇的才放进 Official 板块
                    if mode == "official":
                        if any(k in e.title for k in ["Steam", "新品节", "公告", "Next Fest", "新鲜出炉"]):
                            entries.append(e)
                            seen.add(e.link)
                    else:
                        entries.append(e)
                        seen.add(e.link)
        except: continue

    # 排序：新品节和官方预告永远排在最前面
    entries.sort(key=lambda x: any(k in x.title for k in ["新品节", "Next Fest", "2026"]), reverse=True)

    html = ""
    for e in entries[:10]:
        title, link = e.title, e.link
        content = e.get('summary', '') or e.get('description', '')
        img = re.search(r'<img [^>]*src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        
        # 针对新品节的视觉高亮
        is_nf = "新品节" in title or "Next Fest" in title
        tag = '<span class="bg-yellow-400 text-black text-[10px] px-2 py-0.5 rounded font-black mr-2">VALVE OFFICIAL</span>' if is_nf else ""
        
        html += f'''
        <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-full w-full overflow-hidden rounded-[2rem] bg-slate-100 dark:bg-slate-900 border {"border-yellow-400" if is_nf else "border-slate-200 dark:border-white/5"} transition-all duration-500 shadow-xl">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-80 dark:opacity-40 transition-transform duration-700 group-hover:scale-110">
                <div class="absolute inset-0 bg-gradient-to-t from-white/90 dark:from-black via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <h2 class="text-xl font-black text-slate-900 dark:text-white line-clamp-2">{tag}{title}</h2>
                </div>
            </div>
        </div>'''
    return html

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    feat_html = get_steam_rss_data("featured")
    offi_html = get_steam_rss_data("official") # 现在这里非常干净了

    template = f'''<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
    <meta charset="UTF-8">
    <title>STEAM INTEL 2026</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{ darkMode: 'class' }}
        function toggleMode() {{
            document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
        }}
    </script>
    <style>
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .swiper {{ width: 100%; height: 420px; padding: 20px 0 80px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 520px; opacity: 0.1; transition: 0.6s; transform: scale(0.8); filter: blur(5px); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); filter: blur(0); z-index: 10; }}
        body {{ transition: background-color 0.4s; }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#020408] text-slate-900 dark:text-white p-6 md:p-12 min-h-screen">
    <div class="max-w-[1600px] mx-auto">
        <header class="flex justify-between items-center mb-16 border-b border-slate-200 dark:border-white/10 pb-10">
            <div>
                <h1 class="text-6xl font-black italic tracking-tighter uppercase leading-none">Steam Intel</h1>
                <p class="text-[11px] text-blue-600 dark:text-blue-500 font-mono mt-4 tracking-[0.5em] uppercase">Status: Connected // {now_time}</p>
            </div>
            <button onclick="toggleMode()" class="flex items-center gap-3 px-6 py-3 rounded-full bg-white dark:bg-slate-800 shadow-2xl border border-slate-200 dark:border-white/10 transition-all active:scale-95">
                <span class="dark:hidden">🌙 夜间模式</span>
                <span class="hidden dark:inline">☀️ 日间模式</span>
            </button>
        </header>

        <main class="space-y-28">
            <section>
                <div class="flex items-center gap-4 mb-8"><h2 class="text-3xl font-black italic uppercase">Featured 精选流</h2><div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div></div>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{feat_html}</div><div class="swiper-pagination"></div></div>
            </section>
            
            <section>
                <div class="flex items-center gap-4 mb-8 text-blue-600 dark:text-blue-400"><h2 class="text-3xl font-black italic uppercase">Official 官方公告</h2><div class="h-px flex-1 bg-blue-500/20"></div></div>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{offi_html}</div><div class="swiper-pagination"></div></div>
            </section>
        </main>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        if (localStorage.getItem('theme') === 'light') document.documentElement.classList.remove('dark');
        document.querySelectorAll('.mySwiper').forEach(el => {{
            new Swiper(el, {{
                effect: "coverflow", centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: {{ delay: 5000 }},
                coverflowEffect: {{ rotate: 0, stretch: 80, depth: 150, modifier: 1, slideShadows: false }},
                pagination: {{ el: el.querySelector('.swiper-pagination'), clickable: true }}
            }});
        }});
    </script>
</body>
</html>'''
    with open("index.html", "w", encoding="utf-8") as f: f.write(template)

if __name__ == "__main__":
    update_web()
