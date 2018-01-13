# -*- coding: utf-8 -*-

import os, urlparse
import subprocess
from datetime import datetime

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.common import log

addon = xbmcaddon.Addon()

# ファイル/ディレクトリパス
PROFILE_PATH = xbmc.translatePath(addon.getAddonInfo('profile'))
TXT_FILE = os.path.join(PROFILE_PATH, 'open_jtalk.txt')
WAV_FILE = os.path.join(PROFILE_PATH, 'open_jtalk.wav')

#-------------------------------------------------------------------------------
def main():
    # パラメータ抽出
    args = urlparse.parse_qs(sys.argv[2][1:])
    text = args.get('text', None)
    if text is None:
        d = datetime.now()
        text = '%s月%s日、%s時%s分%s秒' % (d.month, d.day, d.hour, d.minute, d.second)
    # テキストをファイル化
    f = open(TXT_FILE, 'w')
    f.write(text)
    f.close()
    # 設定
    addon = xbmcaddon.Addon()
    tts = addon.getSetting('tts')
    dic = addon.getSetting('dic')
    voice = addon.getSetting('voice')
    # 音声合成
    if text and tts and dic and voice:
        # 音声合成コマンド
        command = '"{tts}" -x "{dic}" -m "{voice}" -r {speed} -ow "{wav_file}" "{txt_file}"'.format(
            tts = tts,
            dic = dic,
            voice = voice,
            speed = '1.0',
            wav_file = WAV_FILE,
            txt_file = TXT_FILE
        )
        log(command)
        # 実行
        returncode = subprocess.call(command, shell=True)
        # 再生
        xbmc.executebuiltin('PlayMedia(%s)' % WAV_FILE)

#-------------------------------------------------------------------------------
if __name__  == '__main__': main()
