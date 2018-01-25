# -*- coding: utf-8 -*-

'''
The Japanese TTS System "Open JTalk"
Version 1.10 (http://open-jtalk.sourceforge.net/)
Copyright (C) 2008-2016 Nagoya Institute of Technology
All rights reserved.

The HMM-Based Speech Synthesis Engine "hts_engine API"
Version 1.10 (http://hts-engine.sourceforge.net/)
Copyright (C) 2001-2015 Nagoya Institute of Technology
              2001-2008 Tokyo Institute of Technology
All rights reserved.

Yet Another Part-of-Speech and Morphological Analyzer "Mecab"
Version 0.996 (http://mecab.sourceforge.net/)
Copyright (C) 2001-2008 Taku Kudo
              2004-2008 Nippon Telegraph and Telephone Corporation
All rights reserved.

NAIST Japanese Dictionary
Version 0.6.1-20090630 (http://naist-jdic.sourceforge.jp/)
Copyright (C) 2009 Nara Institute of Science and Technology
All rights reserved.

open_jtalk - The Japanese TTS system "Open JTalk"

  usage:
       open_jtalk [ options ] [ infile ]
  options:                                                                   [  def][ min-- max]
    -x  dir        : dictionary directory                                    [  N/A]
    -m  htsvoice   : HTS voice files                                         [  N/A]
    -ow s          : filename of output wav audio (generated speech)         [  N/A]
    -ot s          : filename of output trace information                    [  N/A]
    -s  i          : sampling frequency                                      [ auto][   1--    ]
    -p  i          : frame period (point)                                    [ auto][   1--    ]
    -a  f          : all-pass constant                                       [ auto][ 0.0-- 1.0]
    -b  f          : postfiltering coefficient                               [  0.0][ 0.0-- 1.0]
    -r  f          : speech speed rate                                       [  1.0][ 0.0--    ]
    -fm f          : additional half-tone                                    [  0.0][    --    ]
    -u  f          : voiced/unvoiced threshold                               [  0.5][ 0.0-- 1.0]
    -jm f          : weight of GV for spectrum                               [  1.0][ 0.0--    ]
    -jf f          : weight of GV for log F0                                 [  1.0][ 0.0--    ]
    -g  f          : volume (dB)                                             [  0.0][    --    ]
    -z  i          : audio buffer size (if i==0, turn off)                   [    0][   0--    ]
  infile:
    text file                                                                [stdin]
'''

import os, shutil
import urlparse
import subprocess
from datetime import datetime
from random import random

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.common import log, notify

# ファイル/ディレクトリパス
addon = xbmcaddon.Addon()
PROFILE_PATH = xbmc.translatePath(addon.getAddonInfo('profile'))
WAV_FILE = os.path.join(PROFILE_PATH, 'open_jtalk.wav')

#-------------------------------------------------------------------------------
def main():
    # パラメータ抽出
    args = urlparse.parse_qs(sys.argv[2][1:])
    text = args.get('text', None)
    quiet = args.get('quiet', None)
    speed = args.get('speed', None)
    txt_file = args.get('txt_file', None)
    wav_file = args.get('wav_file', None)
    # 設定
    tts = addon.getSetting('tts')
    dic = addon.getSetting('dic')
    voice = addon.getSetting('voice')
    # 一時ファイルを初期化
    tmp = str(random())[2:]
    txt_file1 = os.path.join(PROFILE_PATH, '%s.txt' % tmp)
    if os.path.exists(txt_file1): os.remove(txt_file1)
    wav_file1 = os.path.join(PROFILE_PATH, '%s.wav' % tmp)
    if os.path.exists(wav_file1): os.remove(wav_file1)
    # 出力ファイルを初期化
    if wav_file is None:
        wav_file = WAV_FILE
    else:
        wav_file = wav_file[0]
    if os.path.exists(wav_file): os.remove(wav_file)
    # 入力ファイルを準備
    if txt_file:
        shutil.copy2(txt_file, txt_file1)
    elif text:
        text = ' '.join(text)
    else:
        text = '@time'
    if text:
        # 定型文
        if text == '@time':
            now = datetime.now()
            text = '%s月%s日、%s時%s分%s秒' % (now.month, now.day, now.hour, now.minute, now.second)
        log('text: %s' % text)
        # テキストを入力ファイルに書き込む
        f = open(txt_file1, 'w')
        f.write(text)
        f.close()
    # 速度
    if speed is None:
        speed = 1.0
    else:
        speed = speed[0]
    # 音声合成コマンド
    command = '"{tts}" -x "{dic}" -m "{voice}" -r {speed} -ow "{wav}" "{txt}"'.format(
        tts = tts,
        dic = dic,
        voice = voice,
        speed = speed,
        txt = txt_file1,
        wav = wav_file1
    )
    log('command: %s' % command)
    # 音声合成を実行
    returncode = subprocess.call(command, shell=True)
    if returncode == 0:
        # 一時ファイルのファイル名を変更
        os.rename(wav_file1, wav_file)
        # 再生
        if quiet is None:
            xbmc.executebuiltin('PlayMedia(%s)' % wav_file)
    # 一時ファイルを削除
    if os.path.exists(txt_file1): os.remove(txt_file1)
    if os.path.exists(wav_file1): os.remove(wav_file1)

#-------------------------------------------------------------------------------
if __name__  == '__main__': main()
