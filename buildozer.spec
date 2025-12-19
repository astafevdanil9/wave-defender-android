[app]
title = Wave Defender
package.name = wavedefender
package.domain = com.astafevdanil9
source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,ttf,ogg,wav
version = 1.0.0
requirements = python3==3.10, kivy==2.2.1, pygame
orientation = portrait
fullscreen = 1
android.archs = arm64-v8a
android.permissions = INTERNET, VIBRATE

[buildozer]
warn_on_root = 0
log_level = 2
android.accept_sdk_license = True