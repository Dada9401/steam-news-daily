import feedparser
import datetime
import re

def update_web():
    # 1. 抓取 Steam 官方 RSS 数据
    feed = feedparser.parse("https://store.steampowered.com/feeds/news.xml")
    
    # 如果没抓到数据就停止
    if not feed.entries:
        print("未抓取到新闻")
        return

    # 2. 准备新的新闻 HTML 片段
    news_html = '<div id="news-container" class="grid grid-cols-1 md:grid-cols-2 gap-6">\n'
    for entry in feed.entries[:10]:
        news_html += f"""
        <div class="bg-[#2a475e]/50 p-6 rounded-xl border border-blue-900/30">
            <h2 class="text-xl font-bold mb-4 text-white">{entry.title}</h2>
            <a href="{entry.link}" target="_blank" class="text-blue-400 hover:underline text-sm">阅读全文 →</a>
        </div>
        """
    news_html += '\n        </div>'

    # 3. 读取现有的 index.html
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 4. 使用正则表达式精准替换“书签”之间的新闻内容
    # 这解决了你之前的 empty separator 报错
    pattern = r".*?"
    replacement = f"\n        {news_html}\n        "
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 5. 更新显示的时间
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    new_content = re.sub(r"更新时间：.*?</p>", f"更新时间：{now_time}</p>", new_content)

    # 6. 保存修改后的文件
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("更新成功！")

if __name__ == "__main__":
    update_web()
