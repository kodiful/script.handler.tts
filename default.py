# -*- coding: utf-8 -*-

import urlparse, urllib
import sys, re
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from resources.lib.common import log, isholiday
from resources.lib.history import History
from resources.lib.phonebook import PhoneBook
from resources.lib.lookup import Lookup

#-------------------------------------------------------------------------------
def main():
    # パラメータ抽出
    args = urlparse.parse_qs(sys.argv[2][1:])
    text = args.get('action', None)
    # 設定
    addon = xbmcaddon.Addon()
    exe = addon.getSetting('exe')
    dic = addon.getSetting('dic')
    voice = addon.getSetting('voice')

    # 音声合成
    if exe and dic and voice:
        if text[0]:
            pass
        else:
            text = ''
        # 音声合成
        tts = [exe]
        mech = ['-x', dic]
        htsvoice = ['-m', voice]
        speed = ['-r', '1.0']
        wav = ['-ow', 'open_jtalk.wav']
        command = exe + mech + htsvoice + speed + wav
        c = subprocess.Popen(command, stdin=subprocess.PIPE)
        c.stdin.write(text)
        c.stdin.close()
        c.wait()
        # 再生
        aplay = ['aplay','-q','open_jtalk.wav']
        wr = subprocess.Popen(aplay)

#-------------------------------------------------------------------------------
if __name__  == '__main__': main()
