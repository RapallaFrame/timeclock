# Build Time Clock Android APK using Buildozer
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 \
    ANDROID_SDK_ROOT=/opt/android-sdk \
    ANDROID_NDK_ROOT=/opt/android-sdk/ndk/25.1.8937393 \
    PATH=$PATH:/opt/android-sdk/cmdline-tools/latest/bin

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
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for buildozer
RUN useradd -m -s /bin/bash buildozer && \
    usermod -aG sudo buildozer && \
    echo "buildozer ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Install Python dependencies
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install buildozer cython pexpect virtualenv

# Set up Android SDK directories
RUN mkdir -p ${ANDROID_SDK_ROOT} && \
    chown -R buildozer:buildozer ${ANDROID_SDK_ROOT}

# Download and setup Android SDK (as root, then fix permissions)
RUN cd ${ANDROID_SDK_ROOT} && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
    unzip -q commandlinetools-linux-9477386_latest.zip && \
    rm commandlinetools-linux-9477386_latest.zip && \
    mkdir -p cmdline-tools/latest && \
    mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true && \
    chown -R buildozer:buildozer ${ANDROID_SDK_ROOT}

# Switch to non-root user
USER buildozer
WORKDIR /home/buildozer

# Accept Android SDK licenses
RUN yes | ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager --licenses 2>/dev/null || true

# Download Android SDK components
RUN ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager \
    "platforms;android-31" \
    "build-tools;31.0.0" \
    "ndk;25.1.8937393" \
    2>/dev/null || true

# Create app directory
WORKDIR /app

# Copy app files
COPY . /app/

# Build APK
CMD ["buildozer", "android", "debug"]
