# Audio Speech Segmentation Tool for RVC
RVCのための音声スピーチセグメンテーションツール

## これって何
このPythonスクリプトは[RVC](https://github.com/liujing04/Retrieval-based-Voice-Conversion-WebUI)のための
オーディオファイル群を分割、整音するツールです。

## 使い方
python環境に、ソースの冒頭にあるライブラリ、librosa, pydubをインストールして使用してください。

`pip install librosa`

`pip install pydub`

`python speech_seg_tool.py`

## パラメータの説明
### ファイル関連

| パラメータ名 | 説明 | デフォルトの値 |
| :-- | :-: | --: |
| --input_dir | 入力ディレクトリ。ここにオーディオファイル群を入れます。 | input |
| --output_dir | 出力ディレクトリ。ここに分割等各種処理されたオーディオファイル群が格納されます。自動的に作らないので注意。 | output |
| --outfile_suffix | 出力ファイルの接尾辞です。 | segment_ |

### 区間分割関連。[pydubのドキュメント](https://github.com/jiaaro/pydub/blob/master/API.markdown)も見よ。

| パラメータ名 | 説明 | 単位 | デフォルトの値 |
| :-- | :-: | :-: | --: |
| --min_silence_len | 無音とみなす最小の期間。 | msec | 300 |
| --silence_thresh | 無音の閾値 | dBFS | -30 |
| --keep_silence| 無音期間をどれくらい残すか。 | msec、あるいはTrue（全部残す）, False(全部残さない) | 50 |


### その他各種処理関連。こちらも[pydubのドキュメント](https://github.com/jiaaro/pydub/blob/master/API.markdown)と[pydub.effectsのソース](https://github.com/jiaaro/pydub/blob/master/pydub/effects.py)を見よ。
| パラメータ名 | 説明 | 単位 | デフォルトの値 |
| :-- | :-: | :-: | --: |
| --fade_duration | フェードイン/アウトの期間 | msec | 50 |
| --remove_dc_offset | DCオフセットを除去するか | bool | True |
| --hpf_cutoff| ハイパスフィルター（HPF）のカットオフ周波数 | Hz | 80 |
| --compressor | コンプレッサーをかけ、ダイナミックレンジを圧縮するか | bool | True |
| --head_room | ノーマライズ処理のためのマージンルーム | dBFS | 0.1 |
| --mono_channel| モノラル化で左右どちらの信号を使用するか | 0:左, 1:右 | 0 |

## やっていること
- 音源のフェードイン・フェードアウト処理
- DCオフセットの除去
- ハイパスフィルター（HPF）による不要な低音部分の除去
- コンプレッサーによる音量の均一化処理
- ノーマライズ（データ型のダイナミックレンジを生かすような音量の調整）
- チャンネルのモノラル化（備考を見よ）
- 無音区間検出に基づく音源ファイル分割処理（分割したファイルへも上記の各種処理を行っている）

## あえてやっていないこと
- ディザ：学習においてディザー処理は邪魔になる可能性があるとのため。
- ノイズ除去：ノイズ抑制には各種多様なやり方があり、実装しきれないため。
- mp3の再エンコード：多分音質がダメになるので、ファイルサイズを犠牲にしてもwavファイルに強制的に出力したままにしてある。

## 備考
RVCでも以下の処理は行われている。
- ノーマライズ
- チャンネルのモノラル化

ただし、チャンネルのモノラル化については(L+R)/2と言う平均処理が行なわれている。
これは歌唱音源やバイノーラル音源などLとRで位相が必ずしも揃わない信号で、そうした処理を行うと音質が劣化する可能性が考えられる。
本スクリプトではL,Rどちらか一方のチャンネル信号のみを選ぶようにして、この可能性を回避している。
