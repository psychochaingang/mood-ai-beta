# VibeCheck APK Builder
# Paste this entire file into a new Google Colab notebook and run it

import os, subprocess, sys

def run(cmd):
    print(f"Running: {cmd[:80]}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    for line in result.stdout.split('\n')[-5:]:
        if line.strip(): print(line)
    if result.returncode != 0:
        for line in result.stderr.split('\n')[-3:]:
            if line.strip(): print(f"ERR: {line}")

print("=== Installing system dependencies ===")
run("apt-get update -qq && apt-get install -y -qq git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev cmake libffi-dev libssl-dev 2>&1 | tail -3")

print("\n=== Cloning repo ===")
os.chdir("/content")
run("rm -rf mood-ai-beta")
run("git clone https://github.com/psychochaingang/mood-ai-beta.git")
os.chdir("/content/mood-ai-beta")

print("\n=== Installing buildozer ===")
run("pip install buildozer cython -q 2>&1 | tail -3")

print("\n=== Building APK (this takes ~20 min) ===")
os.chdir("/content/mood-ai-beta/mood_ai_app_project")
run("buildozer android debug 2>&1")

print("\n=== APK Ready! ===")
import glob
apks = glob.glob("/content/mood-ai-beta/mood_ai_app_project/bin/*.apk")
if apks:
    size_mb = os.path.getsize(apks[0]) / 1_000_000
    print(f"APK: {apks[0]}")
    print(f"Size: {size_mb:.1f} MB")
    from google.colab import files
    files.download(apks[0])
else:
    print("APK not found. Check the build logs above.")
