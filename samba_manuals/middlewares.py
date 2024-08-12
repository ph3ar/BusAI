import random
from scrapy import signals

class RotateUserAgentMiddleware:
    """Middleware to rotate user-agent for each request."""
    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        # Initialize the middleware with the user agent list from settings
        return cls(crawler.settings.get('USER_AGENT_LIST'))

    def process_request(self, request, spider):
        # Set a random user agent for each request
        request.headers.setdefault('User-Agent', random.choice(self.user_agents))

class SambaManualsSpiderMiddleware:
    """Custom spider middleware for the SambaManualsSpider."""
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        # Log a message when the spider is opened
        spider.logger.info('Spider opened: %s' % spider.name)

# Additional middlewares can be added here as needed
