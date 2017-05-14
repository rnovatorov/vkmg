import os
import logging
import subprocess
from .exceptions import LoginFailedException, CantProceedToAudiosException,\
                        ConfValueIsNoneException
from .utils import pause_on_complete
from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from urllib.parse import urljoin


class VKMusicGetter(object):
    """
    TODO: Add description
    """
    pauses = False

    def __init__(self, conf):
        # Configs
        self.check_configs(conf)
        self.conf = conf

        # Logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.conf.LOG_LEVEL)
        fh = logging.FileHandler(os.path.join(self.conf.LOG_DIR, "vkmg.log"))
        fh.setLevel(self.conf.LOG_LEVEL)
        formatter = logging.Formatter(self.conf.LOG_FORMAT)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def __enter__(self):
        self.start_up()
        return self

    def __exit__(self, *exc):
        self.tear_down()

    def start_up(self):
        self.logger.info("=== Starting up ===")
        self._init_browsermob()
        self._init_selenium()

    def tear_down(self):
        self.logger.info("=== Tearing down ===")
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
        attr_names = [an for an in dir(conf) if not an.startswith("__")]
        for an in attr_names:
            if getattr(conf, an) is None:
                raise ConfValueIsNoneException(an)
        return bool(conf)

    def get_tracks(self, target_vk_user_id, number, tracks_dir):
        self.logger.info("Getting %d tracks from user %d tracklist"
                          % (number, target_vk_user_id))
        self.proceed_to_audios(target_vk_user_id)

        har_name = self.__class__.__name__
        
        # Start recording
        self.proxy.new_har(har_name)

        # Triggering music player
        self.press_play()

        for _ in range(number):
            track_performer, track_title = self.get_track_name()
            try:
                self.wait.until(lambda _:
                    self.get_track_url(self.proxy.har) is not None
                )
            except TimeoutException:
                self.logger.error("Timeout error while getting url for track %s" % track_name)
            else:
                track_url = self.get_track_url(self.proxy.har)
                self.logger.debug("track_url: %s", track_url)
                self.download_track(track_url, tracks_dir, track_performer, track_title)
            finally:
                self.press_next()
                self.proxy.new_har(har_name)

    def download_track(self, track_url, tracks_dir, track_performer, track_title):
        performer_dir = os.path.join(tracks_dir, track_performer)
        if not os.path.exists(performer_dir):
            os.mkdir(performer_dir)
        cmd = ["wget", track_url, "-nv",
               "-O", os.path.join(performer_dir, "%s.mp3" % track_title),
               "-a", os.path.join(self.conf.LOG_DIR, "wget.log")]
        subprocess.Popen(cmd)

    @pause_on_complete(enable=lambda: VKMusicGetter.pauses)
    def login(self):
        self.logger.info("Trying to log in")
        self.driver.get(self.conf.VK_URL)
        try:
            self.wait.until(lambda d:
                d.find_element_by_css_selector(self.conf.VK_INDEX_LOGIN_FORM)
            )
        except TimeoutException:
            self.logger.error("'%s' not found" % self.conf.VK_INDEX_LOGIN_FORM)
            raise

        # Login input
        try:
            login = self.driver.find_element_by_css_selector(self.conf.VK_INDEX_LOGIN)
        except NoSuchElementException:
            self.logger.error("'%s' not found" % self.conf.VK_INDEX_LOGIN)
            raise
        login.clear()
        login.send_keys(self.conf.VK_USER_PHONE)

        # Password input
        try:
            password = self.driver.find_element_by_css_selector(self.conf.VK_INDEX_PASSWORD)
        except NoSuchElementException:
            self.logger.error("'%s' not found" % self.conf.VK_INDEX_PASSWORD)
            raise
        password.clear()
        password.send_keys(self.conf.VK_USER_PASSWORD)

        # Submitting
        try:
            login_button = self.driver.find_element_by_css_selector(self.conf.VK_INDEX_LOGIN_BUTTON)
        except NoSuchElementException:
            self.logger.error("'%s' not found" % self.conf.VK_INDEX_LOGIN_BUTTON)
            raise
        login_button.click()

        # Checking if login succeeded
        try:
            self.wait.until(lambda d:
                d.find_element_by_css_selector(self.conf.VK_LOGIN_ERROR)
            )
            self.logger.error("Login failed")
            raise LoginFailedException
        except TimeoutException:
            self.logger.info("Login succeeded")

    @pause_on_complete(enable=lambda: VKMusicGetter.pauses)
    def proceed_to_audios(self, target_vk_user_id):
        self.logger.info("Proceeding to user %d tracklist" % target_vk_user_id)
        url = urljoin(self.conf.VK_URL, "audios%d" % target_vk_user_id)
        self.driver.get(url)
        if self.driver.current_url != url:
            self.logger.error("Can not proceed to audios: instead of %s got %s"
                               % (url, self.driver.current_url))
            raise CantProceedToAudiosException

    @pause_on_complete(enable=lambda: VKMusicGetter.pauses)
    def press_play(self):
        try:
            play_button = self.driver.find_element_by_css_selector(self.conf.VK_PLAYER_PLAY)
            play_button.click()
        except NoSuchElementException:
            self.logger.error("'%s' not found" % self.conf.VK_PLAYER_PLAY)
            raise

    @pause_on_complete(enable=lambda: VKMusicGetter.pauses)
    def press_next(self):
        try:
            next_button = self.driver.find_element_by_css_selector(self.conf.VK_PLAYER_NEXT)
            next_button.click()
        except NoSuchElementException:
            self.logger.error("'%s' not found" % self.conf.VK_PLAYER_NEXT)
            raise

    @pause_on_complete(enable=lambda: VKMusicGetter.pauses)
    def get_track_name(self):
        performer_elem = self.driver.find_element_by_css_selector(
            self.conf.VK_PLAYER_CURRENT_SONG_PERFORMER
        )
        performer = performer_elem.get_attribute("textContent")
        self.logger.info("Performer: %s" % performer)
        title_elem = self.driver.find_element_by_css_selector(
            self.conf.VK_PLAYER_CURRENT_SONG_TITLE
        )
        title = title_elem.get_attribute("textContent")
        self.logger.info("Title: %s" % title)
        return performer, title[3:] # title[:3] == " - "

    @pause_on_complete(enable=lambda: VKMusicGetter.pauses)
    def get_track_url(self, har):
        entries = har["log"]["entries"]
        if not entries:
            return None
        media = filter(lambda e: e["response"]["status"] == 206, entries)
        if not media:
            return None
        urls = [e["request"]["url"] for e in media]
        if not urls:
            return None
        return urls[-1]
