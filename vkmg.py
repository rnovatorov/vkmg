#! venv/bin/python3


from src.vkmusicgetter import VkMusicGetter
from argparse import ArgumentParser


def main(args):
    with VkMusicGetter(tracks_dir=args.tracks_dir) as vkmg:
        vkmg.login()
        vkmg.get_tracks(
            target_vk_user_id=args.target_vk_user_id,
            number=args.number
        )


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
        type=int,
        required=False,
        default=3,
        help="number of tracks to get"
    )
    main(arg_parser.parse_args())
