import subprocess
import json
import os

result = subprocess.run(["youtube-dl", "-f", "mp4", "https://www.youtube.com/watch?v=QintlPRNhHM", "--print-json"], stdout=subprocess.PIPE)

if result.returncode == 0:
    data = json.loads(result.stdout.decode("utf-8"))
    filename = data["_filename"]
    print("Video downloaded as `%s`" % filename)

    if not os.path.exists(filename.rstrip("mp4") + "json"):
        result = subprocess.run(["./subtool.py", filename], stdout=subprocess.PIPE)
        print(result.stdout.decode("utf-8"))
        print(result.returncode)
    else:
        print("Already subbed")