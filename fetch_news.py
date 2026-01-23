import feedparser
import datetime
import re

def update_web():
    # 1. 抓取 Steam 官方精选 RSS
    # 这个源包含了精选和官方的大部分核心动态
    feed = feedparser.parse("https://store.steampowered.com/feeds/news.xml")
    
    slides_html = ""
    
    # 2. 遍历并提取精华 (包含图片处理)
    for entry in feed.entries[:12]:
        # 尝试从内容中提取第一张图片作为封面
        img_src = "https://community.akamai.steamstatic.com/public/images/sharedfiles/steam_workshop_default_image.png"
        img_match = re.search(r'<img src="(.*?)"', entry.summary)
        if img_match:
            img_src = img_match.group(1)
        
        # 格式化日期
        date_str = entry.published[5:16] if 'published' in entry else "LIVE"

        # 生成卡片 HTML
        slides_html += f"""
        <div class="swiper-slide cursor-pointer" onclick="window.open('{entry.link}', '_blank')">
            <div class="relative h-full w-full overflow-hidden rounded-3xl border border-white/10 group">
                <img src="{img_src}" class="absolute inset-0 w-full h-full object-cover opacity-60 group-hover:scale-110 transition-transform duration-700">
                <div class="absolute inset-0 bg-gradient-to-t from-[#0b0e14] via-[#0b0e14]/40 to-transparent"></div>
                
                <div class="absolute bottom-0 p-8 w-full">
                    <div class="flex items-center gap-3 mb-4">
                        <span class="px-3 py-1 bg-blue-600 text-white text-[10px] font-bold rounded-full uppercase tracking-widest">Official</span>
                        <span class="text-gray-400 text-xs font-mono">{date_str}</span>
                    </div>
                    <h2 class="text-2xl md:text-3xl font-black text-white leading-tight mb-4 group-hover:text-blue-400 transition-colors">
                        {entry.title[:80] + '...' if len(entry.title) > 80 else entry.title}
                    </h2>
                    <p class="text-gray-400 text-sm line-clamp-2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        点击查看详情及完整公告内容
                    </p>
                </div>
            </div>
        </div>
        """

    # 3. 完整的前端页面代码 (高度定制的可视化效果)
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Steam 精选资讯</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #05070a; color: white; min-h-screen; font-family: system-ui; }}
        .swiper {{ width: 100%; max-width: 1000px; height: 600px; padding: 50px 0; }}
        .swiper-slide {{ width: 450px; height: 100%; }}
        @media (max-width: 768px) {{ .swiper-slide {{ width: 85%; height: 80%; }} }}
    </style>
</head>
<body class="flex flex-col items-center justify-center overflow-hidden">
    <div class="text-center z-10 mb-8">
        <h1 class="text-6xl font-black tracking-tighter italic text-transparent bg-clip-text bg-gradient-to-b from-white to-gray-500">
            STEAM NEWS
        </h1>
        <p class="text-blue-500 font-mono text-xs tracking-[0.5em] mt-2 uppercase opacity-80"> 精选 & 官方精华推送 </p>
    </div>

    <div class="swiper mySwiper">
        <div class="swiper-wrapper">
            {slides_html}
        </div>
        <div class="swiper-pagination"></div>
    </div>

    <div class="mt-8 text-gray-600 text-[10px] font-mono tracking-widest uppercase">
        Last Sync: {now_time} | Auto-Update Daily
    </div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            new Swiper(".mySwiper", {{
                effect: "coverflow",
                grabCursor: true,
                centeredSlides: true,
                slidesPerView: "auto",
                loop: true,
                coverflowEffect: {{ rotate: 20, stretch: 0, depth: 200, modifier: 1, slideShadows: true }},
                autoplay: {{ delay: 3500, disableOnInteraction: false }},
                pagination: {{ el: ".swiper-pagination", clickable: true }},
            }});
        }});
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("精华内容抓取完成，带图页面已重新生成！")

if __name__ == "__main__":
    update_web()
