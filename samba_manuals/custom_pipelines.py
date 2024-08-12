import json
import os
import logging
from urllib.parse import urlparse
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

class CustomImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        # Customize the file path logic here
        url_parts = urlparse(request.url).path.lstrip('/').split('/')
        file_name = os.path.basename(request.url)
        directory_path = os.path.join(settings.get('IMAGES_STORE'), *url_parts[:-1])
        # Create directory if it doesn't exist
        os.makedirs(directory_path, exist_ok=True)
        return os.path.join(directory_path, file_name)

class SambaManualsPipeline:
    def open_spider(self, spider):
        # Set up logger
        self.logger = logging.getLogger(__name__)

    def close_spider(self, spider):
        # Close operations (if any)
        pass

    def process_item(self, item, spider):
        # Data cleaning and logging
        adapter = ItemAdapter(item)
        for field in adapter:
            if isinstance(adapter[field], str):
                adapter[field] = adapter[field].strip()
        self.logger.info(f"Item processed: {adapter.get('title')}")
        return item

class CustomFilePipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None):
        url_parts = urlparse(request.url).path
        path_segments = url_parts.lstrip('/').split('/')
        file_name = os.path.basename(request.url)
        directory_path = os.path.join(settings.get('FILES_STORE'), *path_segments[:-1])

        # Create directory if it doesn't exist
        os.makedirs(directory_path, exist_ok=True)

        return os.path.join(directory_path, file_name)

class JsonExportPipeline:
    def process_item(self, item, spider):
        url = item.get('page_url', '')
        url_parts = urlparse(url).path.lstrip('/').split('/')
        directory_path = os.path.join(settings.get('JSON_STORE'), *url_parts[:-1])

        # Create directory if it doesn't exist
        os.makedirs(directory_path, exist_ok=True)

        file_name = f"{url_parts[-1]}.json"
        file_path = os.path.join(directory_path, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
            file.write(line)
        return item
