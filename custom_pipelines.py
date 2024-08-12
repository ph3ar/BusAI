from urllib.parse import urlparse
import os
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

