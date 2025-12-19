[app]
title = Wave Defender
package.name = wavedefender
package.domain = com.astafevdanil9
source.dir = .
source.main = main.py
version = 1.0.0
requirements = python3==3.11, kivy==2.3.0, pygame, sdl2_ttf
orientation = portrait
fullscreen = 1
android.archs = arm64-v8a
android.permissions = INTERNET, VIBRATE

[buildozer]
warn_on_root = 0
log_level = 2
android.accept_sdk_license = True