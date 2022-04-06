import json


import requests
import ddddocr

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29'}


def spider(shop_id):
    url = 'http://tiaoma.cnaidc.com'

    # 开启一个会话，模拟浏览器打开一个标签页
    session = requests.session()

    # 获取验证码
    img_data = session.get(url + '/index/verify.html', headers=headers).content

    # 解析验证码
    ocr = ddddocr.DdddOcr()
    img_code = ocr.classification(img_data)

    # form表单
    data = {"code": shop_id, "verify": img_code}

    # 发送post请求
    response = session.post(url + '/index/search.html', headers=headers, data=data)

    # 将得到的数据JSON化
    result = json.loads(response.content)
    print(result)
    return result


if __name__ == '__main__':
    # 从某个文件中读取到shop_id
    with open('shop_id.txt', 'r', encoding='utf-8') as f:
        shop = f.read()

    # 得到返回值
    res = spider(shop_id=shop)

    # 判断是否成功查询到信息
    while res['msg'] != '查询成功':
        if res['msg'] == '该条码不存在或未收录,请稍后再查询':
            break
        res = spider(shop_id=shop)

    # 将查到的信息保存，没查到就保存一个空文件夹
    with open('shop_info.json', 'w', encoding='utf-8') as jsonFile:
        # 如果查到数据，把数据存入文件中
        if res['code'] != 0:
            res = json.dumps(res['json'], ensure_ascii=False)
            jsonFile.write(res)