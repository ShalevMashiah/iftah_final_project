FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# System deps for OpenCV GUI + X11
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    libgtk-3-0 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libcanberra-gtk-module \
    libcanberra-gtk3-module \
    libxkbcommon-x11-0 \
    libxcb1 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-randr0 \
    libxcb-xfixes0 \
    libxcb-sync1 \
    libxcb-shm0 \
    libxcb-util1 \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY requirements.txt ./

# Install python deps + sanity check versions (prevents silent numpy/opencv mismatch)
RUN pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    python -c "import numpy as np; import cv2; print('numpy', np.__version__, 'cv2', cv2.__version__)"

COPY . .

CMD ["python", "src/main.py"]
