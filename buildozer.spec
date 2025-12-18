[app]
title = Wave Defender
package.name = wavedefender
package.domain = com.astafevdanil9
source.dir = .
source.main = main.py
version = 1.0
requirements = python3, pygame, sdl2_ttf
orientation = landscape
fullscreen = 1
# Уберите эти строки - Buildozer сам определит:
# android.api = 31
# android.ndk = 25.2.9519653
android.archs = arm64-v8a
android.permissions = INTERNET, VIBRATE

[buildozer]
log_level = 2