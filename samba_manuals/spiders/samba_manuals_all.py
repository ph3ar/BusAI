import scrapy
from scrapy.loader import ItemLoader
from samba_manuals.items import SambaManualItem
import os
import json
import pdfkit
from urllib.parse import urljoin
from samba_manuals.custom_pipelines import CustomImagesPipeline  # Add this line
import re

class CombinedSambaManualsSpider(scrapy.Spider):
    name = 'combined_samba_manuals'
    allowed_domains = ['thesamba.com']
    start_urls = [
        'https://www.thesamba.com/vw/forum/login.php',
        'https://www.thesamba.com/vw/archives/manuals/type2.php',
        'https://www.thesamba.com/vw/archives/dic/index.php',
        'https://www.thesamba.com/vw/archives/info/tools1.php',
        'https://www.thesamba.com/vw/archives/info/',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=37',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=10',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=14',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=12',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=13',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=11',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=15',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=16',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=37',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=57',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=44',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=46',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=50',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=53',
        'https://www.thesamba.com/vw/forum/album_search.php?search_keywords=bus&search_forum%5B%5D=-1',
        'https://www.thesamba.com/vw/forum/search.php?search_keywords=bus&search_terms=all&search_author=&topic_starter=0&search_forum=5&search_fields=titleonly&show_results=topics&sort_by=0&sort_dir=DESC&return_chars=200',
        'https://www.thesamba.com/vw/forum/search.php?search_id=1605212941&start=4850',
    ]

    link_urls = [
        'https://www.thesamba.com/vw/links/cat.php?id=1',
        'https://www.thesamba.com/vw/links/cat.php?id=2',
        'https://www.thesamba.com/vw/links/cat.php?id=3',
        'https://www.thesamba.com/vw/links/cat.php?id=4',
        'https://www.thesamba.com/vw/links/cat.php?id=5',
        'https://www.thesamba.com/vw/links/cat.php?id=6',
        'https://www.thesamba.com/vw/links/cat.php?id=7',
        'https://www.thesamba.com/vw/links/cat.php?id=8',
        'https://www.thesamba.com/vw/links/cat.php?id=9',
        'https://www.thesamba.com/vw/links/cat.php?id=10',
        'https://www.thesamba.com/vw/links/cat.php?id=11',
        'https://www.thesamba.com/vw/links/cat.php?id=12',
        'https://www.thesamba.com/vw/links/cat.php?id=13',
        'https://www.thesamba.com/vw/links/cat.php?id=14',
        ]

    # Define login credentials
    username = os.environ.get('SAMBA_USERNAME', 'default_username')
    password = os.environ.get('SAMBA_PASSWORD', 'default_password')

    custom_settings = {
        'ITEM_PIPELINES': {
            # Include other pipelines if needed
            'samba_manuals.custom_pipelines.CustomImagesPipeline': 1,  # Use the custom pipeline
        }
    }

    def parse(self, response):
        # Check if the current URL is a login page
        if 'login.php' in response.url:
            yield scrapy.FormRequest(
                self.start_urls[3],  # Login URL
                formdata={
                    'username': self.username,
                    'password': self.password,
                },
                callback=self.after_login
            )
        else:
            # Continue with your scraping logic here
            # Example: Extracting vehicle type links
            for href in response.css('center a::attr(href)').getall():
                yield response.follow(href, callback=self.parse_vehicle_type)

    def parse_vehicle_type(self, response):
        # Check if the response content is text-based (e.g., HTML)
        content_type = response.headers.get('Content-Type', b'').decode('utf-8').lower()
        if 'text/html' in content_type:
            # Extracting individual manual links and following them
            for href in response.css('a[href$=".php"]::attr(href)').getall():
                yield response.follow(href, callback=self.parse_manual)
            next_page = response.css('a.next::attr(href)').get()  # Modify the selector as per your page's structure

            # Handling pagination
            pagination_links = response.css('div.pagination a::attr(href)').getall()
            current_page = response.url

            next_page = self.find_next_page(pagination_links, current_page)
            if next_page:
                yield response.follow(next_page, self.parse_vehicle_type)
        else:
            self.logger.warning(f"Ignoring non-text response with content type: {content_type}")


    def find_next_page(self, pagination_links, current_page):
        # Logic to determine the next page from pagination links
        for link in pagination_links:
            if self.is_next_link(link, current_page):
                return link
        return None

    def is_next_link(self, link, current_page):
        # Implement the logic to check if the link is the 'next' page link
        # Example logic here - needs to be tailored to the target website
        if 'next' in link or self.is_sequential_link(link, current_page):
            return True
        return False

    def is_sequential_link(self, link, current_page):
        # Additional logic to handle sequential links like page numbers or letter ranges
        # Example: Compare page numbers or letter ranges
        ...
        return False

    def after_login(self, response):
        # Check if login was successful based on a response check
        if 'Welcome back' in response.text:
            self.logger.info('Login successful!')
            # Continue with your scraping logic after login
            # Example: Making requests to other pages
            yield scrapy.Request('https://www.thesamba.com/vw/forum/index.php', callback=self.parse_forum)

    def convert_url_and_save_pdf(self, url):
        # Extract the query parameters using regular expressions
        match = re.search(r'\?t=(\d+)&', url)
        if match:
            topic_id = match.group(1)
            # Replace specific characters and format the new URL
            new_url = f'https://www.thesamba.com/vw/forum/archive/index.php/o-t--t-{topic_id}--.html'

            # Use pdfkit to save the page as a PDF
            pdf_file_name = f'topic_{topic_id}.pdf'  # Define the PDF file name
            pdfkit.from_url(new_url, pdf_file_name)

            return new_url, pdf_file_name
        else:
            return None, None  # URL format doesn't match

    def parse_manual(self, response):
        if response.status != 200:
            self.logger.error(f"Non-success status: {response.status} at {response.url}")
            return

        # Use a CSS selector to target the table element you want to scrape
        table = response.css('#table1')

        if not table:
            self.logger.warning(f"Expected table not found at {response.url}")
            return

        # Initialize lists to store PDF and JPG URLs
        pdf_urls = []
        jpg_urls = []

        # Iterate through table rows
        for row in table.css('tr')[1:]:
            item = SambaManualItem()
            item['page_url'] = response.url
            item['title'] = response.css('title::text').get(default='').strip()

            # Remove "_small" from image URLs
            item['image_urls'] = [
                response.urljoin(url.replace("_small", "")) 
                for url in response.css('img::attr(src)').getall()
            ]

            item['year'] = row.css('td:nth-child(1)::text').get(default='').strip()
            item['text_content'] = row.css('td:nth-child(2)::text').get(default='').strip()
            item['language'] = row.css('td:nth-child(3)::text').get(default='').strip()
            item['contributor'] = row.css('td:nth-child(4)::text').get(default='').strip()

            # Check for PDF and JPG links in the row and add them to the respective lists
            pdf_link = row.css('a[href$=".pdf"]::attr(href)').get()
        if pdf_link:
            pdf_urls.append(response.urljoin(pdf_link))

        jpg_link = row.css('a[href$=".jpg"]::attr(href)').get()
        if jpg_link:
            jpg_urls.append(response.urljoin(jpg_link))

        # Add the lists of PDF and JPG URLs to the item's 'file_urls' and 'image_urls' fields
        item['file_urls'] = pdf_urls + jpg_urls  # Combine both PDF and JPG URLs
        item['image_urls'] = jpg_urls  # Only JPG URLs in 'image_urls'

        yield item

    def parse_forum(self, response):
        for topic in response.css('.topictitle'):
            title = topic.css('a::text').get()

            # Check if the word "bus" is in the topic title
        if 'bus' in title.lower():
            topic_url = urljoin(response.url, topic.css('a::attr(href)').get())
            yield scrapy.Request(topic_url, callback=self.parse_forum_topic, meta={'title': title})

        # Check for pagination and follow next pages if available
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_forum)

    def parse_forum_topic(self, response):
        loader = ItemLoader(item=SambaManualItem(), response=response)
        loader.add_value('title', response.meta.get('title', ''))
        loader.add_css('author', '.postprofile a::text')
        loader.add_css('date', '.postdate::text')
        loader.add_css('image_urls', 'img::attr(src)')
        loader.add_css('content', '.content')
        loader.add_css('additional_content', '.postbody')

        # Save the current page as a PDF
        pdf_file_name = f"{response.meta['title'].replace(' ', '_')}.pdf"
        pdfkit.from_string(response.text, pdf_file_name)

        # Save data as JSON
        data = {
            'title': response.meta.get('title', ''),
            'author': loader.get_collected_values('author'),
            'date': loader.get_collected_values('date'),
            'content': loader.get_collected_values('content'),
            'additional_content': loader.get_collected_values('additional_content'),
            'image_urls': loader.get_collected_values('image_urls')
        }
        json_file_name = f"{response.meta['title'].replace(' ', '_')}.json"
        with open(json_file_name, 'w') as f:
            json.dump(data, f)

        yield loader.load_item()
