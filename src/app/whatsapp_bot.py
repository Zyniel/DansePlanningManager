import logging
import time
import sys

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import TimeoutException


class WhatsappBot(object):
    def __init__(self, config):
        self.config = config

        # set options as you wish
        self.options = Options()
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("start-maximized")
        self.options.add_argument("--disable-extensions")
        if self.config.user_dir_folder:
            self.options.add_argument("--user-data-dir=" + self.config.user_dir_folder)

        # setup Edge Driver
        self.browser = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=self.options)

    def send_message(self, to, message=""):
        # identify contact / group
        name_argument = f"//span[contains(@title,'{to}')]"
        title = self.wait.until(EC.presence_of_element_located((By.XPATH, name_argument)))
        title.click()

        # many a times class name or other HTML properties changes so keep a track of current class name for input box by using inspect elements
        input_path = '//*[@id="main"]/footer//p[@class="selectable-text copyable-text"]'
        box = self.wait.until(EC.presence_of_element_located((By.XPATH, input_path)))
        # wait for security
        time.sleep(1)
        # send your message followed by an Enter
        box.send_keys(message + Keys.ENTER)
        # wait for security
        time.sleep(2)

    def get_back(self):
        """
        Simulate a back action on browser.
        """
        self.browser.back()

    def login(self):
        try:

            self.browser.get("https://web.whatsapp.com/")
            self.browser.maximize_window()
            self.wait = WebDriverWait(driver=self.browser, timeout=900)

            # wait 5s until leanding page displays
            try : 
                landing = WebDriverWait(driver=self.browser, timeout=20).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="landing-main"]'))
                )
                if landing:
                    print("Scan QR Code, And then Enter")
                    input()
                    print("Logged In")                
            except TimeoutException as e:
                print("No need to authenticate !")

        except Exception as e:
            logging.info("There was some error while logging in.")
            logging.info(sys.exc_info()[0])
            exit()

    def close_and_quit(self):
        """
        Close current browser page and quit browser instance
        """
        self.browser.close()
        self.browser.quit()
