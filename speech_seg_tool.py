
import pydub
import noisereduce as nr
import numpy as np
import array

from pydub import AudioSegment
from pydub import effects
import os
import argparse

parser = argparse.ArgumentParser(description='Audio Speech Segmentation Tool for RVC')

# filepath
parser.add_argument('--input_dir', default="input")
parser.add_argument('--output_dir',default="output")
parser.add_argument('--outfile_suffix',default="segment_")

# split silent
parser.add_argument('--min_silence_len',default=300)
parser.add_argument('--silence_thresh',default=-30)
parser.add_argument('--keep_silence',default=50)
parser.add_argument('--seek_step',default=5)

# etc
parser.add_argument('--fade_duration',default=50) # msec
parser.add_argument('--remove_dc_offset',default=True)
parser.add_argument('--hpf_cutoff',default=80) # Hz
parser.add_argument('--compressor',default=2.0)
parser.add_argument('--noise_reduction',default=0.3)
parser.add_argument('--head_room',default=0.1) # margin for normalize
parser.add_argument('--mono_channel',default=1) # 1: left 2: right 

# 機械学習にディザは良くないらしいので、今は機能しない（実装もない）。
dither = False
dither_amount = 0.5 # 0.0<->1.0 の範囲で設定する。　rand(-dither_amount, +dither_amount)

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

    if args.compressor > 1.0:
        print("comp")
        audio_segment=effects.compress_dynamic_range(audio_segment, ratio=args.compressor)

    data = np.array(audio_segment.get_array_of_samples(), dtype=np.int32) 

    if args.noise_reduction > 0:
        print("noise reduction")
        data=nr.reduce_noise(y=data, sr=audio_segment.frame_rate, prop_decrease=args.noise_reduction)

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
        audio_segment = AudioSegment.from_file(file_path)
        print(f" load: {file_path}")
    except Exception:
        print(f"can't load {file_path}")
        continue

    # to mono
    if args.mono_channel > 0:
        if args.mono_channel==1: # left
            audio_segment=audio_segment.split_to_mono()[0]
        elif args.mono_channel==2: # right
            audio_segment=audio_segment.split_to_mono()[1]
        else:
            audio_segment=audio_segment.set_channel(1) # bad quality...

    # 音声ファイルの前後には空白（沈黙）があると仮定した処理を行う。そうでないと、先頭および末尾の無駄な空白を取り除けないため。
    silent=AudioSegment.silent(duration=args.min_silence_len) 
    audio_segment = silent + audio_segment + silent

    # convert 32bit for signal proccessing with precision
    audio_segment=audio_segment.set_sample_width(4) 

    audio_segment=proc(audio_segment)

    chunks = pydub.silence.split_on_silence(audio_segment,min_silence_len=args.min_silence_len, silence_thresh=args.silence_thresh,keep_silence=args.keep_silence, seek_step=args.seek_step)

    for j, chunk in enumerate(chunks):
        chunk=proc(chunk)
        chunk.export(f"{args.output_dir}/{basename}.{args.outfile_suffix}{j}.wav", format="wav")
        print(f"output: {args.output_dir}/{basename}.{args.outfile_suffix}{j}.wav")
