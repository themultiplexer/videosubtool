import json
import pandas as pd
import ffmpeg
import argparse
import math

parser = argparse.ArgumentParser(description='Create video with by cutting out words and pasting them to a sentence')
parser.add_argument('in_filename', help='Input filename (`-` for stdin)')
parser.add_argument('query', help='Input word sequence (`-` for stdin)', nargs='?')
parser.add_argument('--best', help='Input word sequence (`-` for stdin)', action='store_true')
parser.add_argument('--worst', help='Input word sequence (`-` for stdin)', action='store_true')

def cut(filename, times):
    in_file = ffmpeg.input(filename)

    vid = in_file.video.filter_multi_output('split')
    aud = in_file.audio.filter_multi_output('asplit')

    print(len(times))
    outs = []

    for i in range(len(times)):
        s = times[i][0]
        e = times[i][1]

        outs.extend((vid[i].trim(start=s, end=e).setpts('PTS-STARTPTS'),
                     aud[i].filter_('atrim', start=s, end=e).filter_('asetpts', 'PTS-STARTPTS')))

    joined = ffmpeg.concat(*outs, v=1, a=1).node
    output = ffmpeg.output(joined[0], joined[1], 'out.mp4')
    #print(" ".join(output.get_args()))
    output.run()


args = parser.parse_args()

json_filename = args.in_filename.split(".")[0] + ".json"
words = pd.read_json(json_filename)
words["len"] = words["end"] - words["start"]
lofw = words.drop_duplicates(subset=['word']).sort_values(["word"], inplace = False, ascending=[True])["word"].to_list()
f = open("listofwords.txt", "w")
f.write("\n".join(lofw))
f.close()
words.sort_values(["conf", "len"], inplace = True, ascending=[False, False])

if args.query is not None:
    print("Constructing sentence: \"%s\"" % args.query)

    times = []
    for req_word in args.query.lower().split(" "):
        tword = req_word.rstrip("-")
        trailingrem = (len(req_word) - len(tword)) * 0.07

        lword = tword.lstrip("-")
        leadingrem = (len(tword) - len(lword)) * 0.07
        
        word = lword
        matches = words.loc[words["word"]==word]
        
        if matches.size > 0:
            match = matches.iloc[0]
            trailtime = trailingrem * match.len
            leadtime = leadingrem * match.len
            times.append((match.start + leadtime, match.end - trailtime))
            words.drop(match.name, inplace=True)

    print(times)
    cut(args.in_filename, times)
elif args.best:
    top = list(words.head(30)[["start", "end"]].to_records(index=False))
    print(top)
    cut(args.in_filename, top)
elif args.worst:
    bottom = list(words.tail(30)[["start", "end"]].to_records(index=False))
    print(bottom)
    cut(args.in_filename, bottom)
else:
    print("Use either --best, --worst or own query.")