# Build Flutter for Linux desktop
FROM ghcr.io/cirruslabs/flutter:stable

# Install Linux desktop dependencies
RUN apt-get update && apt-get install -y \
    clang \
    cmake \
    ninja-build \
    pkg-config \
    libgtk-3-dev \
    liblzma-dev \
    libstdc++-12-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Flutter project files
COPY pubspec.* ./
RUN flutter pub get

COPY . .

# Enable Linux desktop and build
RUN flutter config --enable-linux-desktop
RUN flutter build linux --release

# Set the built app as the working directory
WORKDIR /app/build/linux/x64/release/bundle

# Set environment for software rendering
ENV LIBGL_ALWAYS_SOFTWARE=1

# Run the Flutter desktop app
CMD ["./flutter_to_do_list"]
