FROM python:3.11-alpine

LABEL name="apichanges" \
    homepage="https://github.com/trustoncloud/api-change-log-for-aws" \
    maintainer="TrustOnCloud <dev@trustoncloud.com>"

ENV PATH="${PATH}:/root/.local/bin"
RUN apk add --no-cache libxml2-dev libxslt-dev python3-dev gcc build-base \
    openssl-dev libffi-dev wget unzip git curl zstd libgit2-dev && \
    wget -O - https://install.python-poetry.org | python3 && \
    pip3 install awscli

RUN adduser -D apichanges
COPY --chown=apichanges:apichanges . /home/apichanges

WORKDIR /home/apichanges/
RUN POETRY_VIRTUALENVS_CREATE=false poetry install --only main

USER apichanges
ENV LC_ALL="C.UTF-8" LANG="C.UTF-8" TZ=":/etc/localtime"
ENV PATH="${PATH}:/home/apichanges/.local/bin"

RUN wget -O - https://sh.rustup.rs | sh -s -- -y  \
    && $HOME/.cargo/bin/cargo install just \
    && mkdir -p $HOME/.local/bin/ \
    && ln -s $HOME/.cargo/bin/just $HOME/.local/bin/just

ENTRYPOINT ["/home/apichanges/.local/bin/just"]
