import os
import logging
import re
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
from urllib.parse import urlparse
from itemadapter import ItemAdapter
import json

BOT_NAME = 'samba_manuals'

SPIDER_MODULES = ['samba_manuals.spiders']
NEWSPIDER_MODULE = 'samba_manuals.spiders'

# Directory Settings
BASE_DIR = os.getcwd()
FILES_STORE = os.path.join(BASE_DIR, 'out/files')
IMAGES_STORE = os.path.join(BASE_DIR, 'out/images')
JSON_STORE = os.path.join(BASE_DIR, 'out/json')  # JSON file store
PDF_STORE = os.path.join(BASE_DIR, 'out/pdf')    # PDF file store
FORUM_POSTS_STORE = os.path.join(BASE_DIR, 'out/forum_posts')  # Forum posts store

# Export Settings
FEED_FORMAT = 'json'
FEED_URI = os.path.join(JSON_STORE, 'output.json')

# Bot and Request Settings
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 128
DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16
COOKIES_ENABLED = False

# Middleware Settings
SPIDER_MIDDLEWARES = {
   'samba_manuals.middlewares.SambaManualsSpiderMiddleware': 543,
}

DOWNLOADER_MIDDLEWARES = {
   'samba_manuals.middlewares.RotateUserAgentMiddleware': 110,
   'scrapy_deltafetch.DeltaFetch': 120,
   # 'scrapy_cdn_middleware.ProxyMiddleware': 700,  # Uncomment if needed
}

# User Agent List
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    # ... other user agents ...
]

# Custom Pipeline for saving files based on URL path
class CustomFilePipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None):
        url_parts = urlparse(request.url).path
        path_segments = url_parts.lstrip('/').split('/')
        file_name = os.path.basename(request.url)
        directory_path = os.path.join(*path_segments[:-1])
        full_path = os.path.join(directory_path, file_name)
        return full_path

# Custom Pipeline for saving images based on URL path
class CustomImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        url_parts = urlparse(request.url).path.lstrip('/').split('/')
        file_name = os.path.basename(request.url)
        directory_path = os.path.join(*url_parts[:-1])
        return os.path.join('images', directory_path, file_name)

# Custom Pipeline for exporting items as JSON
class JsonExportPipeline:
    def open_spider(self, spider):
        self.file = open(os.path.join(JSON_STORE, 'items.json'), 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

# Pipeline Settings
ITEM_PIPELINES = {
    'samba_manuals.pipelines.SambaManualsPipeline': 300,
    'samba_manuals.pipelines.CustomFilePipeline': 400,
    'samba_manuals.pipelines.CustomImagesPipeline': 200,
    'samba_manuals.pipelines.JsonExportPipeline': 500,
}
