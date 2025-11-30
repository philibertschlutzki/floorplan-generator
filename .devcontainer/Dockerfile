# Optional: Custom Dockerfile for more control
# Use this if devcontainer.json image doesn't provide enough flexibility

FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    xvfb \
    x11-utils \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libegl1-mesa \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libfontconfig1 \
    libdbus-1-3 \
    jq \
    wget \
    curl \
    git \
    libopencv-dev \
    python3-opencv \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    imagemagick \
    ghostscript \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Set display for headless operation
ENV DISPLAY=:99

# Install QCAD (will be done in setup script for flexibility)
# User can switch between this Dockerfile approach or devcontainer.json + setup.sh
