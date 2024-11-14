
work_dir := "build"
sdk_git_repo := "https://github.com/boto/botocore.git"
icon_pack_url := "https://d1.awsstatic.com/webteam/architecture-icons/q1-2022/Asset-Package_01312022.735e45eb7f0891333b7fcce325b0af915fd44766.zip"
website_bucket := "awsapichanges.com"


# Build a docker image
image:
    docker build -t apichanges:latest .

# Clone an aws sdk api repo for introspection.
sdk-repo: cache-get
    #!/usr/bin/env python3
    import json, subprocess, datetime, pathlib
    work_dir = pathlib.Path('{{ work_dir }}').resolve()
    repo_dir = work_dir/'sdk_repo'
    try:
        data = json.load(open(str(work_dir/'cache.json')))
        last = datetime.datetime.fromtimestamp(data[1]['created'])
        cmd = [
            'git',
            'clone',
            '--branch=master',
            '--shallow-since=%s' % last.isoformat(),
            '{{ sdk_git_repo }}',
            str(repo_dir)
        ]
    except (FileNotFoundError, IndexError):
        cmd = ['git', 'clone', '--branch=master', '{{ sdk_git_repo }}', str(repo_dir)]
    print("run %s" % (' '.join(cmd)))
    subprocess.check_call(cmd)

# Build the website
build: sdk-repo icons
    #!/usr/bin/env python3
    import logging
    from apichanges.sitebuild import Site
    from pathlib import Path
    logging.basicConfig(level=logging.INFO)
    builder_dir = Path('.').resolve()
    work_dir = Path('{{ work_dir }}').resolve()
    Site(
        work_dir / 'sdk_repo',
        work_dir / 'cache.json',
        builder_dir / 'templates',
        builder_dir / 'assets',
        work_dir / 'stage'
    )

# Publish the website
publish: build
    #!/bin/sh
    cd {{ work_dir }}
    aws s3 sync stage/ s3://{{ website_bucket }}


# Get the commit cache file
cache-get:
    #!/bin/sh
    mkdir -p {{ work_dir }}
    cd {{ work_dir }}
    aws s3 cp s3://{{ website_bucket }}/cache.json.zst .
    if [ -f cache.json.zst ]; then
        zstd -f -d cache.json.zst
    fi

# Upload the commit cache file
cache-upload:
    #!/bin/sh
    set -ex
    cd {{ work_dir }}
    zstd -f -19 cache.json
    aws s3 cp cache.json.zst s3://{{ website_bucket }}/cache.json.zst

# manual dev - trim cache file to simulate incremental
cache-trim:
    #!/usr/bin/env python3
    import json
    data = json.load(open('cache.json'))
    data = data[4:]
    with open('cache.json', 'w') as fh:
        json.dump(data, fp=fh)

# Place icons and build CSS for aws service icons.
icons:
    #!/usr/bin/env python3
    from apichanges.icons import IconBuilder
    IconBuilder('{{ icon_pack_url }}')
