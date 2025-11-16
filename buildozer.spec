[app]

# (str) Title of your application
title = Time Clock App

# (str) Package name
package.name = timeclock

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (source.dir) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,images/*

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
# Do not remove empty list as it falls back to source.exclude_patterns
# This removes the entire venv/ folder
#source.exclude_patterns = license,images/*/*.py

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK / App will support.
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
#android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android app theme, default is ok for Kivy-based app
# android.theme = "@android:style/Theme.NoTitleBar"

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a,armeabi-v7a

# (int) overrides automatic versionCode (used in build.gradle)
#android.version_code = 1

# (str) overrides automatic versionName (used in build.gradle)
#android.version_name = 0.1

# (str) Supported orientation (landscape, portrait or all)
android.orientation = portrait

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) Android gradle dependencies to add
android.gradle_dependencies = 

#
# Python for android (p4a) specific
#

# (str) python for android URL, defaults to the one specified in p4a/__init__.py
#p4a.url = https://github.com/kivy/python-for-android/archive/develop.zip

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#p4a.port = 5037

#
# buildozer.log_level = 2

#
# log_level = 2

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning upon buildozer start
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. where to put the built APK)
# bin_dir = ./bin

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning upon buildozer start
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. where to put the built APK)
# bin_dir = ./bin
