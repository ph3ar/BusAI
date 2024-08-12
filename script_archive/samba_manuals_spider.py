# path/filename: samba_manuals/spiders/samba_manuals_spider.py

import scrapy
from samba_manuals.items import SambaManualItem

class SambaManualsSpider(scrapy.Spider):
    name = 'samba_manuals'
    allowed_domains = ['thesamba.com']
    start_urls = [
        'https://www.thesamba.com/vw/archives/manuals/type4.php',
        'https://www.thesamba.com/vw/forum/album_search.php?search_keywords=bus&search_forum%5B%5D=-1',
        'https://www.thesamba.com/vw/forum/search.php?search_keywords=bus&search_terms=all&search_author=&topic_starter=0&search_forum=5&search_fields=titleonly&show_results=topics&sort_by=0&sort_dir=DESC&return_chars=200'
    ]

    # Define your login credentials
    login_url = 'https://www.thesamba.com/vw/forum/login.php'
    username = 'bignerdlolz'
    password = 'As9kYLnEq6PVMN2u!!'

    def start_requests(self):
        # Start with a login request
        yield scrapy.Request(self.login_url, callback=self.login)

    def login(self, response):
        # Submit the login form with your credentials
        yield scrapy.FormRequest.from_response(
            response,
            formdata={'username': self.username, 'password': self.password},
            callback=self.after_login
        )

    def after_login(self, response):
        # Check if login was successful (you can customize this check)
        if "Welcome, {0}!".format(self.username) in response.text:
            self.logger.info("Login successful")
            # Now, continue with your original scraping logic
            for url in self.start_urls:
                yield scrapy.Request(url, callback=self.parse)
        else:
            self.logger.error("Login failed")
            # Handle the case where login failed, maybe raise an exception or exit

    def parse(self, response):
        # Your scraping logic remains the same
        for href in response.css('center a::attr(href)').getall():
            yield response.follow(href, callback=self.parse_vehicle_type)

    def parse_vehicle_type(self, response):
        # Extracting individual manual links and following them
        for href in response.css('a[href$=".php"]::attr(href)').getall():
            yield response.follow(href, callback=self.parse_manual)

    def parse_manual(self, response):
        if response.status != 200:
            self.logger.error(f"Non-success status: {response.status} at {response.url}")
            return

        if not response.css('#table1'):
            self.logger.warning(f"Expected table not found at {response.url}")
            # Implement alternative data extraction logic here or skip
            return

        for row in response.css('#table1 tr')[1:]:
            item = SambaManualItem()
            item['page_url'] = response.url
            item['title'] = response.css('title::text').get(default='').strip()
            item['image_urls'] = [response.urljoin(url) for url in response.css('img::attr(src)').getall()]

            item['year'] = row.css('td:nth-child(1)::text').get(default='').strip()
            item['text_content'] = row.css('td:nth-child(2)::text').get(default='').strip()
            item['language'] = row.css('td:nth-child(3)::text').get(default='').strip()
            item['contributor'] = row.css('td:nth-child(4)::text').get(default='').strip()

            yield item

