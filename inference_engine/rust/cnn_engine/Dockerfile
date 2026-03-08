FROM nvidia/cuda:12.9.1-cudnn-devel-ubuntu24.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
    tzdata \
    curl \
    build-essential \
    pkg-config \
    libssl-dev \
    cmake \
    git \
    python3 \
    ca-certificates \
 && dpkg-reconfigure -f noninteractive tzdata \
 && rm -rf /var/lib/apt/lists/*

RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

COPY Cargo.toml Cargo.lock ./
RUN mkdir -p src && printf 'fn main() {}' > src/main.rs
RUN cargo build --release
RUN rm -rf src

COPY . .
RUN cargo build --release


FROM nvidia/cuda:12.9.1-cudnn-runtime-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
    tzdata \
    libgomp1 \
    ca-certificates \
    python3 \
    python3-venv \
 && dpkg-reconfigure -f noninteractive tzdata \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ARG ORT_VERSION=1.24.2
ARG ORT_CUDA12_EXTRA_INDEX=https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --extra-index-url ${ORT_CUDA12_EXTRA_INDEX} onnxruntime-gpu==${ORT_VERSION}

RUN python - <<'PY'
import os, shutil, site, glob
sp = site.getsitepackages()[0]
capi = os.path.join(sp, "onnxruntime", "capi")
dst = "/opt/onnxruntime/lib"
os.makedirs(dst, exist_ok=True)
for p in glob.glob(os.path.join(capi, "*.so*")):
    shutil.copy2(p, dst)
print("Copied ORT .so files from:", capi)
print("Into:", dst)
PY

RUN ln -sf /opt/onnxruntime/lib/libonnxruntime.so.1.24.2 /opt/onnxruntime/lib/libonnxruntime.so \
 && ln -sf /opt/onnxruntime/lib/libonnxruntime.so.1.24.2 /opt/onnxruntime/lib/libonnxruntime.so.1

RUN rm -f /opt/onnxruntime/lib/libonnxruntime_providers_tensorrt.so

ENV LD_LIBRARY_PATH=/opt/onnxruntime/lib:/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu
ENV ORT_DYLIB_PATH=/opt/onnxruntime/lib/libonnxruntime.so.1

RUN echo "/opt/onnxruntime/lib" > /etc/ld.so.conf.d/onnxruntime.conf \
 && echo "/usr/local/cuda/lib64" > /etc/ld.so.conf.d/cuda.conf \
 && echo "/usr/lib/x86_64-linux-gnu" > /etc/ld.so.conf.d/ubuntu.conf \
 && ldconfig

COPY --from=builder /app/target/release/cnn_engine /app/server

EXPOSE 8088
CMD ["/app/server"]