@echo off
REM Quick setup script for Time Clock App Android build
REM Run as Administrator

echo ============================================
echo Time Clock App - Android Build Setup
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed or not in PATH
    echo Download from: https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
pip install kivy buildozer cython pillow --upgrade

echo.
echo [2/4] Checking Java...
java -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Java not found. You will need to install JDK 11 or 17
    echo Download from: https://www.oracle.com/java/technologies/downloads/
    echo.
) else (
    java -version
)

echo.
echo [3/4] Environment variables...
echo.
echo Setting JAVA_HOME (modify path if needed):
set JAVA_HOME=C:\Program Files\Java\jdk-17
setx JAVA_HOME "C:\Program Files\Java\jdk-17"
echo JAVA_HOME set to: %JAVA_HOME%

echo.
echo Setting ANDROID_SDK_ROOT:
set ANDROID_SDK_ROOT=C:\Android\sdk
setx ANDROID_SDK_ROOT "C:\Android\sdk"
echo ANDROID_SDK_ROOT set to: %ANDROID_SDK_ROOT%

echo.
echo [4/4] Next steps:
echo.
echo 1. Download Android SDK from:
echo    https://developer.android.com/studio/command-line/sdkmanager
echo.
echo 2. Extract to C:\Android\sdk
echo.
echo 3. Run this to install NDK:
echo    C:\Android\sdk\cmdline-tools\latest\bin\sdkmanager.bat "ndk;25.1.8937393"
echo.
echo 4. Test the app on desktop:
echo    python main.py
echo.
echo 5. Build APK:
echo    buildozer android debug
echo.

echo ============================================
echo Setup complete! See README_ANDROID.md
echo ============================================
pause
