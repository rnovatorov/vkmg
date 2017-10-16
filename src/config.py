import os
import logging


# Logging
LOG_LEVEL = logging.DEBUG
LOG_DIR = "log"
LOG_FORMAT = "%(asctime)s:%(name)s:%(levelname)s - %(message)s"

# Browsermob-proxy binary path
BROWSERMOB_PROXY_BIN_PATH = os.environ.get("BROWSERMOB_PROXY_BIN_PATH")

# Firefox profile path
FIREFOX_PROFILE_PATH = os.environ.get("FIREFOX_PROFILE_PATH")

# Webdriver wait time out
WEBDRIVER_WAIT_TIMEOUT = 30

# VK main page url
VK_URL = "https://vk.com"

# VK user credentials
VK_USER_PHONE = os.environ.get("VK_USER_PHONE")
VK_USER_PASSWORD = os.environ.get("VK_USER_PASSWORD")

# VK elements location (css selectors)
VK_INDEX_LOGIN_FORM = "#index_login_form"
VK_INDEX_LOGIN = "#index_email"
VK_INDEX_PASSWORD = "#index_pass"
VK_INDEX_LOGIN_BUTTON = "#index_login_button"
VK_LOGIN_ERROR = "#login_message .error"
VK_PLAYER_PLAY = ".audio_page_player_play"
VK_PLAYER_NEXT = ".audio_page_player_next"
VK_PLAYER_CURRENT_SONG_PERFORMER = ".audio_page_player_title_performer"
VK_PLAYER_CURRENT_SONG_TITLE = ".audio_page_player_title_song"
