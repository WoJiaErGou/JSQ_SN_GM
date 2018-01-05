from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import random
from GM_jsqSpider.settings import GM_user_agent
class GM_user(UserAgentMiddleware):
    def process_request(self, request, spider):
        agent=random.choice(GM_user_agent)
        if agent:
            request.headers.setdefault('User-Agent',agent)