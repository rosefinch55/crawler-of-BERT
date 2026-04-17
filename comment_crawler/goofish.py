import csv
import time
import random

from DrissionPage import ChromiumPage  # 导入库
import pandas as pd
import json

hrl='https://www.goofish.com/personal?spm=a21ybx.item.itemHeader.1.5db53da6iBXZxi&userId=2200691341105'

# 创建文件对象
f = open('123.csv',mode='w',encoding='utf-8-sig',newline='')
# 字典写入的方法
csv_writer = csv.DictWriter(f,fieldnames=['评论','时间'])
# 写入表头
csv_writer.writeheader()

# 打开浏览器（实例化对象）
dp = ChromiumPage()
# 访问网站
dp.get(hrl)
time.sleep(2)
# 监听
dp.listen.start('mtop.idle.web.trade.rate.list')
dp.ele('text=信用及评价').click()
# 构建循环翻页
# 5️⃣ 循环抓取
for i in range(30):
    try:
        # 等待数据
        resp = dp.listen.wait(timeout=12)
        body = resp.response.body

        # 解析JSON
        data = json.loads(body) if isinstance(body, str) else body

        # 提取评论列表
        for item in data.get('data', {}).get('cardList', []):
            card = item.get('cardData', {})
            # ✅ 只取时间和评论
            csv_writer.writerow({
                '时间': card.get('gmtCreate', ''),
                '评论': card.get('feedback', '')
            })

        print(f"✅ 第{i + 1}页完成")

        # 翻页 + 防封
        if not data.get('data', {}).get('nextPage'):
            break
        dp.scroll.to_bottom()

    except:
        continue
    # 翻页

dp.close()






