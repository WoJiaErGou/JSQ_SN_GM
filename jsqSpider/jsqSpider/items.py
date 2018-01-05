# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JsqspiderItem(scrapy.Item):
    p_Name = scrapy.Field()
    #商品名称
    shop_name = scrapy.Field()
    #店铺名称
    ProductID = scrapy.Field()
    #商品ID
    price = scrapy.Field()
    #原价
    PreferentialPrice = scrapy.Field()
    #售价&折扣价
    CommentCount = scrapy.Field()
    #评论总数&售出数量
    GoodRateShow = scrapy.Field()
    #好评率
    GoodCount = scrapy.Field()
    #好评数
    GeneralCount = scrapy.Field()
    #中评数
    PoorCount = scrapy.Field()
    #差评数
    keyword = scrapy.Field()
    #评论关键词，商品关键词
    type = scrapy.Field()
    #核心参数，全部参数
    brand = scrapy.Field()
    #品牌
    X_name = scrapy.Field()
    #型号
    install = scrapy.Field()
    #安装方式
    drink = scrapy.Field()
    #是否可直饮
    X_type = scrapy.Field()
    #类别
    level = scrapy.Field()
    #滤芯等级
    kinds = scrapy.Field()
    #滤芯种类
    life = scrapy.Field()
    #滤芯使用寿命
    precision = scrapy.Field()
    #过滤精度
    color = scrapy.Field()
    #颜色
    product_url = scrapy.Field()
    #商品链接
    source = scrapy.Field()
    #来源，电商平台
    ProgramStarttime = scrapy.Field()
    #爬取时间
    '''
    'p_Name',
    'shop_name',
    'ProductID',
    'price',
    'PreferentialPrice',
    'CommentCount',
    'GoodRateShow',
    'GoodCount',
    'GeneralCount',
    'PoorCount',
    'keyword',
    'type',         #核心参数
    'brand',        #品牌
    'X_name',       #型号
    'install',      #安装方式
    'drink',        #直饮
    'level',        #滤芯等级
    'kinds',        #滤芯种类
    'life',         #滤芯使用寿命
    'precision',    #过滤精度
    'color',        #颜色
    'product_url',
    'source',
    'ProgramStarttime'
    '''
