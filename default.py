# -*- coding: utf-8 -*-

import os, shutil
import urlparse
import subprocess
from datetime import datetime
from random import random

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.common import log, notify
from resources.lib.common import LANG

# ファイル/ディレクトリパス
addon = xbmcaddon.Addon()
PROFILE_PATH = xbmc.translatePath(addon.getAddonInfo('profile'))
WAV_FILE = os.path.join(PROFILE_PATH, 'open_jtalk.wav')

#-------------------------------------------------------------------------------
def main():
    # パラメータ抽出
    args = urlparse.parse_qs(sys.argv[2][1:])
    lang = args.get('lang', None)
    text = args.get('text', None)
    quiet = args.get('quiet', None)
    amp = args.get('amp', None)
    speed = args.get('speed', None)
    txt_file = args.get('txt_file', None)
    wav_file = args.get('wav_file', None)
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
        text = '1,2,3,4,5,6,7,8,9,10'
    if text:
        # テキストを入力ファイルに書き込む
        f = open(txt_file1, 'w')
        f.write(text)
        f.close()
    # 言語
    if lang is None:
        lang = 'Japanese'
    else:
        lang = lang[0]
    # 音量
    if amp is None:
        amp = 1.0
    else:
        amp = float(amp[0])
    # 速度
    if speed is None:
        speed = 1.0
    else:
        speed = float(speed[0])
    # 音声合成コマンド
    settings = LANG[lang]
    if settings['tts'] == 'espeak':
        tts = addon.getSetting('espeak')
        dic = None
        voice = None
        command = '"{tts}" -a {amp100} -s {speed175} -v {lang} -f "{txt}" -w "{wav}" '.format(
            tts = tts,
            amp100 = int(100*amp),
            speed175 = int(175*speed),
            lang = settings['lang'],
            txt = txt_file1,
            wav = wav_file1
        )
    elif settings['tts'] == 'open_jtalk':
        tts = addon.getSetting('open_jtalk')
        dic = addon.getSetting('open_jtalk_dic')
        voice = addon.getSetting('open_jtalk_voice')
        command = '"{tts}" -x "{dic}" -m "{voice}" -g {amp0} -r {speed1} -ow "{wav}" "{txt}"'.format(
            tts = tts,
            dic = dic,
            voice = voice,
            amp0 = 10*math.log(amp)/math.log(10),
            speed1 = speed,
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
