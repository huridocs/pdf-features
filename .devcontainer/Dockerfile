FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    wget \
    build-essential \
    cmake \
    pkg-config \
    libfontconfig1-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    libpng-dev \
    libtiff5-dev \
    libcurl4-openssl-dev \
    zlib1g-dev \
    qt5-qmake \
    qtbase5-dev \
    libqt5gui5 \
    libqt5widgets5 \
    libboost-all-dev \
    libcairo2-dev \
    liblcms2-dev \
    qpdf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN wget https://poppler.freedesktop.org/poppler-24.02.0.tar.xz \
    && tar -xf poppler-24.02.0.tar.xz \
    && cd poppler-24.02.0 \
    && mkdir build \
    && cd build \
    && cmake .. -DCMAKE_BUILD_TYPE=Release -DENABLE_UNSTABLE_API_ABI_HEADERS=ON -DENABLE_NSS3=OFF -DENABLE_GPGME=OFF -DENABLE_QT6=OFF \
    && make -j$(nproc) \
    && make install \
    && ldconfig

WORKDIR /workspace

CMD ["bash"]