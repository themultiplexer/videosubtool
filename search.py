import vlc
import argparse
import math
import time

parser = argparse.ArgumentParser(description='Convert speech audio to text using Google Speech API')
parser.add_argument('in_filename', help='Input filename (`-` for stdin)')
args = parser.parse_args()

Instance = vlc.Instance()
player = Instance.media_player_new()
media = Instance.media_new(args.in_filename)
media.add_option('start-time=120.0')
media.get_mrl()

player.set_media(media)
player.play()
time.sleep(10)
while player.is_playing():
    time.sleep(1)