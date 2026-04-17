import csv
import time
import json
import re
from DrissionPage import ChromiumPage

import re
from urllib.parse import urlparse, parse_qs


def extract_tmall_item_id(url):
    """
    从天猫/淘宝商品链接中提取数字ID
    支持：
    - https://detail.tmall.com/item.htm?id=632605090131&...
    - https://item.taobao.com/item.htm?id=632605090131
    - https://detail.tmall.com/item.htm?spm=...&id=632605090131
    - https://h5.m.taobao.com/awp/core/detail.htm?id=632605090131
    """
    # 方法1：正则直接提取 id=数字
    match = re.search(r'[?&]id=(\d+)', url)
    if match:
        return match.group(1)

    # 方法2：解析URL参数（备用）
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    if 'id' in params:
        return params['id'][0]

    # 方法3：从路径中提取（极少数情况）
    path_match = re.search(r'/item/(\d+)', parsed.path)
    if path_match:
        return path_match.group(1)

    raise ValueError(f"无法从URL中提取商品ID: {url}")


url='https://detail.tmall.com/item.htm?abbucket=11&id=743999875667&mi_id=0000fDFQbFQsuBplTh_75gJichxbSdXMGD6mGuiSaG3e6PQ&ns=1&priceTId=214783f217763894098477652e1300&skuId=6175430691608&spm=a21n57.1.hoverItem.5&utparam=%7B%22aplus_abtest%22%3A%22e4cd788784e70a281ce38b9ee8400d01%22%7D&xxc=taobaoSearch'
# 使用示例
item_id = extract_tmall_item_id(url)
url = f'https://detail.tmall.com/item.htm?id={item_id}'

f = open('天猫评论.csv', mode='w', encoding='utf-8-sig', newline='')
csv_writer = csv.DictWriter(f, fieldnames=['评论', '时间'])
csv_writer.writeheader()

dp = ChromiumPage()
dp.get(url)
time.sleep(2)

dp.listen.start('mtop.taobao.rate.detaillist.get')
dp.ele('text=查看全部评价').click()
time.sleep(1.5)

comment_panel = dp.ele('xpath://div[contains(@class,"comments--") and contains(@style,"overflow-y: scroll")]')
if not comment_panel:
    print("⚠️ 未找到评论容器，将尝试滚动整个页面")
    comment_panel = dp

page = 1
timeout_count = 0  # 连续超时计数器

while True:
    try:
        resp = dp.listen.wait(timeout=2)  # 适当缩短超时时间
        if not resp:
            timeout_count += 1
            print(f"⚠️ 第{page}页监听超时 (连续{timeout_count}次)")

            # 连续超时2次，或之前已抓到过数据但超时，则判定为无更多数据
            if timeout_count >= 2:
                print("📭 连续超时，已无更多评论，退出")
                break

            comment_panel.scroll.to_bottom()
            time.sleep(0.2)
            continue
        else:
            timeout_count = 0  # 有数据返回则重置超时计数

        body = resp.response.body

        # 解析 JSONP
        if isinstance(body, str):
            match = re.search(r'\(({.*})\)', body, re.S)
            if match:
                root = json.loads(match.group(1))
            else:
                root = json.loads(body)
        else:
            root = body

        data = root.get('data', {})
        rate_list = data.get('rateList', [])

        for item in rate_list:
            csv_writer.writerow({
                '时间': item.get('feedbackDate', ''),
                '评论': item.get('feedback', '')
            })

        print(f"✅ 第{page}页完成，本页{len(rate_list)}条")

        # 检查 hasNext 字段
        if not data.get('hasNext'):
            print("🎉 已抓取全部评论")
            break

        # 有下一页则滚动并继续
        comment_panel.scroll.to_bottom()
        time.sleep(0.2)
        page += 1

        if page==15 :
            break


    except Exception as e:
        print(f"❌ 第{page}页出错：{e}")
        comment_panel.scroll.to_bottom()
        time.sleep(2)
        continue

dp.close()
print("抓取完成！")