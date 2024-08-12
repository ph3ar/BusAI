import scrapy
from urllib.parse import urljoin
from samba_manuals.items import SambaManualItem
import os
import logging
import re
import pdfkit


class CombinedSambaManualsSpider(scrapy.Spider):
    name = 'combined_samba_manuals_latest'
    allowed_domains = ['thesamba.com']
    start_urls = [
        'https://www.thesamba.com/vw/archives/manuals/type4.php',
        'https://www.thesamba.com/vw/forum/album_cat.php?cat_id=37',
        'https://www.thesamba.com/vw/forum/album_search.php?search_keywords=bus&search_forum%5B%5D=-1',
        'https://www.thesamba.com/vw/forum/search.php?search_keywords=bus&search_terms=all&search_author=&topic_starter=0&search_forum=5&search_fields=titleonly&show_results=topics&sort_by=0&sort_dir=DESC&return_chars=200',
        'https://www.thesamba.com/vw/forum/login.php',
        'https://www.thesamba.com/vw/forum/search.php?search_id=1605212941&start=4850',  # New URL
    ]

    # Define login credentials
    username = 'bignerdlolz'
    password = 'As9kYLnEq6PVMN2u!!'

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
        """
        Parse the vehicle type page and extract individual manual links.

        Args:
            response (scrapy.Response): The response from the vehicle type page.

        Returns:
            None
        """
        # Your existing parse_vehicle_type logic here
        pass

    def after_login(self, response):
        """
        Handle actions to be performed after a successful login.

        Args:
            response (scrapy.Response): The response after the login attempt.

        Returns:
            None
        """
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
            # Implement alternative data extraction logic here or skip
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
                response.urljoin(url.replace("_small", ""))  # Remove "_small" from URL
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
        # Implement your scraping logic for the forum here
        for topic in response.css('.topictitle'):
            title = topic.css('a::text').get()
            topic_url = response.urljoin(topic.css('a::attr(href)').get())

            # Extract additional data from the topic pages
            yield scrapy.Request(topic_url, callback=self.parse_forum_topic, meta={'title': title})

        # Check for pagination and follow next pages if available
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_forum)

    def parse_forum_topic(self, response):
        # Extract more data from forum topics
        title = response.meta.get('title', '')
        author = response.css('.postprofile a::text').get()
        date = response.css('.postdate::text').get()

        # Extract images
        image_urls = response.css('img::attr(src)').getall()
        image_urls = [response.urljoin(url) for url in image_urls]

        # Extract text content
        content = response.css('.content').get()

        # Extract additional text content
        additional_content = response.css('.postbody').get()

        yield {
            'title': title,
            'author': author,
            'date': date,
            'image_urls': image_urls,
            'content': content,
            'additional_content': additional_content,  # Include the additional text content
            # Add more fields as needed
        }
