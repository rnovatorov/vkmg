import config as conf
from pprint import pprint
from argparse import ArgumentParser
from browsermobproxy import Server
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import urljoin


class VKMusicGetter(object):
    """
    """
    def __init__(self, conf):
        # Configs
        self.conf = conf

        # Initialising Browsermob
        self.server = Server(self.conf.BROWSERMOB_PROXY_BIN_PATH)
        self.server.start()
        self.proxy = self.server.create_proxy()

        # Setting up Selenium, using custom profile
        profile = webdriver.FirefoxProfile(self.conf.FIREFOX_PROFILE_PATH)
        profile.set_proxy(self.proxy.selenium_proxy())
        self.driver = webdriver.Firefox(firefox_profile=profile)

        # self.proxy.new_har("google")
        # self.driver.get("https://google.com")
        # pprint(self.proxy.har) # returns a HAR JSON blob

    def tear_down(self):
        """
        Closing Browsermob server and Selenium webdriver
        """
        self.server.stop()
        self.driver.quit()

    def login(self):
        self.driver.get(self.conf.VK_URL)

        # Login input
        try:
            login = self.driver.find_element_by_id(self.conf.VK_INDEX_LOGIN)
        except NoSuchElementException:
            print("#%s not found" % self.conf.VK_INDEX_LOGIN)
        login.clear()
        login.send_keys(self.conf.VK_USER_PHONE)

        # Password input
        try:
            password = self.driver.find_element_by_id(self.conf.VK_INDEX_PASSWORD)
        except NoSuchElementException:
            print("#%s not found" % self.conf.VK_INDEX_PASSWORD)
        password.clear()
        password.send_keys(self.conf.VK_USER_PASSWORD)

        # Submitting
        try:
            login_button = self.driver.find_element_by_id(self.conf.VK_INDEX_LOGIN_BUTTON)
        except NoSuchElementException:
            print("#%s not found" % self.conf.VK_INDEX_LOGIN_BUTTON)
        login_button.click()

    def proceed_to_target_vk_user_audios(self, target_vk_user_id):
        url = urljoin(self.conf.VK_URL, "audios%d" % target_vk_user_id)
        self.driver.get(url)


if __name__ == "__main__":
    vkmg = VKMusicGetter(conf)
    vkmg.login()
