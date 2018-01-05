import scrapy
from scrapy import Selector
import requests
from requests import Session,adapters
import re
import time
from bs4 import BeautifulSoup
from GM_jsqSpider.items import GmJsqspiderItem
import pandas as pd
class Jsq_gmspider(scrapy.Spider):
    name='gm_jsq'
    def start_requests(self):
        df=pd.read_csv('国美净水器.csv')
        urllist=list(df['url'])
        ProgramStarttime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        item = GmJsqspiderItem(ProgramStarttime=ProgramStarttime)
        for each in urllist:
            yield scrapy.Request(url=each,callback=self.product_page,dont_filter=False,meta={'item':item})
            # break
    def product_page(self,response):
        # 检测到网页长度不足证明网页内容不全，重新获取
        if len(response.text) < 30000:
            yield scrapy.Request(url=response.request.url, callback=self.product_page, dont_filter=True)
            return None
        #商品集合页查询商品名称，店铺名称，商品详情页url
        item = response.meta['item']
        product_url = response.request.url
        if 'deal' in product_url:
            skuID = re.findall('sku:"(.*?)"',response.text)[0]
        else:
            skuID = None
        try:
            p_Name=re.findall("prdName:'(.*?)'",response.text)[0]
        except:
            try:
                p_Name=re.findall('商品名称：(.*?)</div>',response.text)[0]
            except:
                try:
                    p_Name = re.findall('itemName:"(.*?)"',response.text)[0]
                except:
                    try:
                        p_Name = re.findall('description:"(.*?)"',response.text)[0]
                    except:
                        p_Name=None
        #商品ID
        try:
            ProductID = Selector(response).re('prdId:"(.*?)"')[0]
        except:
            try:
                ProductID = re.findall('prdId:"(.*?)"', response.text)[0]
            except:
                try:
                    ProductID = re.findall('prdId:"(.*?)"', response.text)[0]
                except:
                    ProductID = response.url.split('/')[-1].split('-')[0]
        # 好评，差评等信息采集
        comment_url = 'http://ss.gome.com.cn/item/v1/prdevajsonp/appraiseNew/%s/1/all/0/10/flag/appraise' % ProductID
        mark_url = 'http://ss.gome.com.cn/item/v1/prdevajsonp/productEvaComm/%s/flag/appraise/totleMarks?callback=totleMarks' % ProductID
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        request_retry = requests.adapters.HTTPAdapter(max_retries=3)
        with Session() as gome:
            # 建立会话对象
            gome.mount('http://', request_retry)
            gome.mount('https://', request_retry)
            gome.headers = headers
            comment_text = gome.get(url=comment_url).text
            time.sleep(0.3)
            mark_text = gome.get(url=mark_url).text
        # 店铺名称
        try:
            shop_name = response.xpath(".//div[@class='zy-stores shops-name']/a[@class='name']/text()").extract()[0]
        except:
            try:
                shop_name = response.xpath(".//h2[@id='store_live800_wrap']/a[@class='name']/text()").extract()[0]
            except:
                try:
                    shop_name = response.xpath(".//div[@class='zy-stores shops-name']/span[@class='identify']/text()").extract()[0]
                except:
                    shop_name = None
        # 价格类代码重写
        try:
            Price = re.findall('price:"(.*?)"', response.text)
            gomeprice = re.findall('gomePrice:"(.*?)"', response.text)
            groupprice = re.findall('groupPrice:"(.*?)"', response.text)
            oldprice = re.findall('<span id="listPrice">(.*?)</span>', response.text)
            if Price:
                if Price[0] == '0':
                    price = gomeprice[0]
                    PreferentialPrice = gomeprice[0]
                else:
                    if float(Price[0]) < float(gomeprice[0]):
                        price = gomeprice[0]
                        PreferentialPrice = Price[0]
                    else:
                        price = Price[0]
                        PreferentialPrice = gomeprice[0]
            else:
                if float(oldprice[0]) < float(groupprice[0]):
                    price = groupprice[0]
                    PreferentialPrice = oldprice[0]
                else:
                    price = oldprice[0]
                    PreferentialPrice = groupprice[0]
            if 'deal' in product_url:
                PreferentialPrice = groupprice[0]
                price = None
        except:
            price = None
            PreferentialPrice = None
        #真划算
        if skuID:
            try:
                get_price='http://ajaxtuan.gome.com.cn/cheap/getSkuPrice?callback=getSkuPrice&skuId=%s' % skuID
                if not price:
                    price_text=requests.get(get_price,headers=headers).text
                    price=re.findall('"data":"(.*?)"',price_text)[0]
                    print(price)
                    print(PreferentialPrice)
                    if float(price)<float(PreferentialPrice):
                        tt =price
                        price = price[:0] + PreferentialPrice
                        PreferentialPrice = PreferentialPrice[:0] + tt
            except:
                pass
        # 品牌
        try:
            brand = Selector(response).re('品牌：(.*?)</div>')[0]
        except:
            try:
                brand = re.findall('品牌：(.*?)</div>', response.text)[0]
            except:
                brand = None
        if brand:
            if re.findall(r'（.*?）', brand):
                re_com = re.compile('（.*?）')
                brand = brand[:0] + re.sub(re_com, '', brand)
        if brand:
            if re.findall(r'(.*?)', brand):
                re_cn = re.compile('\(.*?\)')
                brand = brand[:0] + re.sub(re_cn, '', brand)
        # 品牌型号
        try:
            X_name = Selector(response).re('型号：(.*?)</div>')[0]
        except:
            try:
                X_name = re.findall('型号：(.*?)</div>', response.text)[0]
            except:
                try:
                    X_name = Selector(response).re('型号</span><span>(.*?)</span>')[0]
                except:
                    try:
                        X_name = re.findall('型号</span><span>(.*?)</span>', response.text)[0]
                    except:
                        X_name = None
        if X_name:
            if brand:
                if brand in X_name:
                    X_name = X_name[:0] + re.sub(brand, '', X_name)
            X_name = X_name[:0] + re.sub(r'（.*?）', '', X_name)
            X_name = X_name[:0] + re.sub(r'\(.*?\)', '', X_name)
        #颜色
        try:
            color = Selector(response).re('颜色</span><span>(.*?)</span>')[0]
        except:
            try:
                color = re.findall('颜色</span><span>(.*?)</span>', response.text)[0]
            except:
                color = None
        #类别
        try:
            X_type = Selector(response).re('类别：(.*?)</div>')[0]
        except:
            try:
                X_type = re.findall('类别：(.*?)</div>', response.text)[0]
            except:
                try:
                    X_type = Selector(response).re('类别</span><span>(.*?)</span>')[0]
                except:
                    try:
                        X_type = re.findall('类别</span><span>(.*?)</span>', response.text)[0]
                    except:
                        X_type = None
        #安装方式
        try:
            install = Selector(response).re('安装位置：(.*?)</div>')[0]
        except:
            try:
                install = re.findall('安装位置：(.*?)</div>', response.text)[0]
            except:
                try:
                    install = Selector(response).re('安装位置</span><span>(.*?)</span>')[0]
                except:
                    try:
                        install = re.findall('安装位置</span><span>(.*?)</span>', response.text)[0]
                    except:
                        install = None
        #是否直饮
        try:
            drink = Selector(response).re('直饮：(.*?)</div>')[0]
        except:
            try:
                drink = re.findall('直饮：(.*?)</div>', response.text)[0]
            except:
                try:
                    drink = Selector(response).re('直饮</span><span>(.*?)</span>')[0]
                except:
                    try:
                        drink = re.findall('直饮</span><span>(.*?)</span>', response.text)[0]
                    except:
                        drink = None
        #滤芯等级
        try:
            level = Selector(response).re('过滤级别：(.*?)</div>')[0]
        except:
            try:
                level = re.findall('过滤级别：(.*?)</div>', response.text)[0]
            except:
                try:
                    level = Selector(response).re('过滤级别</span><span>(.*?)</span>')[0]
                except:
                    try:
                        level = re.findall('过滤级别</span><span>(.*?)</span>', response.text)[0]
                    except:
                        level = None
        #滤芯种类
        try:
            kinds = Selector(response).re('滤芯种类：(.*?)</div>')[0]
        except:
            try:
                kinds = re.findall('滤芯种类：(.*?)</div>', response.text)[0]
            except:
                try:
                    kinds = Selector(response).re('滤芯种类</span><span>(.*?)</span>')[0]
                except:
                    try:
                        kinds = re.findall('滤芯种类</span><span>(.*?)</span>', response.text)[0]
                    except:
                        try:
                            kinds = re.findall('滤芯构成：(.*?)</div>', response.text)[0]
                        except:
                            kinds = None
        #滤芯使用寿命
        life = None
        #过滤精度
        try:
            precision = Selector(response).re('过滤精度：(.*?)</div>')[0]
        except:
            try:
                precision = re.findall('过滤精度：(.*?)</div>', response.text)[0]
            except:
                try:
                    precision = Selector(response).re('过滤精度</span><span>(.*?)</span>')[0]
                except:
                    try:
                        precision = re.findall('过滤精度</span><span>(.*?)</span>', response.text)[0]
                    except:
                        precision = None
        '''核心参数，特别处理部分'''
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            parameter = []
            div_item = soup.find_all('div', class_='param-item')
            # print(div_item)
            for each in div_item:
                li_list = each.find_all('li')
                for each in li_list:
                    li_text = re.sub(r'\n', '', each.text)
                    parameter.append(li_text)
            if len(parameter) < 1:
                print(1 / 0)
        except:
            try:
                parameter = []
                div_item = soup.find('div', class_='guigecanshu_wrap')
                div_canshu = div_item.find_all('div', class_='guigecanshu')
                for each in div_canshu:
                    parameter.append(each.text)
                if len(parameter) < 1:
                    print(1 / 0)
            except:  # 针对真划算页面的type参数分析
                try:
                    parameter = []
                    table = soup.find('table', attrs={'class': 'grd-specbox'})
                    tr_list = table.find_all('tr')
                    for each in tr_list:
                        if each.find('td'):
                            td = each.find_all('td')
                            if td:
                                td1 = re.sub(r'\n', '', td[0].text)
                                td2 = re.sub(r'\n', '', td[1].text)
                                parameter.append(td1 + ':' + td2)
                                # print(td1 + ':' + td2)
                    print(parameter)
                    if len(parameter) < 1:
                        print(1 / 0)
                except:
                    parameter = None
        # 将核心参数转化为字符串形式
        try:
            if parameter == None:
                type = None
            else:
                type = '"'
                for i in range(len(parameter)):
                    type = type[:] + parameter[i]
                    if i < len(parameter) - 1:
                        type = type[:] + ' '
                    if i == len(parameter) - 1:
                        type = type[:] + '"'
        except:
            type = None
        if type:
            if brand == None:
                try:
                    brand = re.findall('品牌:(.*?) ', type)[0]
                except:
                    brand = None
            if brand:
                if re.findall(r'（.*?）', brand):
                    re_com = re.compile('（.*?）')
                    brand = brand[:0] + re.sub(re_com, '', brand)
            if brand:
                if re.findall(r'(.*?)', brand):
                    re_cn = re.compile('\(.*?\)')
                    brand = brand[:0] + re.sub(re_cn, '', brand)
            if X_name == None:
                try:
                    X_name = re.findall('型号:(.*?) ', type)[0]
                except:
                    X_name = None
            if X_name:
                if brand:
                    if brand in X_name:
                        X_name = X_name[:0] + re.sub(brand, '', X_name)
                X_name = X_name[:0] + re.sub(r'（.*?）', '', X_name)
                X_name = X_name[:0] + re.sub(r'\(.*?\)', '', X_name)
            if color == None:
                try:
                    color = re.findall('颜色:(.*?) ', type)[0]
                except:
                    color = None
            if X_type == None:
                try:
                    X_type = re.findall('类别:(.*?) ', type)[0]
                except:
                    X_type = None
            #安装方式
            if install == None:
                try:
                    install = re.findall('安装位置:(.*?) ', type)[0]
                except:
                    install = None
            #是否直饮
            if drink == None:
                try:
                    drink = re.findall('直饮:(.*?) ', type)[0]
                except:
                    drink = None
            #滤芯等级
            if level == None:
                try:
                    level = re.findall('过滤级别:(.*?) ', type)[0]
                except:
                    level = None
            #滤芯种类
            if kinds == None:
                try:
                    kinds = re.findall('滤芯种类:(.*?) ', type)[0]
                except:
                    try:
                        kinds = re.findall('滤芯构成:(.*?) ',type)[0]
                    except:
                        kinds = None
            #过滤精度
            if precision == None:
                try:
                    precision = re.findall('过滤精度:(.*?) ', type)[0]
                except:
                    precision = None
        # 访问comment_url
        try:
            # 好评
            GoodCount = re.findall('"good":(.*?),', comment_text)[0]
        except:
            GoodCount = None
            # 中评
        try:
            GeneralCount = re.findall('"mid":(.*?),', comment_text)[0]
        except:
            GeneralCount = None
            # 差评
        try:
            PoorCount = re.findall('"bad":(.*?),', comment_text)[0]
        except:
            PoorCount = None
            # 总评
        try:
            CommentCount = re.findall('"totalCount":(.*?),', comment_text)[0]
        except:
            CommentCount = None
        # 访问评论关键字
        # 好评度
        try:
            GoodRateShow = re.findall(r'"goodCommentPercent":(\d+)', mark_text)[0]
        except:
            try:
                GoodRateShow = re.findall(r'"good":(\d+),', mark_text)[0]
            except:
                GoodRateShow = None
        try:
            keyword = '"'
            word_list = re.findall('"recocontent":"(.*?)"', mark_text)
            for each in word_list:
                if '?' in each:
                    word_list.remove(each)
            if word_list:
                for every in word_list:
                    keyword = keyword[:] + every
                    if every != word_list[-1]:
                        keyword = keyword[:] + ' '
                    if every == word_list[-1]:
                        keyword = keyword[:] + '"'
            if len(keyword) <= 1:
                print(1 / 0)
        except:
            keyword = None
        source='国美'
        if type==None and brand==None and X_name==None:
            print('一条数据被过滤！')
            yield None
        else:
            item['shop_name'] = shop_name
            item['p_Name'] = p_Name
            item['X_name'] = X_name
            item['type'] = type
            item['price'] = price
            item['PreferentialPrice'] = PreferentialPrice
            item['brand'] = brand
            item['keyword'] = keyword
            item['PoorCount'] = PoorCount
            item['CommentCount'] = CommentCount
            item['GoodCount'] = GoodCount
            item['GeneralCount'] = GeneralCount
            item['GoodRateShow'] = GoodRateShow
            item['install'] = install
            item['drink'] = drink
            item['source'] = source
            item['level'] = level
            item['kinds'] = kinds
            item['life'] = life
            item['precision'] = precision
            item['color'] = color
            item['product_url'] = product_url
            item['ProductID'] = ProductID
            item['X_type'] = X_type
            yield item