# -*- coding: utf-8 -*-

import os, shutil
import urlparse
import subprocess
from datetime import datetime
from random import random
from math import log as ln

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.common import log, notify
from resources.lib.language import LANGUAGE

# ファイル/ディレクトリパス
ADDON = xbmcaddon.Addon()
PROFILE_PATH = xbmc.translatePath(ADDON.getAddonInfo('profile'))
WAV_FILE = os.path.join(PROFILE_PATH, 'tts.wav')

# import langdetect
addon_path = xbmc.translatePath(ADDON.getAddonInfo('path'))
resources_path = os.path.join(addon_path, 'resources')
lib_path = os.path.join(resources_path, 'lib')
path = os.path.join(lib_path, 'langdetect-1.0.7')
sys.path.append(path)
from langdetect import detect

#-------------------------------------------------------------------------------
def main():
    # パラメータ抽出
    args = urlparse.parse_qs(sys.argv[2][1:])
    lang = args.get('lang', None)
    text = args.get('text', None)
    silent = args.get('silent', None)
    amp = args.get('amp', None)
    speed = args.get('speed', None)
    txt_file = args.get('txt_file', None)
    wav_file = args.get('wav_file', None)

    #
    # パラメータチェック
    #

    # 言語
    if lang is None:
        lang = ADDON.getSetting('lang') or 'auto'
    else:
        lang = lang[0]
    if lang == 'auto' or LANGUAGE.get(lang, None):
        pass
    else:
        notify('Invalid argument(lang)', error=True)
        sys.exit()

    # 音量
    if amp is None:
        amp = ADDON.getSetting('amp') or 1.0
        amp = float(amp)
    else:
        amp = float(amp[0])
    if amp < 0.0 or amp > 2.0:
        notify('Invalid argument(amp)', error=True)
        sys.exit()

    # 速度
    if speed is None:
        speed = ADDON.getSetting('speed') or 1.0
        speed = float(speed)
    else:
        speed = float(speed[0])
    if speed < 0.0 or speed > 3.0:
        notify('Invalid argument(speed)', error=True)
        sys.exit()

    # 再生
    if silent is None:
        silent = 'false'
    else:
        silent = silent[0]
        if silent == 'true' or silent == 'false':
            pass
        else:
            notify('Invalid argument(silent)', error=True)
            sys.exit()

    #
    # ファイル初期化
    #

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
        if os.path.exists(txt_file):
            shutil.copy2(txt_file, txt_file1)
        else:
            notify('Invalid txt_file', error=True)
            sys.exit()
    else:
        if text:
            text = ' '.join(text)
        else:
            text = ADDON.getSetting('teststr') or 'hello'
        # テキストを入力ファイルに書き込む
        f = open(txt_file1, 'w')
        f.write(text)
        f.close()

    #
    # 言語判定
    #

    if lang == 'auto':
        try:
            code = detect(text.decode('utf-8'))
            for lang in LANGUAGE.keys():
                if LANGUAGE[lang]['code'] == code:
                    log('detected language: %s' % lang)
                    break
            else:
                lang = 'English'
                log('detected language: %s' % 'n/a')
        except:
            lang = 'English'
            log('detected language: %s' % 'error')

    #
    # 音声合成コマンド
    #

    settings = LANGUAGE[lang]
    if settings['tts'] == 'espeak':
        tts = ADDON.getSetting('espeak')
        voice = ADDON.getSetting('espeak_voice')
        if tts is None or voice is None:
            command = None
            notify('Invalid eSpeak settings', error=True)
        else:
            command = '"{tts}" -a {amp} -s {speed} -v {lang}{voice} -f "{txt}" -w "{wav}" '.format(
                tts = tts,
                voice = (voice=='auto' and ' ' or voice),
                amp = int(100*amp),
                speed = int(175*speed),
                lang = settings['code'],
                txt = txt_file1,
                wav = wav_file1
            )
            log('command: %s' % command)
    elif settings['tts'] == 'openjtalk':
        tts = ADDON.getSetting('openjtalk')
        dic = ADDON.getSetting('openjtalk_dic')
        voice = ADDON.getSetting('openjtalk_voice')
        if tts is None or dic is None or voice is None:
            command = None
            notify('Invalid OpenJTalk settings', error=True)
        else:
            command = '"{tts}" -x "{dic}" -m "{voice}" -g {amp} -r {speed} -ow "{wav}" "{txt}"'.format(
                tts = tts,
                dic = dic,
                voice = voice,
                amp = 10*ln(amp)/ln(10),
                speed = speed,
                txt = txt_file1,
                wav = wav_file1
            )
            log('command: %s' % command)

    # 音声合成を実行
    if command:
        returncode = subprocess.call(command, shell=True)
        if returncode == 0:
            # 一時ファイルのファイル名を変更
            os.rename(wav_file1, wav_file)
            # 再生
            if silent == 'true':
                pass
            else:
                xbmc.executebuiltin('PlayMedia(%s)' % wav_file)
        else:
            notify('TTS error', error=True)

    # 一時ファイルを削除
    if os.path.exists(txt_file1): os.remove(txt_file1)
    if os.path.exists(wav_file1): os.remove(wav_file1)

#-------------------------------------------------------------------------------
if __name__  == '__main__': main()
