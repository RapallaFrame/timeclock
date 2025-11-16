# Build Time Clock Android APK using Buildozer
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 \
    ANDROID_SDK_ROOT=/opt/android-sdk \
    ANDROID_NDK_ROOT=/opt/android-ndk

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    git \
    wget \
    unzip \
    openjdk-11-jdk \
    libc6 \
    libstdc++6 \
    libssl-dev \
    libffi-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --upgrade pip
RUN pip3 install buildozer cython kivy pexpect virtualenv

# Download and setup Android SDK
RUN mkdir -p ${ANDROID_SDK_ROOT} && \
    cd ${ANDROID_SDK_ROOT} && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
    unzip -q commandlinetools-linux-9477386_latest.zip && \
    rm commandlinetools-linux-9477386_latest.zip && \
    mkdir -p cmdline-tools/latest && \
    mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true

# Accept Android SDK licenses
RUN yes | ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager --licenses 2>/dev/null || true

# Download Android SDK components
RUN ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager \
    "platforms;android-31" \
    "build-tools;31.0.0" \
    "ndk;25.1.8937393" \
    2>/dev/null || true

# Setup NDK path
RUN export ANDROID_NDK_ROOT=/opt/android-sdk/ndk/25.1.8937393 || true

# Create app directory
WORKDIR /app

# Copy app files
COPY . /app/

# Set buildozer.spec to use correct paths
RUN sed -i "s|android.sdk_path =.*|android.sdk_path = ${ANDROID_SDK_ROOT}|g" buildozer.spec && \
    sed -i "s|android.ndk_path =.*|android.ndk_path = ${ANDROID_NDK_ROOT}|g" buildozer.spec

# Build APK
CMD ["buildozer", "android", "debug"]
