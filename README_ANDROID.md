# Time Clock App - Android APK Build Guide

## Overview
This is a Kivy-based version of the Time Clock desktop application converted to run on Android as a native APK.

## Prerequisites

### For Desktop Testing (Windows):
1. **Python 3.9+**
2. **Kivy** - For building the UI
3. **Buildozer** (optional - for desktop testing)

### For Android APK Build:
1. **Java Development Kit (JDK)** - Java 11 or 17
2. **Android SDK** - Minimum API level 21
3. **Android NDK** - For native compilation
4. **Python 3.9+**
5. **Buildozer** - Build tool for Kivy → APK

---

## Step 1: Install Dependencies on Windows

### A. Install Kivy

```powershell
pip install kivy
pip install buildozer
pip install cython
pip install pillow
```

### B. Test on Desktop First

Before building for Android, test the app on your PC:

```powershell
python main.py
```

---

## Step 2: Prepare for Android Build (Windows)

### Install Android Tools

1. **Install Java JDK 11 or 17**
   - Download from: https://www.oracle.com/java/technologies/downloads/
   - Or use OpenJDK: `choco install openjdk11` (if using Chocolatey)

2. **Set JAVA_HOME Environment Variable**
   - Open PowerShell as Admin:
   ```powershell
   $env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
   [Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Java\jdk-17", "User")
   ```

3. **Install Android SDK**
   - Download Android Command Line Tools from: https://developer.android.com/studio/command-line/sdkmanager
   - Extract to `C:\Android\sdk`
   - Set ANDROID_SDK_ROOT:
   ```powershell
   [Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", "C:\Android\sdk", "User")
   [Environment]::SetEnvironmentVariable("ANDROID_HOME", "C:\Android\sdk", "User")
   ```

4. **Install Android NDK**
   ```powershell
   cd C:\Android\sdk
   .\cmdline-tools\latest\bin\sdkmanager.bat "ndk;25.1.8937393"
   ```

---

## Step 3: Build the APK

### Option A: Using Buildozer (Recommended)

Navigate to your project directory and run:

```powershell
buildozer android debug
```

This will:
- Download Cython and other dependencies
- Compile your Python code
- Build the APK

**Build Output:**
- APK will be saved to: `bin/timeclock-0.1-debug.apk`

**Build time:** 30 minutes to 1+ hour (first build is slow)

### Option B: Advanced Build with Verbose Output

For debugging build issues:

```powershell
buildozer android debug -- --verbose
```

---

## Step 4: Transfer APK to Android Device

### Via USB Cable (Recommended):
1. Enable USB Debugging on your Android phone:
   - Settings → About Phone → Tap "Build Number" 7 times
   - Back to Settings → Developer Options → USB Debugging → ON
2. Connect phone to PC via USB
3. Run:
   ```powershell
   adb install "bin/timeclock-0.1-debug.apk"
   ```

### Via File Transfer:
1. Copy `bin/timeclock-0.1-debug.apk` to your phone
2. Open file manager on phone and tap the APK to install

---

## Step 5: Build Release APK (For Distribution)

### Generate Signing Keys

First-time only:

```powershell
keytool -genkey -v -keystore my-release-key.keystore -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias
```

### Update buildozer.spec

Edit `buildozer.spec` and add:

```ini
android.release_artifact = aab

# Add these lines in [app] section
android.keystore = 1
android.keystore_path = ./my-release-key.keystore
android.keystore_alias = my-key-alias
```

### Build Release APK

```powershell
buildozer android release
```

Output: `bin/timeclock-0.1-release.apk`

---

## Troubleshooting

### Issue: "JAVA_HOME not set"
**Solution:**
```powershell
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
```

### Issue: "Android SDK not found"
**Solution:**
```powershell
$env:ANDROID_SDK_ROOT = "C:\Android\sdk"
$env:ANDROID_HOME = "C:\Android\sdk"
```

### Issue: Build fails with NDK error
**Solution:**
Ensure NDK is installed:
```powershell
cd C:\Android\sdk
.\cmdline-tools\latest\bin\sdkmanager.bat "ndk;25.1.8937393"
```

### Issue: "XDG_RUNTIME_DIR not set"
**Solution:** This can be ignored on Windows

### Issue: Gradle build fails
**Solution:** Delete `./buildozer` folder and retry:
```powershell
Remove-Item -Recurse ./buildozer -Force
buildozer android debug
```

---

## Project Structure

```
Time clock app/
├── main.py                 # Kivy app (converted from Tkinter)
├── buildozer.spec         # Build configuration
├── timeclock_data.json    # Current session data (auto-created)
├── timeclock_history.json # Time entries history (auto-created)
├── timeclock_users.json   # User data (auto-created)
└── README.md              # This file
```

---

## Key Features

✅ Clock In/Out time tracking  
✅ Daily time totals  
✅ Add notes (max 20 words)  
✅ View work history  
✅ Multiple user support  
✅ Persistent data storage  

---

## File Structure After APK Install

On your Android device, data is stored in:
```
/data/data/org.example.timeclock/files/
├── timeclock_data.json
├── timeclock_history.json
└── timeclock_users.json
```

---

## Next Steps

1. ✅ Test on Windows desktop: `python main.py`
2. ✅ Install Android tools (JDK, SDK, NDK)
3. ✅ Build debug APK: `buildozer android debug`
4. ✅ Transfer to phone and test
5. ✅ Build release APK for distribution

---

## Useful ADB Commands

```powershell
# Check connected devices
adb devices

# Install APK
adb install "bin/timeclock-0.1-debug.apk"

# Uninstall app
adb uninstall org.example.timeclock

# View logs
adb logcat | grep python

# Open app
adb shell am start -n org.example.timeclock/.MainActivity
```

---

## Additional Resources

- **Kivy Documentation:** https://kivy.org/doc/stable/
- **Buildozer Documentation:** https://buildozer.readthedocs.io/
- **Python for Android:** https://python-for-android.readthedocs.io/
- **Android Developer:** https://developer.android.com/

