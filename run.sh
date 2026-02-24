#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# run.sh — Launch MetaPro in Docker with X11 display forwarding
# ─────────────────────────────────────────────────────────────────────────────
#
# Usage:
#   ./run.sh                         # basic launch
#   ./run.sh /path/to/photos         # mount a photos directory at /data
#
# Prerequisites:
#   - Docker installed and running
#   - On Linux: X11 display server (default on most distros)
#   - On macOS: XQuartz installed (brew install --cask xquartz)
#   - On Windows: VcXsrv or X410 installed
# ─────────────────────────────────────────────────────────────────────────────

set -e

IMAGE_NAME="metapro"
CONTAINER_NAME="metapro-app"

# Build image if it doesn't exist or if --build flag is passed
if [[ "$1" == "--build" ]] || ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
    echo "[MetaPro] Building Docker image..."
    docker build -t "$IMAGE_NAME" .
    [[ "$1" == "--build" ]] && shift
fi

# Allow X11 connections from Docker
if command -v xhost &>/dev/null; then
    xhost +local:docker 2>/dev/null || true
else
    echo "[MetaPro] Warning: xhost not found. Install with: sudo apt install x11-xserver-utils"
    echo "[MetaPro] Continuing without xhost — may work if XAUTHORITY is shared."
fi

# Determine volume mount
VOLUME_ARGS=""
if [[ -n "$1" && -d "$1" ]]; then
    PHOTOS_DIR="$(realpath "$1")"
    VOLUME_ARGS="-v ${PHOTOS_DIR}:/data:ro"
    echo "[MetaPro] Mounting ${PHOTOS_DIR} at /data inside container"
fi

# Remove any existing container with the same name
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

# Run the container
docker run -it --rm \
    --name "$CONTAINER_NAME" \
    -e DISPLAY="$DISPLAY" \
    --device /dev/dri:/dev/dri \
    -e LIBGL_ALWAYS_SOFTWARE=0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v "$HOME/.Xauthority:/root/.Xauthority:ro" \
    --network host \
    $VOLUME_ARGS \
    "$IMAGE_NAME"

# Revoke X11 access when done
command -v xhost &>/dev/null && xhost -local:docker 2>/dev/null || true
