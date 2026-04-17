import csv
import time

from DrissionPage import ChromiumPage  # 导入库
import pandas as pd

# 创建文件对象
f = open('123.csv',mode='w',encoding='utf-8-sig',newline='')
# 字典写入的方法
csv_writer = csv.DictWriter(f,fieldnames=['评论','时间'])
# 写入表头
csv_writer.writeheader()

# 打开浏览器（实例化对象）
dp = ChromiumPage()
# 访问网站
dp.get('https://item.jd.com/10146439366839.html#comment')
time.sleep(2)
# 监听
dp.listen.start('client.action')
dp.ele('text=全部评价').click()
# 构建循环翻页
for i in range(5):
    # 等待数据包加载
    resp = dp.listen.wait()
    # 获取响应的数据内容
    json_data = resp.response.body
    data = json_data['result']['floors'][2]['data']

    # 解析数据，字典取值，提取评论内容所在列表
    # for循环遍历，提取列表里面的内容
    # 部分评论里没有commentInfo干扰，所以异常处理
    try:
        for index in data:
            # 提取具体评论内容
            dic = {
                '评论': index["commentInfo"]['commentData'],
                '时间': index["commentInfo"]['commentDate']

            }
            # 写入数据

            csv_writer.writerow(dic)
    except:
        pass
    # 翻页
    tab = dp.ele('css:._rateListContainer_1ygkr_45')
    tab.scroll.to_bottom()
    time.sleep(0.1)
dp.close()






