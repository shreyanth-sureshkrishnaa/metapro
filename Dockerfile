FROM python:3.12-slim

# Install system dependencies: exiftool + comprehensive Qt/WebEngine runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libimage-exiftool-perl \
    # OpenGL / EGL
    libgl1 \
    libegl1 \
    libopengl0 \
    # X11 core
    libx11-6 \
    libx11-xcb1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrender1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxcursor1 \
    libxtst6 \
    libxss1 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libxkbfile1 \
    # XCB plugins for Qt
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxcb-glx0 \
    libxcb-shm0 \
    # D-Bus, Fontconfig, GLib
    libdbus-1-3 \
    libfontconfig1 \
    libglib2.0-0 \
    # Accessibility
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    # WebEngine / Chromium dependencies
    libnss3 \
    libnspr4 \
    libasound2t64 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libcairo-gobject2 \
    # Multimedia
    libpulse0 \
    # Fonts
    fonts-inter \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and add to video/render groups for GPU access
RUN groupadd -g 107 render || true && \
    useradd -m -u 1000 -G video,render metapro || useradd -m -u 1000 -G video metapro || useradd -m -u 1000 metapro

WORKDIR /app

# Ensure we have permissions for the app and home directory
RUN chown -R metapro:metapro /app /home/metapro

# Install Python dependencies as non-root
USER metapro
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Add user bin to path for pip installed packages
ENV PATH="/home/metapro/.local/bin:${PATH}"

# Copy application code and fix ownership
USER root
COPY . .
RUN chown -R metapro:metapro /app

# Switch back to non-root user
USER metapro

# Disable Chromium sandbox (required for Docker)
ENV QTWEBENGINE_DISABLE_SANDBOX=1

CMD ["python", "main.py"]
