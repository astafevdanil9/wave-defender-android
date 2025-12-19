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

[android]
android.api = 33
android.build_tools_version = 33.0.2
android.sdk_path = /home/runner/android-sdk
android.ndk_path =

[buildozer]
warn_on_root = 0
log_level = 2
android.accept_sdk_license = True