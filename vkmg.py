#! /usr/bin/env python3


import config as conf
from src.VKMusicGetter import VKMusicGetter
from src.utils import valid_directory
from argparse import ArgumentParser


def main(args):
    if args.pauses:
        VKMusicGetter.pauses = True
    with VKMusicGetter(conf) as vkmg:
        vkmg.login()
        vkmg.get_tracks(
            target_vk_user_id=args.target_vk_user_id,
            number=args.number,
            tracks_dir=args.tracks_dir
        )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("target_vk_user_id",
        type=int,
        help="id of vk user whose tracklist to get"
    )
    parser.add_argument("-o",
        dest="tracks_dir",
        type=valid_directory,
        required=False,
        default="tracks",
        help="directory to save tracks to"
    )
    parser.add_argument("-n",
        dest="number",
        type=int,
        required=False,
        default=1,
        help="number of tracks to download"
    )
    parser.add_argument("-p",
        dest="pauses",
        action="store_true",
        required=False,
        default=False,
        help="enable pauses after functions completions")
    args = parser.parse_args()
    main(args)
