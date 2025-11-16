# Docker APK Build Instructions

## Prerequisites
- **Docker Desktop** installed on Windows ([Download](https://www.docker.com/products/docker-desktop))
- WSL2 backend enabled (automatic with Docker Desktop)

## Quick Start

### Option 1: Build APK (Recommended)
```powershell
cd "C:\Users\Rapal\OneDrive\Desktop\Current projects\Time clock app"
docker-compose up --build
```

The APK will be generated in the `bin/` folder after build completes (~10-15 minutes first time).

**Output:** `bin/timeclockapp-1.0.0-debug.apk`

### Option 2: Interactive Build (For Debugging)
```powershell
docker-compose run --rm buildozer bash
# Inside container:
buildozer android debug
```

### Option 3: Clean Build (Reset Cache)
```powershell
docker-compose down -v
docker-compose up --build
```

## What Docker Does
1. Creates Linux container with Ubuntu 22.04
2. Installs Java JDK, Android SDK, Android NDK (all tools)
3. Mounts your app directory inside container
4. Runs buildozer to compile APK
5. Outputs APK to your `bin/` folder on Windows

## Transfer APK to Android Phone

After build completes:

1. **Via USB Cable:**
   ```powershell
   # Copy APK to phone via adb
   adb devices  # List connected devices
   adb push bin/timeclockapp-1.0.0-debug.apk /sdcard/Download/
   ```
   Then on phone: Settings > Apps > Install from Unknown Sources > select APK from Downloads

2. **Via File Sharing:**
   - Copy `bin/timeclockapp-1.0.0-debug.apk` to cloud (Google Drive, OneDrive)
   - Download on phone from cloud storage
   - Tap file to install

3. **Via Email:**
   - Attach APK to email
   - Open email on phone
   - Tap attachment to install

## Troubleshooting

**Error: "Docker daemon not running"**
- Open Docker Desktop application

**Error: "image not found"**
- First build takes longer. Wait ~10 minutes for Android SDK download

**Error: "Permission denied"**
- On macOS/Linux: Use `sudo docker-compose` instead

**Build takes too long**
- Normal first time (~15-20 min for SDK download)
- Subsequent builds use cache (~2-3 min)

## Alternative: Manual Windows Buildozer Fix

If you prefer to fix Windows buildozer directly:

1. **Install Ubuntu WSL2:**
   ```powershell
   wsl --install Ubuntu-22.04
   ```

2. **Build inside WSL2:**
   ```bash
   cd /mnt/c/Users/Rapal/OneDrive/Desktop/Current\ projects/Time\ clock\ app
   buildozer android debug
   ```

This runs buildozer in Linux environment where it's natively supported.

## Files Included

- `Dockerfile` - Container configuration with all Android tools
- `docker-compose.yml` - Simplified build orchestration
- `buildozer.spec` - App configuration (already set up)
- `main.py` - Time Clock app code

## Next Steps After APK Generated

1. Transfer APK to Android phone (see "Transfer APK" section above)
2. Enable "Install from Unknown Sources" in Settings
3. Open file manager and tap APK to install
4. App appears in app drawer as "Time Clock App"
5. Create user account and start tracking hours!

---

**Estimated Time:**
- First build: 15-20 minutes (downloads Android SDK)
- Subsequent builds: 2-3 minutes (uses cache)
- APK size: ~50-80 MB

**Questions?**
- Check build logs: `docker-compose logs buildozer`
- Clean everything: `docker-compose down -v`
- Manual rebuild: `docker-compose up --build`
