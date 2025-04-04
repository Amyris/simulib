ARG SUNDIALS_VERSION=5.1.0
ARG GLPK_VERSION=4.65
ARG EXTRAS="dfba"

FROM ghcr.io/amyris/sundials-glpk-pybind:sundials-${SUNDIALS_VERSION}-glpk-${GLPK_VERSION} as dev
COPY --from=ghcr.io/astral-sh/uv:0.6.11 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml ./

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
ARG USER_UID=1000
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
