import feedparser
import datetime
import re

def update_web():
    feed = feedparser.parse("https://store.steampowered.com/feeds/news.xml")
    if not feed.entries: return

    # 生成符合 Swiper 结构的 HTML
    news_html = '<div id="news-container" class="swiper-wrapper">\n'
    for entry in feed.entries[:10]:
        # 提取简短日期
        pub_date = entry.published if 'published' in entry else "LIVE"
        short_date = pub_date[:11]

        news_html += f"""
        <div class="swiper-slide cursor-pointer" onclick="window.open('{entry.link}', '_blank')">
            <div class="mb-4">
                <span class="bg-blue-600 text-[10px] px-2 py-1 rounded shadow-lg font-bold">LATEST REPORT</span>
            </div>
            <h2 class="text-3xl font-bold mb-6 leading-tight hover:text-blue-300 transition-colors">{entry.title}</h2>
            <div class="flex justify-between items-center text-slate-500 text-sm border-t border-white/10 pt-6">
                <span>{short_date}</span>
                <span class="text-blue-400 font-bold uppercase tracking-widest text-xs tracking-widest">Click to Read →</span>
            </div>
        </div>
        """
    news_html += '\n            </div>'

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 替换内容
    pattern = r".*?"
    replacement = f"\n        {news_html}\n        "
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 更新同步时间
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_content = re.sub(r'id="update-time".*?</p>', f'id="update-time" class="text-blue-500 font-mono text-sm mb-12 opacity-60 italic">LAST SYNC: {now_time} @ STEAMWORKS_SERVER</p>', new_content)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    update_web()
