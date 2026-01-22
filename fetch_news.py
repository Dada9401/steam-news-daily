import feedparser
import datetime
import os

def update_web():
    # 抓取 Steam 官方 RSS
    feed = feedparser.parse("https://store.steampowered.com/feeds/news.xml")
    if not feed.entries:
        return

    news_items_html = ""
    # 只取前 10 条
    for entry in feed.entries[:10]:
        time_str = entry.published if 'published' in entry else "今日"
        news_items_html += f"""
        <div class="news-card bg-[#2a475e]/50 p-6 rounded-xl border border-blue-900/30 hover:border-blue-400/50 shadow-xl">
            <span class="text-blue-400 text-xs font-bold uppercase tracking-tighter italic">{time_str}</span>
            <h2 class="text-xl font-bold mt-2 mb-4 text-white group-hover:text-blue-300">{entry.title}</h2>
            <div class="flex justify-between items-center">
                <a href="{entry.link}" target="_blank" class="inline-block bg-blue-600 hover:bg-blue-500 text-white text-xs px-4 py-2 rounded-md transition">阅读全文</a>
            </div>
        </div>
        """

    # 读取并替换 index.html 中的内容
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 替换容器内容和时间
    new_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    content = content.split('')[0] + '\n<div id="news-container" class="grid grid-cols-1 md:grid-cols-2 gap-6">' + news_items_html + '</div>' + content.split('</div>')[2]
    
    # 极简替换时间戳（定位 ID）
    if "Last Update:" in content:
        import re
        content = re.sub(r"Last Update: \d{4}-\d{2}-\d{2}", f"Last Update: {datetime.date.today()}", content)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_web()
