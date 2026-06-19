[app]
title = VibeCheck
package.name = moodai
package.domain = com.glitchaura.vibecheck
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
android.ndk = 28c
android.gradle = 1
android.enable_androidx = 1
android.archs = arm64-v8a
android.presplash_color = #0a0a1a
android.add_src = 
android.add_jars = 
android.wakelock = 0
android.enable_minification = 1
android.enable_proguard = 1
android.split_permissions = 1

[buildozer]
log_level = 1
build_dir = ./.buildozer
bin_dir = ./bin
target = android
