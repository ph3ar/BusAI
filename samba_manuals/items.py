import scrapy

class SambaManualItem(scrapy.Item):
    # Define the fields for your item here
    title = scrapy.Field()  # Title or name of the manual or image
    page_url = scrapy.Field()  # URL of the page where the item was found
    image_urls = scrapy.Field()  # List of image URLs to download
    images = scrapy.Field()  # Information about downloaded images
    file_urls = scrapy.Field()  # List of file URLs to download (PDFs, docs, etc.)
    files = scrapy.Field()  # Information about downloaded files
    text_content = scrapy.Field()  # Text content scraped from the page
    language = scrapy.Field()  # Language of the manual or text
    contributor = scrapy.Field()  # Contributor's name or source
    year = scrapy.Field()  # Year of publication or relevant year
    # Additional fields can be added as needed

