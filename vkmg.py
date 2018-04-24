#! venv/bin/python3

import os
from pprint import pprint
from argparse import ArgumentParser
from src.utils import positive_int
from src.vkmg import VkMusicGetter


def main(args):
    print("Getting things ready...")
    with VkMusicGetter(tracks_dir=args.tracks_dir) as vkmg:
        print("Logging in...")
        vkmg.login()

        print("Starting download...")
        tracks = vkmg.get_tracks(
            target_vk_user_id=args.target_vk_user_id,
            number=args.number
        )

        print("Validating download...")
        tracks_not_downloaded = [
            track for track in tracks
            if not os.path.exists(track.path)
        ]

    n_tracks_not_downloaded = len(tracks_not_downloaded)
    n_tracks_downloaded = args.number - n_tracks_not_downloaded
    print("%d tracks were downloaded." % n_tracks_downloaded)
    if tracks_not_downloaded:
        print("%d tracks were NOT downloaded:" % n_tracks_not_downloaded)
        pprint(tracks_not_downloaded)


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "-t", "--target",
        dest="target_vk_user_id",
        type=int,
        required=True,
        help="id of vk user whose tracks to get"
    )
    arg_parser.add_argument(
        "-o", "--output",
        dest="tracks_dir",
        required=False,
        default="tracks",
        help="directory to save tracks to"
    )
    arg_parser.add_argument(
        "-n", "--number",
        dest="number",
        type=positive_int,
        required=False,
        default=10,
        help="number of tracks to get"
    )
    main(arg_parser.parse_args())
