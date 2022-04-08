import json

import pika
import requests
import ddddocr

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29'}


# 爬虫
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


# 向消息队列发送查询到的商品信息
def sendToRabbitMq(shopinfo):
    credentials = pika.PlainCredentials('ledyy', '123456')
    connectionBuild = pika.ConnectionParameters(host='localhost',
                                                port=5672,
                                                virtual_host='/shop_repository',
                                                credentials=credentials)
    connection = pika.BlockingConnection(connectionBuild)
    channel = connection.channel()

    channel.queue_declare(queue='shopInfo', durable=True)
    channel.basic_publish(exchange='',
                          routing_key='shopInfo',
                          body=shopinfo)
    connection.close()


# 从消息队列中拿待查询商品的条码
def receiveFromRabbitMq():
    credentials = pika.PlainCredentials('ledyy', '123456')
    connectionBuild = pika.ConnectionParameters(host='localhost',
                                                port=5672,
                                                virtual_host='/shop_repository',
                                                credentials=credentials)
    connection = pika.BlockingConnection(connectionBuild)
    channel = connection.channel()

    def callback(ch, method, properties, body):
        shop = body
        # 得到返回值
        res = spider(shop_id=shop)

        # 判断是否成功查询到信息
        while res['msg'] != '查询成功':
            if res['msg'] == '该条码不存在或未收录,请稍后再查询':
                break
            res = spider(shop_id=shop)

        # 将查到的信息发向消息队列，没查到发空消息
        if res['code'] != 0:
            res = json.dumps(res['json'], ensure_ascii=False)
            sendToRabbitMq(res)

    channel.queue_declare(queue='shopId', durable=True)
    channel.basic_consume(queue='shopId',
                          auto_ack=True,
                          on_message_callback=callback)

    # channel.start_consuming()


if __name__ == '__main__':
    receiveFromRabbitMq()
