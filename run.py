import config as conf
from src.VKMusicGetter import VKMusicGetter
from argparse import ArgumentParser


if __name__ == "__main__":
    with VKMusicGetter(conf) as vkmg:
        vkmg.login()
