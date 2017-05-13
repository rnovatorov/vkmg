import os
import logging
from .exceptions import LoginFailedException
# from pprint import pprint, pformat
from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from urllib.parse import urljoin


class VKMusicGetter(object):
    """
    TODO: Add description
    """
    def __init__(self, conf):
        # Logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Configs
        self.check_configs(conf)
        self.conf = conf

    def __enter__(self):
        self.start_up()
        return self

        # self.proxy.new_har("google")
        # self.driver.get("https://google.com")
        # pprint(self.proxy.har) # returns a HAR JSON blob

    def __exit__(self, *exc):
        self.tear_down()

    def start_up(self):
        self._init_browsermob()
        self._init_selenium()

    def tear_down(self):
        self.server.stop()
        self.driver.quit()

    def _init_browsermob(self):
        self.server = Server(self.conf.BROWSERMOB_PROXY_BIN_PATH)
        self.server.start(options={"log_path": self.conf.LOG_DIR})
        self.proxy = self.server.create_proxy()

    def _init_selenium(self):
        # Using custom Firefox profile with BrowserMob SSL cert
        profile = webdriver.FirefoxProfile(self.conf.FIREFOX_PROFILE_PATH)
        profile.set_proxy(self.proxy.selenium_proxy())
        self.driver = webdriver.Firefox(
            firefox_profile=profile,
            log_path=os.path.join(self.conf.LOG_DIR, "geckodriver.log")
        )
        self.wait = WebDriverWait(self.driver, self.conf.WEBDRIVER_WAIT_TIMEOUT)

    def check_configs(self, conf):
        """
        TODO: Add checking
        """
        return bool(conf)

    def login(self):
        self.driver.get(self.conf.VK_URL)

        # Login input
        try:
            login = self.driver.find_element_by_id(self.conf.VK_INDEX_LOGIN)
        except NoSuchElementException as e:
            self.logger.error("#%s not found" % self.conf.VK_INDEX_LOGIN)
            raise e
        login.clear()
        login.send_keys(self.conf.VK_USER_PHONE)

        # Password input
        try:
            password = self.driver.find_element_by_id(self.conf.VK_INDEX_PASSWORD)
        except NoSuchElementException as e:
            self.logger.error("#%s not found" % self.conf.VK_INDEX_PASSWORD)
            raise e
        password.clear()
        password.send_keys(self.conf.VK_USER_PASSWORD)

        # Submitting
        try:
            login_button = self.driver.find_element_by_id(self.conf.VK_INDEX_LOGIN_BUTTON)
        except NoSuchElementException as e:
            self.logger.error("#%s not found" % self.conf.VK_INDEX_LOGIN_BUTTON)
            raise e
        login_button.click()

        try:
            self.wait.until(lambda x:
                x.find_element_by_class_name("error")
            )
            self.logger.error("Login failed")
            raise LoginFailedException
        except TimeoutException:
            self.logger.info("Login succeeded")

        # Pausing
        input()

    def proceed_to_target_vk_user_audios(self, target_vk_user_id):
        url = urljoin(self.conf.VK_URL, "audios%d" % target_vk_user_id)
        self.driver.get(url)
