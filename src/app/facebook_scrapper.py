#!/usr/bin/python
# coding: utf-8
import logging

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# other necessary ones
import edgedriver_autoinstaller
import pandas as pd
import time
import sys
import os

IMAGES_TO_CONSIDER = 1


class FacebookScrapper(object):
    def __init__(self, ids, folder, depth=5, delay=2, lowres=False, highres=True):
        self.ids = ids
        self.folder = folder
        self.depth = depth + 1
        self.delay = delay
        self.posts = []
        self.photos = {}
        self.highres = highres
        self.lowres = lowres

        # set options as you wish
        self.options = Options()
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("start-maximized")
        self.options.add_argument("--disable-extensions")
        # self.options.add_argument("--headless")

        # setup Edge Driver
        self.browser = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=self.options)


    # def get_post_date(self, post):

        

    def collect_page(self, page):
        # navigate to page
        self.browser.get("https://www.facebook.com/" + page + "/")

        # Scroll down depth-times and wait delay seconds to load
        # between scrolls
        for scroll in range(self.depth):
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(self.delay)

        # once the full page is loaded, we can start scraping all posts
        logging.info("Scrapping displayed posts...")
        posts = self.browser.find_elements(By.XPATH, "//div[@class='x1ja2u2z xh8yej3 x1n2onr6 x1yztbdb']")
        logging.info("Analysing posts and extracting images...")
        for post in posts:
            self.extract_photos(post)


    def collect_groups(self, group):
        # navigate to page
        self.browser.get("https://www.facebook.com/groups/" + group + "/")

        # Scroll down depth-times and wait delay seconds to load
        # between scrolls
        for scroll in range(self.depth):
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(self.delay)

        # once the full page is loaded, we can start scraping all posts
        # to implement


    def collect(self, typ):
        if typ == "groups":
            for iden in self.ids:
                self.collect_groups(iden)
        elif typ == "pages":
            for iden in self.ids:
                self.collect_page(iden)


    def download(self):
        """
        Download low resolution and high resolution images from the post
        """
        for count, (id, urls) in enumerate(self.photos.items()):
            if self.lowres:
                lq_filename = id + "_lq.png"
                self.download_photo(url=urls[0], filename=os.path.join(self.folder, lq_filename))
            if self.highres:
                hq_filename = id + "_hq.png"
                self.download_photo(url=urls[1], filename=os.path.join(self.folder, hq_filename))


    def get_back(self):
        """
        Simulate a back action on browser.
        """
        self.browser.back()


    def login(self, email, password):
        try:

            self.browser.get("https://facebook.com")
            self.browser.maximize_window()
            self.wait = WebDriverWait(self.browser, 30)

            # open facebook and log in
            email_field = self.wait.until(EC.visibility_of_element_located((By.NAME, "email")))
            email_field.send_keys(email)
            pass_field = self.wait.until(EC.visibility_of_element_located((By.NAME, "pass")))
            pass_field.send_keys(password)
            pass_field.send_keys(Keys.RETURN)
            time.sleep(5)

        except Exception as e:
            logging.info("There was some error while logging in.")
            logging.info(sys.exc_info()[0])
            exit()


    def download_photo(self, url, filename):
        """
        Focus browser on image and extract the picture to disk using a Selenium Screenshot
        """
        self.browser.get(url)
        image = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//img[contains(@src, 'https://scontent-')]"))
        )

        # write image bytes to png file
        with open(filename, "wb") as file:
            logging.info("Created: " + filename)
            file.write(image.screenshot_as_png)
        time.sleep(0.25)


    def extract_photos(self, post):
        """
        Parse facebook post page looking for specific posts.
        Research is based on current FB ids generated from the page. Future FB updates might break this logic.
        Count the number of images per post and work only on those with one.
        Parse the post to get image LQ link (img) and HQ link (a href)
        """
        # get links related to FB images - HQ URL
        links = post.find_elements(
            By.XPATH, ".//a[@role='link' and contains(@href, 'https://www.facebook.com/photo/?fbid=')]"
        )

        if not len(links):
            logging.info(post.id + " : No images to parse !")

        elif len(links) > IMAGES_TO_CONSIDER:
            logging.info(post.id + " : Too many images ! Low probability of candidate post !")

        else:
            logging.info(post.id + " : Fetching " + str(len(links)) + " image(s)")
            # for each link, parse the related image
            for count, link in enumerate(links):
                img_id = post.id + "_" + link.id
                img_hq_url = link.get_attribute("href")
                images = link.find_elements(By.XPATH, ".//img[contains(@src, 'https://scontent-')]")

                # can skip lowres
                for count, image in enumerate(images):
                    # get low resolution url
                    img_lq_url = image.get_attribute("src")
                    self.photos[img_id] = [img_lq_url, img_hq_url]


    def close_and_quit(self):
        """
        Close current browser page and quit browser instance
        """
        self.browser.close()
        self.browser.quit()
