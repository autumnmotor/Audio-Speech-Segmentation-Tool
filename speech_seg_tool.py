import librosa
import pydub
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

# etc
parser.add_argument('--fade_duration',default=50) # msec
parser.add_argument('--remove_dc_offset',default=True)
parser.add_argument('--hpf_cutoff',default=80) # Hz
parser.add_argument('--compressor',default=True)
parser.add_argument('--head_room',default=0.1) # margin for normalize
parser.add_argument('--mono_channel',default=0) # 0: left 1: right 

# 機械学習にディザは良くないらしいので、今は機能しない（実装もない）。
dither = False
dither_amount = 0.5 # 0.0<->1.0 の範囲で設定する。　rand(-dither_amount, +dither_amount)


args = parser.parse_args()

filenames = [os.path.join(args.input_dir, x) for x in sorted(os.listdir(args.input_dir)) if not x.startswith(".")]
filelist = [file for file in filenames if os.path.isfile(file)]
filelist.sort()

def proc(audio_segment):

    if args.fade_duration > 0:
        audio_segment=audio_segment.fade_in(args.fade_duration).fade_out(args.fade_duration)

    if args.remove_dc_offset:
        audio_segment=audio_segment.remove_dc_offset()

    if args.hpf_cutoff > 0:
        audio_segment=effects.high_pass_filter(audio_segment, args.hpf_cutoff)

    if args.compressor:
        audio_segment=effects.compress_dynamic_range(audio_segment)

    if args.head_room > 0:
        audio_segment=effects.normalize(audio_segment, args.head_room)

    return audio_segment


for i in range(len(filelist)):

    file_path = filelist[i]
    print(f"try to load: {file_path}")

    try:
        audio, sr = librosa.load(file_path, sr=None)
    except Error:
        print(f"can't load {file_path}")
        continue
 
    basename=os.path.basename(file_path)

    audio_segment = AudioSegment.from_file(file_path)

    if args.mono_channel > 0:
        audio_segment=audio_segment.split_to_mono()[args.mono_channel]

    audio_segment=proc(audio_segment)

    # 音声ファイルの前後には空白（沈黙）があると仮定した処理を行う。そうでないと、先頭および末尾の無駄な空白を取り除けないため。
    silent=AudioSegment.silent(duration=args.min_silence_len) 
    audio_segment = silent + audio_segment + silent

    chunks = pydub.silence.split_on_silence(audio_segment,min_silence_len=args.min_silence_len, silence_thresh=args.silence_thresh,keep_silence=args.keep_silence)

    for j, chunk in enumerate(chunks):
        chunk=proc(chunk)
        chunk.export(f"{args.output_dir}/{basename}.{args.outfile_suffix}{j}.wav", format="wav")
        print(f"output: {args.output_dir}/{basename}.{args.outfile_suffix}{j}.wav")
