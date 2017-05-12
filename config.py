import os


# VK domain name
VK_DOMAIN_NAME = "https://vk.com"


# VK user credentials
VK_USER_PHONE = os.environ.get("VK_USER_PHONE")
VK_USER_PASSWORD = os.environ.get("VK_USER_PASSWORD")


# ID of vk user whose audios are to be downloaded
VK_TARGET_ID = os.environ.get("VK_TARGET_ID")


# Browsermob-proxy binary path
BROWSERMOB_PROXY_BIN_PATH = os.environ.get("BROWSERMOB_PROXY_BIN_PATH")


# Firefox profile path
FIREFOX_PROFILE_PATH = os.environ.get("FIREFOX_PROFILE_PATH")
