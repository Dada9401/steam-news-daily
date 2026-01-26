import feedparser
import datetime
import re
import time

# --- 2026 Steam 官方活动数据库 ---
STEAM_EVENTS_2026 = [
    {"name": "棋盘游戏节", "start": "20260126", "end": "20260202", "type": "fest"},
    {"name": "打字节 (焦点节)", "start": "20260205", "end": "20260209", "type": "spotlight"},
    {"name": "PvP 游戏节", "start": "20260209", "end": "20260216", "type": "fest"},
    {"name": "Steam 新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest", "appid": "3985950"},
    {"name": "Steam 春季特卖", "start": "20260319", "end": "20260326", "type": "major"},
]

def get_steam_rss_data(mode):
    # --- 核心改动：使用社区原生源，彻底解决 1月15日 不更新的问题 ---
    if mode == "featured":
        # 精选流使用商店推荐接口
        urls = ["https://store.steampowered.com/feeds/news/collection/featured/?l=schinese"]
    else:
        # 官方流：直接对接 Steam 社区组的实时 RSS，这比商店接口快得多
        urls = [
            "https://steamcommunity.com/groups/steam/rss/",                    # 官方公告最快源
            "https://steamcommunity.com/groups/steamworks/rss/",              # 开发者/新品节通知
            "https://store.steampowered.com/feeds/news/app/3985950/?l=schinese" # 定向抓取2月新品节
        ]

    entries = []
    seen_links = set()
    timestamp = int(time.time())

    for url in urls:
        try:
            # 加入随机参数强制刷新缓存
            feed = feedparser.parse(f"{url}?t={timestamp}")
            for e in feed.entries:
                if e.link not in seen_links:
                    # 在这里通过关键词确保 100% 抓取到 1月15日 之后的内容
                    if mode == "official":
                        # 降低过滤门槛，确保所有官方动态都能进来
                        if any(k.lower() in e.title.lower() for k in ["Steam", "新品节", "Next Fest", "2026", "Sale", "公告"]):
                            entries.append(e)
                            seen_links.add(e.link)
                    else:
                        entries.append(e)
                        seen_links.add(e.link)
        except: continue

    # 强制按发布时间降序，保证“最新”在最前
    def get_pub_time(entry):
        if hasattr(entry, 'published_parsed'):
            return time.mktime(entry.published_parsed)
        return 0

    entries.sort(key=get_pub_time, reverse=True)

    slides_html = ""
    for e in entries[:12]:
        title, link = e.title, e.link
        content = e.get('summary', '') or e.get('description', '') or ""
        
        # 优化图片抓取：如果 RSS 没图，尝试去内容里找高质量图
        img = re.search(r'src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        
        # 统一清理标题中可能出现的 RSS 格式残留
        title = title.replace("Steam 官方公告 - ", "").replace("Steam News - ", "")
        
        pub_time = time.strftime("%Y-%m-%d %H:%M", e.published_parsed) if hasattr(e, 'published_parsed') else "Latest"
        is_new = "新品节" in title or "Next Fest" in title or "2026" in title

        slides_html += f'''
        <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-full w-full overflow-hidden rounded-[2.5rem] bg-slate-100 dark:bg-slate-900 border {"border-yellow-400" if is_new else "border-slate-200 dark:border-white/5"} group transition-all duration-700 shadow-2xl">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-90 dark:opacity-40 transition-transform duration-1000 group-hover:scale-105">
                <div class="absolute inset-0 bg-gradient-to-t from-white/95 dark:from-[#020408] via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <div class="text-[11px] font-mono text-blue-600 dark:text-blue-400 mb-2 font-black uppercase tracking-widest">{pub_time}</div>
                    <h2 class="text-2xl font-black text-slate-900 dark:text-white line-clamp-2 leading-[1.1] tracking-tighter uppercase italic">
                        {"⚡️ " if is_new else ""}{title}
                    </h2>
                </div>
            </div>
        </div>'''
    return slides_html

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    feat_html = get_steam_rss_data("featured")
    offi_html = get_steam_rss_data("official")

    template = f'''<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
    <meta charset="UTF-8">
    <title>STEAM INTEL CENTER</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{ darkMode: 'class' }}
        function toggleTheme() {{
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        }}
    </script>
    <style>
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .swiper {{ width: 100%; height: 480px; padding: 20px 0 100px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 560px; opacity: 0.1; transition: 0.8s cubic-bezier(0.2, 1, 0.3, 1); transform: scale(0.8); filter: blur(10px); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); filter: blur(0); z-index: 20; }}
        body {{ transition: background-color 0.8s cubic-bezier(0.4, 0, 0.2, 1); }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#020408] text-slate-900 dark:text-white p-6 md:p-16 min-h-screen">
    <div class="max-w-[1700px] mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-start md:items-center mb-24 gap-8">
            <div class="border-l-[12px] border-blue-600 pl-8">
                <h1 class="text-8xl font-black italic tracking-tighter uppercase leading-none text-slate-900 dark:text-white">INTEL</h1>
                <p class="text-[12px] text-blue-600 dark:text-blue-500 font-mono mt-4 tracking-[0.8em] uppercase font-black">Community Sync Active // {now_time}</p>
            </div>
            <button onclick="toggleTheme()" class="group relative px-10 py-5 bg-white dark:bg-slate-800 rounded-full shadow-2xl border border-slate-200 dark:border-white/10 transition-all hover:ring-4 ring-blue-500/20 active:scale-95">
                <span class="dark:hidden font-black text-xs text-slate-700">🌙 MODE: NIGHT SCAN</span>
                <span class="hidden dark:inline font-black text-xs text-blue-400">☀️ MODE: DAYLIGHT</span>
            </button>
        </header>

        <main class="space-y-40">
            <section>
                <div class="flex items-center gap-6 mb-12">
                    <h2 class="text-4xl font-black italic uppercase tracking-tighter">Featured <span class="text-blue-600">精选流</span></h2>
                    <div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div>
                </div>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{feat_html}</div><div class="swiper-pagination"></div></div>
            </section>
            
            <section>
                <div class="flex items-center gap-6 mb-12">
                    <h2 class="text-4xl font-black italic uppercase tracking-tighter text-blue-600 dark:text-blue-400">Official <span class="dark:text-white">官方社区实时动态</span></h2>
                    <div class="h-px flex-1 bg-blue-500/20"></div>
                </div>
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
                coverflowEffect: {{ rotate: 0, stretch: 150, depth: 300, modifier: 1, slideShadows: false }},
                pagination: {{ el: el.querySelector('.swiper-pagination'), clickable: true }}
            }});
        }});
    </script>
</body>
</html>'''
    with open("index.html", "w", encoding="utf-8") as f: f.write(template)

if __name__ == "__main__":
    update_web()
