import os
from pprint import pprint
from .vkmusicgetter import VkMusicGetter
from . import config


def get_tracks(tracks_dir, target_vk_user_id, number):
    try:
        with VkMusicGetter(tracks_dir=tracks_dir) as vkmg:
            print("Getting things ready...")
            vkmg.login()

            print("Starting download...")
            tracks = vkmg.get_tracks(
                target_vk_user_id=target_vk_user_id,
                number=number
            )
            print("Done")

            if vkmg.tracks_timed_out:
                print("The following tracks got timed out and were not downloaded:")
                pprint(vkmg.tracks_timed_out)

            tracks_not_downloaded = []
            for track in tracks:
                if not os.path.exists(track.path):
                    tracks_not_downloaded.append(track)
            if tracks_not_downloaded:
                print("The following tracks were not downloaded:")
                pprint(tracks_not_downloaded)

            if not (vkmg.tracks_timed_out or tracks_not_downloaded):
                print("All tracks were successfully downloaded")
    except Exception as e:
        print("Exception occurred: %s" % e)
        print("For details refer to %s/vkmg.log" % config.LOG_DIR)
