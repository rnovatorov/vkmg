import os


# Browsermob-proxy binary path
BROWSERMOB_PROXY_BIN_PATH = os.environ.get("BROWSERMOB_PROXY_BIN_PATH")


# Firefox profile path
FIREFOX_PROFILE_PATH = os.environ.get("FIREFOX_PROFILE_PATH")


# VK main page url
VK_URL = "https://vk.com"


# VK user credentials
VK_USER_PHONE = os.environ.get("VK_USER_PHONE")
VK_USER_PASSWORD = os.environ.get("VK_USER_PASSWORD")


# ID of vk user whose audios are to be downloaded
VK_TARGET_ID = os.environ.get("VK_TARGET_ID")


# VK elements location
VK_INDEX_LOGIN = "index_email"
VK_INDEX_PASSWORD = "index_pass"
VK_INDEX_LOGIN_BUTTON = "index_login_button"
