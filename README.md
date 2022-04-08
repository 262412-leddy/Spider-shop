# Spider-shop
1. spider.py 一个简单的爬虫code，通过输入的商品条码来获取商品的基本信息，获取到的商品存入`shop_info.json`文件中  
2. spider-rabbit.py 从shopId队列中获取商品id，经过爬虫爬取信息后，将爬到的信息放回shopInfo队列中
