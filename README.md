<h1 align="center">RoboCapture</h1>
<p align="center"><i>Tool for defining and deploying pipelines for audio/video processing.</i></p>
<hr>
<p align="center">
    [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
    [![GitHub commits](https://badgen.net/github/commits/fgrhlm/robocapture)](https://GitHub.com/fgrhlm/robocapture/commit/)
    [![GitHub latest commit](https://badgen.net/github/last-commit/fgrhlm/robocapture)](https://GitHub.com/fgrhlm/robocapture/commit/)
    [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)
</p>
<hr>
<p align="center">
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
</p>
<hr>
<h2 id="installation">Installation</h2>
<h3 id="linux">Linux</h4>
<h4>Step 1: Installing Python</h4>
<p>
RoboCapture expects python version `3.12.9`. If your distro does not
provide a package for this specific version (it probably does not) you
can use one of the following methods to obtain the correct version:
</p>
<p>
<b>Using pyenv (Recommended)</b>
Install following instructions [here](https://github.com/pyenv/pyenv?tab=readme-ov-file#a-getting-pyenv)

1. Navigate to source directory `cd robocapture/`

2. Get python 3.12.9 `pyenv install 3.12.9`

3. Robocapture ships with a `.python-version` file which should allow pyenv to automatically switch
to the correct python version when in the source directory. You can test that your environment
is using the correct py version by (while in source directory) running `python --version` and verifying
that the output reads `Python 3.12.9`
</p>
<p>
<b>Manual Installation</b>

Follow official instructions [here](https://www.python.org/downloads/release/python-3129/)
</p>
<p>
<b>Building from source</b>

Follow official instructions [here](https://docs.python.org/3.12/using/unix.html#building-python)
</p>
<h4>Step 2: Python venv</h4>
<p>
Create and activate virtualenv:

`python -m venv venv && source venv/bin/activate`
</p>
<h4>Step 3: Install dependencies</h4>
<p>
`pip install -r requirements.txt`
</p>
<h3 id="docker">Docker</h4>
<h4>WIP</h4>
<h3 id="ros">ROS</h3>
<h4>WIP</h4>
<hr>
<h2 id="config">Configuration</h2>
<h3 id="general">General</h3>
<p>
<span>`server_type`: Decides the root worker. Can be `"audio"` or `"video"`</span>
<span>`device`: Input device</span>
<span>`on_data`: List of workers to be executed on hook `on_data`</span>
<span>`on_save`: List of workers to be executed on hook `on_save`</span>
<span>`socket`: Address info for websocket.</span>
<span>`log`: Logging configuration.</span>
</p>
<h3 id="workers">Workers</h3>
<p>
<span>`enabled`: On/Off.</span>
<span>`name`: Human readable worker name.</span>
<span>`path`: Path to worker module.</span>
<span>`config`: Worker specific config.</span>
</p>
<h3 id="socket">Socket</h3>
<p>
<span>`host`: Hostname.</span>
<span>`port`: Port.</span>
</p>
<h3 id="audio">Audio</h3>
<p>
<span>`device`: Input device index. Use script `list_dev_audio` to find device index.</span>

More on the following options [here](https://python-sounddevice.readthedocs.io/en/0.5.1/api/streams.html#sounddevice.Stream)
<span>`sample_rate`: Stream sample rate.</span>
<span>`channels`: Stream no. of channels.</span>
<span>`blksize`: Number of frames per block.</span>

<span>`max_clip_len`: Max clip length.</span>
<span>`mode`: Can be `voice_activity` or `normal`</span>
<span>`rec_threshold`: Signal level at which to activate recording.</span>
<span>`rec_hold`: Wait `rec_hold` seconds before stopping recording after activity has stopped.</span>
</p>
<h3 id="video">Video</h3>
<span>`device`: Input, look [here](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html)</span>
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
