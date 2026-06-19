[app]
title = Mood AI
package.name = moodai
package.domain = com.moodai.app
source.dir = .
source.include_exts = py,png,jpg,json,task,tflite
version = 1.0.0
requirements = python3,kivy,opencv-python,mediapipe,numpy,edge-tts,soundfile,plyer
orientation = portrait
fullscreen = 1
android.permissions = CAMERA,INTERNET,RECORD_AUDIO
android.api = 34
android.minapi = 26
android.targetapi = 34
android.ndk = 27b
android.sdk = 34
android.gradle = 1
android.enable_androidx = 1
android.arch = arm64-v8a

[buildozer]
log_level = 1
build_dir = ./.buildozer
bin_dir = ./bin
target = android
