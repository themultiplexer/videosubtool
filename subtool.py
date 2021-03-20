#!/usr/bin/env python
from __future__ import unicode_literals, print_function
import argparse
import ffmpeg
import logging
import sys
from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import wave, json
from datetime import datetime
import contextlib

SetLogLevel(0)

if not os.path.exists("model"):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    exit(1)


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


parser = argparse.ArgumentParser(description='Add subtitles to video by feeding audio to vosk and resulting text into (soft-)subtitled mkv. (And extract words into json for further processing)')
parser.add_argument('in_filename', help='Input filename (`-` for stdin)')


def decode_audio(in_filename, out_filename, **input_kwargs):
    try:
        out, err = (ffmpeg
            .input(in_filename, **input_kwargs)
            .output(out_filename, acodec='pcm_s16le', ac=1, ar='44100')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    return out_filename

def insert_subs(in_filename, subs_filename):
    out_filename = in_filename.split(".")[0] + "-subbed.mkv"
    try:
        stream = (ffmpeg
            .input(subs_filename, i=in_filename)
            .output(out_filename, codec='copy', map=['0', '1'])
            .overwrite_output())
        print(" ".join(stream.get_args()))
        out, err = stream.run(capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    return out

def convtime(seconds):
    return datetime.utcfromtimestamp(seconds).strftime('%H:%M:%S,%f')[:-3]

def get_transcripts(video_filename, audio_filename):
    debug = False

    sub_filename = video_filename.split(".")[0] + ".ass"
    json_filename = video_filename.split(".")[0] + ".json"
    test = open(sub_filename, "w")

    wf = wave.open(audio_filename, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        exit(1)

    frames = wf.getnframes()
    rate = wf.getframerate()
    duration = frames / float(rate)

    model = Model("model")
    rec = KaldiRecognizer(model, wf.getframerate())

    i = 0
    words = []

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            data = json.loads(rec.Result())
            if "result" in data:
                words = words + data["result"]
                print('{0:.3f}% in audio time'.format((float(data["result"][-1]["end"]) / duration) * 100, 3), end='\r')
                test.write(str(i) + "\n")
                test.write(convtime(data["result"][0]["start"]) + " --> " + convtime(data["result"][-1]["end"]) + "\n")
                test.write(data["text"] + "\n\n")
                i += 1
        elif debug == True:
            print(rec.PartialResult())

    with open(json_filename, 'w') as f:
        json.dump(words, f)

    test.close()
    insert_subs(video_filename, sub_filename)


def transcribe(video_filename):
    audio_filename = decode_audio(video_filename, "output.wav")
    transcripts = get_transcripts(video_filename, audio_filename)


if __name__ == '__main__':
    args = parser.parse_args()
    transcribe(args.in_filename)

