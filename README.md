# Video Subtool

Add subtitles to video by feeding audio to vosk and resulting text into (soft-)subtitled mkv.
All spoken words are extracted into a json file for further processing, like searching in a subtitled video.

## Requirements

Packages
- ffmpeg-python
- vosk

Download e.g. german from  and rename folder to **model**.

### Generating Subtitles / Extracting Words

`subtool.py <input_video_filename>`

Outputs:
- **<input_video_filename>.mkv** - Video with subtitles
- **<input_video_filename>.json** - List of sspoken words with timestamp and accuracy of detected words (directly from vosk)
- **<input_video_filename>.ass** - Subtitles in *SubStation Alpha* Format
- **output.wav** - Temporary Audio file
