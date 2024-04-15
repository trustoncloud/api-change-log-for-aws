FROM python:3.8-bookworm

LABEL name="apichanges" \
    homepage="https://github.com/trustoncloud/api-change-log-for-aws" \
    maintainer="TrustOnCloud <dev@trustoncloud.com>"

RUN adduser --disabled-login apichanges
COPY --chown=apichanges:apichanges . /home/apichanges

RUN apt-get -q update  \
    && apt-get -q -y install \
        libxml2-dev libxslt1-dev libcairo2-dev build-essential libffi-dev \
        git curl unzip zstd libgit2-dev \
    && cd /home/apichanges \
    && pip3 install -r requirements.txt \
    && python3 setup.py develop

USER apichanges
WORKDIR /home/apichanges
RUN curl https://sh.rustup.rs -sSf > rustup.sh \
    && chmod 755 rustup.sh \
    && ./rustup.sh -y \
    && rm rustup.sh \
    && $HOME/.cargo/bin/cargo install just \
    && mkdir -p /home/apichanges/.local/bin/ \
    && ln -s $HOME/.cargo/bin/just /home/apichanges/.local/bin/just

ENV LC_ALL="C.UTF-8" LANG="C.UTF-8" TZ=":/etc/localtime" PATH="${PATH}:/home/apichanges/.local/bin"
ENTRYPOINT ["/home/apichanges/.local/bin/just"]
