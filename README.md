# Audio Speech Segmentation Tool for RVC
RVCのための音声スピーチセグメンテーションツール

## これって何
このPythonスクリプトは[RVC](https://github.com/liujing04/Retrieval-based-Voice-Conversion-WebUI)のための
オーディオファイル群を分割、整音するツールです。

## 使い方
まず、python環境に、ソースの冒頭にあるライブラリ、pydub, noisereduce, voicefixer numpyをインストールしてください。

`pip install pydub`

`pip install noisereduce`

`pip install voicefixer`

`pip install numpy`

あるいはrequirements.txtで各種ライブラリをインストールできる。

`pip install -r requirements.txt`

ライブラリの準備ができたらbat,sh,あるいはpythonからspeech_seg_tool.pyを実行する。デフォルトの値は大体最適なように設定されているので、パラメータを入力せず、そのままでもOK。

`python speech_seg_tool.py`

`run.bat`

`run.sh`


## パラメータの説明
### ファイル関連

| パラメータ名 | 説明 | デフォルトの値 |
| :-- | :-: | --: |
| --input_dir | 入力ディレクトリ。ここにオーディオファイル群を入れます。 | input |
| --output_dir | 出力ディレクトリ。ここに分割等各種処理されたオーディオファイル群が格納されます。自動的に作らないので注意。 | output |

### 区間分割関連。[pydubのドキュメント](https://github.com/jiaaro/pydub/blob/master/API.markdown)も見よ。

| パラメータ名 | 説明 | 単位 | デフォルトの値 |
| :-- | :-: | :-: | --: |
| --min_silence_len | 無音とみなす最小の期間。 | msec | 300 |
| --silence_thresh | 無音の閾値 | dBFS | -30 |
| --keep_silence| 無音期間をどれくらい残すか。 | msec、あるいはTrue（全部残す）, False(全部残さない) | 50 |
| --seek_step| 無音期間探索のためのステップ期間。値が小さいほど精度が増し、負荷は増大する。 | msec | 10 |


### その他各種処理関連。こちらも[pydubのドキュメント](https://github.com/jiaaro/pydub/blob/master/API.markdown)と[pydub.effectsのソース](https://github.com/jiaaro/pydub/blob/master/pydub/effects.py)を見よ。
| パラメータ名 | 説明 | 単位 | デフォルトの値 |
| :-- | :-: | :-: | --: |
| --fade_duration | フェードイン/アウトの期間 | msec | 50 |
| --remove_dc_offset | DCオフセットを除去するか | bool | True |
| --hpf_cutoff| ハイパスフィルター（HPF）のカットオフ周波数 | Hz | 80 |
| --head_room | ノーマライズ処理のためのマージンルーム | dBFS | 0.1 |
| --mono_channel| モノラル化で左右どちらの信号を使用するか | 1:左, 2:右, それ以外:左右の平均（これは音質を劣化させうる！。備考を見よ） | 1 |
| --voicefixer| voicefixerライブラリのモード。 | -1はvoicefixerを使わない。 | 0 |


## やっていること
- 音源のフェードイン・フェードアウト処理
- DCオフセットの除去
- ハイパスフィルター（HPF）による不要な低音部分の除去
- ノイズ除去
- 低サンプリングレート音声の、失われた帯域の修復
- ノーマライズ（データ型のダイナミックレンジを生かすような音量の調整）
- チャンネルのモノラル化（備考を見よ）
- データ型の2**4=32bit化（ディザが出来ないのでデータ型を拡張してお茶をにごす）
- 無音区間検出に基づく音源ファイル分割処理

## あえてやっていないこと
- ディザ：学習においてディザー処理は邪魔になるため。
- mp3の再エンコード：多分音質がダメになるので、flacファイルに強制的に出力したままにしてある。

## 備考
RVCでも以下の前処理は行われている。
- ノーマライズ(ヘッドルームなし)
- チャンネルのモノラル化

ただし、チャンネルのモノラル化については(L+R)/2と言う平均化処理が行なわれている。
これはミキシング・マスタリングされた歌唱音源やバイノーラル音源など、LとRで位相が必ずしも揃わない信号で、そうした処理を行うと音質が劣化する可能性が考えられる。
本スクリプトではL,Rどちらか一方のチャンネル信号のみを選ぶようにして、この可能性を回避している。
