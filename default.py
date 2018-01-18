# -*- coding: utf-8 -*-

import os, urlparse
import subprocess
from datetime import datetime

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.common import log

# ファイル/ディレクトリパス
addon = xbmcaddon.Addon()
PROFILE_PATH = xbmc.translatePath(addon.getAddonInfo('profile'))
TXT_FILE = os.path.join(PROFILE_PATH, 'open_jtalk.txt')
WAV_FILE = os.path.join(PROFILE_PATH, 'open_jtalk.wav')

#-------------------------------------------------------------------------------
def main():
    # ログ
    log("\n".join([
        'argv[0]: %s' % sys.argv[0],
        'argv[1]: %s' % sys.argv[1],
        'argv[2]: %s' % sys.argv[2]
    ]))
    # パラメータ抽出
    args = urlparse.parse_qs(sys.argv[2][1:])
    text = args.get('text', None)
    quiet = args.get('quiet', None)
    speed = args.get('speed', None)
    txt_file = args.get('txt_file', None)
    wav_file = args.get('wav_file', None)
    # 設定
    addon = xbmcaddon.Addon()
    tts = addon.getSetting('tts')
    dic = addon.getSetting('dic')
    voice = addon.getSetting('voice')
    # 入力ファイル
    if text:
        text = ' '.join(text)
        # 定型文
        if text == '@time':
            d = datetime.now()
            text = '%s月%s日、%s時%s分%s秒' % (d.month, d.day, d.hour, d.minute, d.second)
        log('text: %s' % text)
        # テキストをファイル化
        if txt_file is None:
            txt_file = TXT_FILE
        else:
            txt_file = txt_file[0]
        f = open(txt_file, 'w')
        f.write(text)
        f.close()
    # 出力ファイル
    if wav_file is None:
        wav_file = WAV_FILE
    else:
        wav_file = wav_file[0]
    # 速度
    if speed is None:
        speed = 1.0
    else:
        speed = speed[0]
    # 音声合成
    if text and tts and dic and voice and txt_file and wav_file:
        # 音声合成コマンド
        command = '"{tts}" -x "{dic}" -m "{voice}" -r {speed} -ow "{wav_file}" "{txt_file}"'.format(
            tts = tts,
            dic = dic,
            voice = voice,
            speed = speed,
            txt_file = txt_file,
            wav_file = wav_file
        )
        log(command)
        # 実行
        returncode = subprocess.call(command, shell=True)
        if returncode == 0 and quiet is None:
            xbmc.executebuiltin('PlayMedia(%s)' % WAV_FILE)
    else:
        notify('Invalid arguments', error=True)

#-------------------------------------------------------------------------------
if __name__  == '__main__': main()
