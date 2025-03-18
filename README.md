<h1 align="center">RoboCapture</h1>

<p align="center"><i>Tool for defining and deploying pipelines for audio/video processing.</i></p>

<hr>

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

[![GitHub commits](https://badgen.net/github/commits/fgrhlm/robocapture)](https://GitHub.com/fgrhlm/robocapture/commit/)

[![GitHub latest commit](https://badgen.net/github/last-commit/fgrhlm/robocapture)](https://GitHub.com/fgrhlm/robocapture/commit/)

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)

<hr>

- [Installation](#installation)
  - [Linux](#linux)
  - [Docker](#docker)
  - [ROS](#ros)
- [Configuration](#config)
  - [General](#general)
  - [Audio](#audio)
  - [Video](#video)
  - [External Workers](#ext_workers)
      - [YOLO](#yolo)
      - [Yunet](#yunet)
      - [Whisper](#whisper)
      - [MetaAudio](#meta_audio)
      - [MetaVideo](#meta_video)
      - [FrameB64](#frameb64)
- [Usage](#usage)
  - [Example Video](#ex_video)
      - [Configuration](#ex_video_conf)
      - [Running](#ex_video_run)
  - [Example Audio](#ex_audio)
      - [Configuration](#ex_audio_conf)
      - [Running](#ex_audio_run)

<hr>

<h2 id="installation">Installation</h2>

<h3 id="linux">Linux</h4>

<h4>Step 1: Installing Python</h4>

RoboCapture expects python version `3.12.9`. If your distro does not
provide a package for this specific version (it probably does not) you
can use one of the following methods to obtain the correct version:

**Using pyenv (Recommended)**

Install pyenv following the instructions [here](https://github.com/pyenv/pyenv?tab=readme-ov-file#a-getting-pyenv)

1. Navigate to source directory `cd robocapture/`

2. Get python 3.12.9 `pyenv install 3.12.9`

3. Robocapture ships with a `.python-version` file which should allow pyenv to automatically switch
to the correct python version when in the source directory. You can test that your environment
is using the correct py version by (while in source directory) running `python --version` and verifying
that the output reads `Python 3.12.9`

**Manual Installation**

Follow official instructions [here](https://www.python.org/downloads/release/python-3129/)

**Building from source**

Follow official instructions [here](https://docs.python.org/3.12/using/unix.html#building-python)

<h4>Step 2: Python venv</h4>

Create and activate virtualenv:

`python -m venv venv && source venv/bin/activate`

<h4>Step 3: Install dependencies</h4>

`pip install -r requirements.txt`

<h3 id="docker">Docker</h4>

<h4>WIP</h4>

<h3 id="ros">ROS</h3>

<h4>WIP</h4>

<hr>

<h2 id="config">Configuration</h2>

<h3 id="general">General</h3>

`server_type`: Decides the root worker. Can be `"audio"` or `"video"`

`device`: Input device

`on_data`: List of workers to be executed on hook `on_data`

`on_save`: List of workers to be executed on hook `on_save`

`socket`: Address info for websocket.

`log`: Logging configuration.

<h3 id="workers">Workers</h3>

`enabled`: On/Off.

`name`: Human readable worker name.

`path`: Path to worker module.

`config`: Worker specific config.

<h3 id="socket">Socket</h3>

`host`: Hostname.

`port`: Port.

<h3 id="audio">Audio</h3>

`device`: Input device index. Use script `list_dev_audio` to find device index.

More on the following options [here](https://python-sounddevice.readthedocs.io/en/0.5.1/api/streams.html#sounddevice.Stream)

`sample_rate`: Stream sample rate.

`channels`: Stream no. of channels.

`blksize`: Number of frames per block.

RCAudio specific

`max_clip_len`: Max clip length.

`mode`: Can be `voice_activity` or `normal`

`rec_threshold`: Signal level at which to activate recording.

`rec_hold`: Wait `rec_hold` seconds before stopping recording after activity has stopped.

<h3 id="video">Video</h3>

`device`: Input, look [here](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html)

<h3 id="ext_workers">External Workers</h3>

<h4 id="yolo">Yolo</h4>

<h4 id="yunet">Yunet</h4>

<h4 id="whisper">Whisper</h4>

<h4 id="meta_audio">Meta Audio</h4>

<h4 id="meta_video">Meta Video</h4>

<h4 id="frameb64">FrameB64</h4>

<hr>

<h2 id="usage">Usage</h2>

<h3 id="ex_video">Example Video:</h3>

<h4 id="ex_video_conf">Configuration</h4>

<h4 id="ex_video_run">Running</h4>

<h3 id="ex_audio">Example Audio:</h3>

<h4 id="ex_audio_conf">Configuration</h4>

<h4 id="ex_audio_run">Running</h4>
