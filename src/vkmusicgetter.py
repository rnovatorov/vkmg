import logging
import os
import subprocess
from urllib.parse import urljoin
from tqdm import tqdm
from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from . import config
from .track import Track
from .exceptions import LoginFailedException, CannotProceedToAudiosException
from .utils import check_configs


class VkMusicGetter(object):
    """
    Allows to download music from vk
    """
    def __init__(self, tracks_dir):
        check_configs(config)
        self.init_logger()

        # Counting tracks
        self.tracks = []
        self.tracks_timed_out = []

        # Creating dir to download tracks to
        if not os.path.exists(tracks_dir):
            self.logger.info("Creating tracks_dir %s", tracks_dir)
            os.mkdir(tracks_dir)
        self.tracks_dir = tracks_dir

    def __enter__(self):
        self.start_up()
        return self

    def __exit__(self, *exc):
        self.tear_down()

    def start_up(self):
        self.logger.info("=== Starting up ===")
        self.init_browsermob()
        self.init_selenium()

    def tear_down(self):
        self.logger.info("=== Tearing down ===")
        self.driver.quit()
        self.server.stop()

    def get_tracks(self, target_vk_user_id, number):
        self.logger.info("Planning to get %d tracks from user %d track list",
                         number, target_vk_user_id)

        self.proceed_to_audios(target_vk_user_id)
        self.start_recording()
        self.press_play()

        # Looping over target's track list
        for _ in tqdm(range(number), total=number):
            current_track = self.get_current_track()
            self.tracks.append(current_track)

            if current_track.is_already_downloaded:
                self.logger.info("Already downloaded")
                self.start_recording()
                self.press_next()
                continue

            try:
                self.wait(config.WAIT_TRACKS_TIMEOUT).until(
                    lambda _: self.ready_to_download
                )
            except TimeoutException:
                self.logger.error("Timeout error while getting url for %s", current_track)
                self.tracks_timed_out.append(current_track)
            else:
                current_track.url = self.get_current_track_url()
                self.download_track(current_track)
            finally:
                self.start_recording()
                self.press_next()

        return self.tracks

    def wait(self, seconds):
        return WebDriverWait(self.driver, seconds)

    def download_track(self, track):
        performer_dir = os.path.join(self.tracks_dir, track.performer)
        if not os.path.exists(performer_dir):
            self.logger.info("Creating performer dir '%s'", performer_dir)
            os.mkdir(performer_dir)

        self.logger.info("Downloading %s", track)
        cmd = ["wget", track.url,
               "-O", track.path,
               "-a", os.path.join(config.LOG_DIR, "wget.log")]
        subprocess.Popen(cmd)

    def login(self):
        self.logger.info("Trying to log in")
        self.driver.get(config.VK_URL)
        try:
            self.wait(config.WAIT_ELEMENTS_LOCATION_TIMEOUT).until(
                lambda d: d.find_element_by_css_selector(config.VK_INDEX_LOGIN_FORM)
            )
        except TimeoutException:
            self.logger.exception("'%s' not found", config.VK_INDEX_LOGIN_FORM)
            raise

        # Login input
        try:
            login = self.driver.find_element_by_css_selector(config.VK_INDEX_LOGIN)
        except NoSuchElementException:
            self.logger.exception("'%s' not found", config.VK_INDEX_LOGIN)
            raise
        login.clear()
        login.send_keys(config.VK_USER_LOGIN)

        # Password input
        try:
            password = self.driver.find_element_by_css_selector(config.VK_INDEX_PASSWORD)
        except NoSuchElementException:
            self.logger.exception("'%s' not found", config.VK_INDEX_PASSWORD)
            raise
        password.clear()
        password.send_keys(config.VK_USER_PASSWORD)

        # Submitting
        try:
            login_button = self.driver.find_element_by_css_selector(config.VK_INDEX_LOGIN_BUTTON)
        except NoSuchElementException:
            self.logger.exception("'%s' not found", config.VK_INDEX_LOGIN_BUTTON)
            raise
        login_button.click()

        # Checking if login succeeded
        try:
            self.wait(config.WAIT_ELEMENTS_LOCATION_TIMEOUT).until(
                lambda d: d.find_element_by_css_selector(config.VK_LOGIN_ERROR)
            )
            self.logger.error("Login failed")
            raise LoginFailedException
        except TimeoutException:
            self.logger.info("Login succeeded")

    def init_browsermob(self):
        self.logger.info("Initing Browsermob")

        self.server = Server(config.BROWSERMOB_PROXY_BIN_PATH)
        self.server.start(options={"log_path": config.LOG_DIR})
        self.proxy = self.server.create_proxy()

    def init_selenium(self):
        self.logger.info("Initing Selenium")

        # Using custom Firefox profile with BrowserMob SSL cert
        profile = webdriver.FirefoxProfile(config.FIREFOX_PROFILE_PATH)
        profile.set_proxy(self.proxy.selenium_proxy())
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        self.driver = webdriver.Firefox(
            firefox_profile=profile,
            log_path=os.path.join(config.LOG_DIR, "geckodriver.log"),
            firefox_options=firefox_options
        )

    def init_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(config.LOG_LEVEL)

        formatter = logging.Formatter(config.LOG_FORMAT)
        fh = logging.FileHandler(os.path.join(config.LOG_DIR, "vkmg.log"))
        fh.setLevel(config.LOG_LEVEL)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def proceed_to_audios(self, target_vk_user_id):
        self.logger.info("Proceeding to user %d tracklist" % target_vk_user_id)
        url = urljoin(config.VK_URL, "audios%d" % target_vk_user_id)
        self.driver.get(url)
        if self.driver.current_url != url:
            raise CannotProceedToAudiosException(
                expected=url,
                got=self.driver.current_url
            )

    def press_play(self):
        try:
            play_button = self.driver.find_element_by_css_selector(config.VK_PLAYER_PLAY)
            play_button.click()
        except NoSuchElementException:
            self.logger.exception("'%s' not found" % config.VK_PLAYER_PLAY)
            raise

    def press_next(self):
        try:
            next_button = self.driver.find_element_by_css_selector(config.VK_PLAYER_NEXT)
            next_button.click()
        except NoSuchElementException:
            self.logger.exception("'%s' not found" % config.VK_PLAYER_NEXT)
            raise

    def get_current_track(self):
        performer_elem = self.driver.find_element_by_css_selector(
            config.VK_PLAYER_CURRENT_SONG_PERFORMER
        )
        performer = performer_elem.get_attribute("textContent")

        title_elem = self.driver.find_element_by_css_selector(
            config.VK_PLAYER_CURRENT_SONG_TITLE
        )
        title_with_hyphen = title_elem.get_attribute("textContent")
        title = title_with_hyphen[3:]

        track = Track(performer=performer, title=title, tracks_dir=self.tracks_dir)

        self.logger.info("Current track: %s" % track)
        return track

    def get_current_track_url(self):
        entries = self.proxy.har["log"]["entries"]
        if not entries:
            return None
        media = filter(lambda e: e["response"]["status"] == 206, entries)
        if not media:
            return None
        urls = [e["request"]["url"] for e in media]
        if not urls:
            return None
        return urls[-1]

    def start_recording(self):
        har_name = self.__class__.__name__
        self.proxy.new_har(har_name)

    @property
    def ready_to_download(self):
        return self.get_current_track_url() is not None
