from python:3.8.1-buster

LABEL name="apichanges" \
    homepage="https://github.com/trustoncloud/api-change-log-for-aws" \
    maintainer="TrustOnCloud <dev@trustoncloud.com>"

RUN adduser --disabled-login apichanges
COPY --chown=apichanges:apichanges . /home/apichanges
RUN echo "deb http://deb.debian.org/debian buster-backports main" >> /etc/apt/sources.list

RUN apt-get -q update  \
    && apt-get -q -y install \
	libxml2-dev libxslt1-dev libcairo2-dev build-essential libffi-dev \
	git curl unzip zstd \
    && apt-get -y -t buster-backports install libgit2-dev \
    && cd /home/apichanges \
    && pip3 install -r requirements.txt \
    && python3 setup.py develop

RUN curl https://sh.rustup.rs -sSf > rustup.sh \
    && chmod 755 rustup.sh \
    && ./rustup.sh -y \
    && rm rustup.sh \
    && $HOME/.cargo/bin/cargo install just \
    && ln -s $HOME/.cargo/bin/just /usr/local/bin/just

USER apichanges
WORKDIR /home/apichanges
ENV LC_ALL="C.UTF-8" LANG="C.UTF-8" TZ=":/etc/localtime"
ENTRYPOINT ["/usr/local/bin/just"]
