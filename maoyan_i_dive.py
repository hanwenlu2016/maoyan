import requests
from lxml import etree
import pymysql
'''
由于数据库比较少没有使用多线程
'''

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Host': 'maoyan.com',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36',
           'Upgrade-Insecure-Requests': '1'}


# 产生URL参数列表
def url():
    list_url = []
    # 推导 0到90间隔10
    for i in (i * 10 for i in range(10)):
        url = 'http://maoyan.com/board/4?offset={}'.format(i)
        list_url.append(url)
    return list_url


# 解析出html数据
def get_html(url_list):
    list_data = []
    for url in url_list:
        res = requests.get(url, headers=headers)
        links = etree.HTML(res.text)
        for link in links.xpath('//div[@class="container"]/div/div/div/dl/dd'):
            my_data = {}
            my_data['电影名称'] = link.xpath('./a/@title')[0]
            my_data['主演'] = str(link.xpath('./div/div/div/p[2]/text()')[0]).replace('\n', '').replace('\\n',
                                                                                                      '').replace(' ',
                                                                                                                  '')[
                            3:]
            my_data['上映时间'] = link.xpath('./div/div/div/p[3]/text()')[0][5:]
            my_data['评分'] = str(link.xpath('./div/div/div/p/i[1]/text()')[0]) + str(
                (link.xpath('./div/div/div/p/i[2]/text()')[0]))  # 由于不好取评分值写了一个笨办法

            # 追加到列表 因为我们要存放到数据库所以放到列表
            list_data.append(my_data)

    # 返回数据列表  返回时注意循环的层次
    return list_data


if __name__ == '__main__':
    # 连接mysql数据库  写自己实际的数据库连接地址
    db = pymysql.connect(host="127.0.0.1", user="root", port=3307, password="123456", db="move",
                         charset="utf8")
    # 创建游标
    cursor = db.cursor()
    for i in get_html(url()):
        name = i.get('电影名称')
        usre = i.get('主演')
        time = i.get('上映时间')
        secre = i.get('评分')

        try:
            sql = "insert into my_move(mova_name, move_usre, move_time, move_score) values('%s', '%s', '%s', '%s');" % (
                name, usre, time, secre)
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            raise e
    print("数据插入成功\n*************\n")
    # 关闭数据库
    db.close()
