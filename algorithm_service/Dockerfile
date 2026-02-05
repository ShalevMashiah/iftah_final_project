FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH="/usr/local/lib/python3.10/site-packages:/usr/lib/python3.10/site-packages:$PYTHONPATH"

# Install Python and OpenCV from system packages
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-opencv \
    && ln -s /usr/bin/python3 /usr/bin/python

# Install display libraries (GTK, X11, etc.)
RUN apt-get update && apt-get install -y \
    libgtk-3-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Install other packages (skip opencv-python since we have python3-opencv)
RUN pip install --no-cache-dir wheel && \
    pip install --no-cache-dir kafka-python fuzzywuzzy python-Levenshtein zmq numpy

COPY . .

CMD ["python", "src/main.py"]