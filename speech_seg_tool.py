
import pydub
import noisereduce as nr
import voicefixer as vf

import numpy as np
import array

from pydub import AudioSegment
from pydub import effects
import os
import argparse

save_ext="flac"

voicefixer = vf.VoiceFixer()

parser = argparse.ArgumentParser(description='Audio Speech Segmentation Tool for RVC')

# filepath
parser.add_argument('--input_dir', default="input")
parser.add_argument('--output_dir',default="output")

# split silent
parser.add_argument('--min_silence_len',default=300)
parser.add_argument('--silence_thresh',default=-30)
parser.add_argument('--keep_silence',default=50)
parser.add_argument('--seek_step',default=5)

# etc
parser.add_argument('--fade_duration',default=50) # msec
parser.add_argument('--remove_dc_offset',default=True)
parser.add_argument('--hpf_cutoff',default=80) # Hz
parser.add_argument('--head_room',default=0.1) # margin for normalize
parser.add_argument('--mono_channel',default=1) # 1: left 2: right 
parser.add_argument('--voicefixer',default=0) # mode
parser.add_argument('--noisereduce',default=0.1)

args = parser.parse_args()

filenames = [os.path.join(args.input_dir, x) for x in sorted(os.listdir(args.input_dir)) if not x.startswith(".")]
filelist = [file for file in filenames if os.path.isfile(file)]
filelist.sort()

def proc(audio_segment):

    if args.remove_dc_offset:
        print("remove_dc_offset")
        audio_segment=audio_segment.remove_dc_offset()

    if args.hpf_cutoff > 0:
        print("hpf")
        audio_segment=effects.high_pass_filter(audio_segment, args.hpf_cutoff)

    data = np.array(audio_segment.get_array_of_samples(), dtype=np.int32) 

    if args.noisereduce > 0:
        print("noisereduce")
        data=nr.reduce_noise(y=data, sr=audio_segment.frame_rate, prop_decrease=args.noisereduce)

    if args.head_room > 0:
        print("normalize")
        data = data.astype(np.float32) * (10 ** (-args.head_room / 20) * np.iinfo(data.dtype).max / data.max()) # normalize with headroom

    audio_segment = audio_segment._spawn(array.array(audio_segment.array_type, data.astype(audio_segment.array_type)))

    if args.fade_duration > 0:
        print("fadein/out")
        audio_segment=audio_segment.fade_in(args.fade_duration).fade_out(args.fade_duration)


    return audio_segment



for i in range(len(filelist)):

    file_path = filelist[i]

    basename=os.path.basename(file_path)
    audio_segment = None

    try:
        if args.voicefixer >= 0:
            print("voicefixer")
            voicefixer.restore(input=file_path,
                        output=file_path+"."+save_ext,
                        cuda=False, # GPU acceleration
                        mode=args.voicefixer)
            print("fixed")
            audio_segment = AudioSegment.from_file(file_path+"."+save_ext)
            os.remove(file_path+"."+save_ext)
        else:
            audio_segment = AudioSegment.from_file(file_path)

        print(f"load: {file_path}")
    except Exception as e:
        print(f"can't load {file_path} :{e}")
        continue

    # to mono
    if args.mono_channel > 0:
        if args.mono_channel==1: # left
            audio_segment=audio_segment.pan(-1.0)
        elif args.mono_channel==2: # right
            audio_segment=audio_segment.pan(+1.0)
    
    audio_segment=audio_segment.set_channels(1)

    # 音声ファイルの前後には空白（沈黙）があると仮定した処理を行う。そうでないと、先頭および末尾の無駄な空白を取り除けないため。
    silent=AudioSegment.silent(duration=args.min_silence_len) 
    audio_segment = silent + audio_segment + silent

    # convert 2**4=32bit for signal proccessing with precision
    audio_segment=audio_segment.set_sample_width(4) 

    audio_segment=proc(audio_segment)

    chunks = pydub.silence.split_on_silence(audio_segment,min_silence_len=args.min_silence_len, silence_thresh=args.silence_thresh,keep_silence=args.keep_silence, seek_step=args.seek_step)

    for j, chunk in enumerate(chunks):
        chunk=proc(chunk)
        chunk.export( f"{args.output_dir}/{basename}_{j}.{save_ext}", format=save_ext)
        print(f"output: {args.output_dir}/{basename}_{j}.{save_ext}")
