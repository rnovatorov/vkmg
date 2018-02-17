#! venv/bin/python3


import os
from pprint import pprint
from argparse import ArgumentParser
from src.utils import posint
from src.vkmusicgetter import VkMusicGetter


def main(args):
    average_song_size_mb = 4
    approximate_size_gb = (args.number * average_song_size_mb) / 1024
    print("%d tracks on average will take %.2f GB."
          % (args.number, approximate_size_gb))

    print("Getting things ready...")
    with VkMusicGetter(tracks_dir=args.tracks_dir) as vkmg:
        print("Logging in...")
        vkmg.login()

        print("Starting download...")
        tracks = vkmg.get_tracks(
            target_vk_user_id=args.target_vk_user_id,
            number=args.number
        )

        tracks_not_downloaded = [
            track for track in tracks
            if not os.path.exists(track.path)
        ]

    if tracks_not_downloaded:
        print("The following tracks were not downloaded:")
        pprint(tracks_not_downloaded)
    else:
        print("All tracks were successfully downloaded.")


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
        type=posint,
        required=False,
        default=3,
        help="number of tracks to get"
    )
    main(arg_parser.parse_args())
