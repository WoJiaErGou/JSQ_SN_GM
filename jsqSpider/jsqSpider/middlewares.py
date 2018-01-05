from scrapy.exceptions import IgnoreRequest
from scrapy import signals
from jsqSpider.settings import suning_user_agent
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import random
import pandas as pd
class Exceptions(object):
    def __init__(self):
        self.errorlist=[]
        self.reason=[]

    @classmethod
    def from_crawler(cls, crawler):
        ex=cls()
        crawler.signals.connect(ex.spider_closed,signals.spider_closed)
        return ex
    def process_exception(self, request, exception, spider):
        print(exception)
        if request.url in self.errorlist:
            print('该URL已经存在！')
            raise IgnoreRequest
        else:
            self.errorlist.append(request.url)
            self.reason.append(exception)
            raise IgnoreRequest
    def spider_closed(self,spider):
        df=pd.DataFrame(columns=['url','reason'],index=None)
        df.url=self.errorlist
        df.reason=self.reason
        if self.errorlist:
            df.to_csv('error.csv',mode='w',index=None)
class SuningUseragentMiddleware(UserAgentMiddleware):
    '''
    设置User-Agent
    '''
    def process_request(self, request, spider):
        agent=random.choice(suning_user_agent)
        if agent:
            request.headers.setdefault('User-Agent',agent)