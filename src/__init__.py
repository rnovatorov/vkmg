import os
from pprint import pprint
from .vkmusicgetter import VkMusicGetter
from . import config


def get_tracks(tracks_dir, target_vk_user_id, number):
    # Approximating size
    average_song_size_mb = 4
    approximate_size_gb = (number * average_song_size_mb) / 1024
    print("%d tracks on average will take %.2f GB." % (number, approximate_size_gb))

    try:
        print("Getting things ready...")
        with VkMusicGetter(tracks_dir=tracks_dir) as vkmg:
            print("Logging in...")
            vkmg.login()

            print("Starting download...")
            tracks = vkmg.get_tracks(
                target_vk_user_id=target_vk_user_id,
                number=number
            )

            tracks_not_downloaded = []
            for track in tracks:
                if not os.path.exists(track.path):
                    tracks_not_downloaded.append(track)
    except Exception as e:
        print("Exception occurred: %s" % e)
        print("For details refer to %s/vkmg.log" % config.LOG_DIR)
    else:
        if tracks_not_downloaded:
            print("The following tracks were not downloaded:")
            pprint(tracks_not_downloaded)
        else:
            print("All tracks were successfully downloaded.")
