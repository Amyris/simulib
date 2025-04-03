FROM debian:bookworm-slim as builder

ARG SUNDIALS_VERSION="5.0.0"

ENV SUNDIALS="/opt/sundials"

WORKDIR /

# install debian essentials for building dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    cmake \
    build-essential \
    curl \
    gnupg2 \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L -O "https://github.com/LLNL/sundials/releases/download/v${SUNDIALS_VERSION}/sundials-${SUNDIALS_VERSION}.tar.gz" && \
    tar -xzf sundials-${SUNDIALS_VERSION}.tar.gz && \
    mkdir ${SUNDIALS} && \
    mkdir ${SUNDIALS}/install && \
    mkdir ${SUNDIALS}/build && \
    cd ${SUNDIALS}/build && \
    cmake -DCMAKE_INSTALL_PREFIX=${SUNDIALS}/install \ 
          -DEXAMPLES_INSTALL_PATH=${SUNDIALS}/install/examples \
          /sundials-${SUNDIALS_VERSION} && \
    make && \
    make install 

# SUNDIALS container image
FROM python:3.10-slim-bookworm as dev

ARG GLPK_VERSION="4.65"
ENV SUNDIALS="/opt/sundials"

COPY --from=builder ${SUNDIALS}/install ${SUNDIALS}

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    pybind11-dev \
    build-essential \
    gcc \
    gnupg2 \
    cmake \
    gfortran \
    libgmp-dev \
    python-dev-is-python3 \
    libglpk-dev && \
    rm -rf /var/lib/apt/lists/*

# GLPK
# Download the specified distribution, verify it and install
RUN curl -L -O "ftp://ftp.gnu.org/gnu/glpk/glpk-${GLPK_VERSION}.tar.gz" && \
    curl -L -O "ftp://ftp.gnu.org/gnu/glpk/glpk-${GLPK_VERSION}.tar.gz.sig" && \
    gpg --keyserver keyserver.ubuntu.com --recv-keys 5981E818 && \
    gpg --verify "glpk-${GLPK_VERSION}.tar.gz.sig" && \
    tar -xzf "glpk-${GLPK_VERSION}.tar.gz" && \
    cd "glpk-${GLPK_VERSION}" && \
    ./configure --with-gmp && \
    make && \
    make install && \
    cd .. && \
    rm -rf "glpk-${GLPK_VERSION}"*


COPY --from=ghcr.io/astral-sh/uv:0.6.11 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml ./

ARG EXTRAS="dfba"
RUN EXTRA_NAMES=$(echo $EXTRAS | sed 's/,/ --extra /g' | sed 's/^/--extra /')
RUN echo ${EXTRA_NAMES}


RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project ${EXTRA_NAMES}

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen ${EXTRA_NAMES}


ENV PATH="/app/.venv/bin:$PATH"

FROM dev as vscode

ARG USERNAME=vscode
# USER_UID and USER_GID are important - it should match your host's
# user UID and GID. Usually, these are 1000 so it doesn't need to be changed.
# See https://code.visualstudio.com/docs/remote/containers-advanced#_adding-a-nonroot-user-to-your-dev-container
# for more info.
ARG USER_UID=1334627004
ARG USER_GID=$USER_UID

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    sudo git openssh-client vim \
    && groupadd --gid $USER_GID $USERNAME \
    && useradd --no-log-init --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && chown -R $USER_UID:$USER_GID /app

USER $USERNAME
