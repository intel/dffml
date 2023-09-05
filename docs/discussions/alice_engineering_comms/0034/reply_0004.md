# Troubleshooting Failed Whisper Transcriptions

- Try reducing the length of the recording to be transcribed in event of "Killed" (likely due to out of memory)

```console
$ ffmpeg -t 60 -i alan-watts-gnosticism.m4a -acodec copy alan-watts-gnosticism-first-60-seconds.m4a
ffmpeg version 5.1.1-static https://johnvansickle.com/ffmpeg/  Copyright (c) 2000-2022 the FFmpeg developers
  built with gcc 8 (Debian 8.3.0-6)
  configuration: --enable-gpl --enable-version3 --enable-static --disable-debug --disable-ffplay --disable-indev=sndio --disable-outdev=sndio --cc=gcc --enable-fontconfig --enable-frei0r --enable-gnutls --enable-gmp --enable-libgme --enable-gray --enable-libaom --enable-libfribidi --enable-libass --enable-libvmaf --enable-libfreetype --enable-libmp3lame --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenjpeg --enable-librubberband --enable-libsoxr --enable-libspeex --enable-libsrt --enable-libvorbis --enable-libopus --enable-libtheora --enable-libvidstab --enable-libvo-amrwbenc --enable-libvpx --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxml2 --enable-libdav1d --enable-libxvid --enable-libzvbi --enable-libzimg
  libavutil      57. 28.100 / 57. 28.100
  libavcodec     59. 37.100 / 59. 37.100
  libavformat    59. 27.100 / 59. 27.100
  libavdevice    59.  7.100 / 59.  7.100
  libavfilter     8. 44.100 /  8. 44.100
  libswscale      6.  7.100 /  6.  7.100
  libswresample   4.  7.100 /  4.  7.100
  libpostproc    56.  6.100 / 56.  6.100
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'alan-watts-gnosticism.m4a':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2mp41
    encoder         : Lavf58.24.101
  Duration: 00:51:37.36, start: 0.000000, bitrate: 129 kb/s
  Stream #0:0[0x1](und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 128 kb/s (default)
    Metadata:
      handler_name    : SoundHandler
      vendor_id       : [0][0][0][0]
Output #0, ipod, to 'alan-watts-gnosticism-first-60-seconds.m4a':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2mp41
    encoder         : Lavf59.27.100
  Stream #0:0(und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 128 kb/s (default)
    Metadata:
      handler_name    : SoundHandler
      vendor_id       : [0][0][0][0]
Stream mapping:
  Stream #0:0 -> #0:0 (copy)
Press [q] to stop, [?] for help
size=     948kB time=00:01:00.00 bitrate= 129.5kbits/s speed=7.14e+03x
video:0kB audio:938kB subtitle:0kB other streams:0kB global headers:0kB muxing overhead: 1.159434%
$ file alan-watts-gnosticism-first-60-seconds.m4a
alan-watts-gnosticism-first-60-seconds.m4a: ISO Media, Apple iTunes ALAC/AAC-LC (.M4A) Audio
$ python -uc 'import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"])' alan-watts-gnosticism-first-60-seconds.m4a
```


```console
$ ps faux
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
coder        1  0.0  0.0 751808  9176 ?        Ssl  Sep19   0:21 ./coder agent
coder     6052  0.0  0.0   6100  4016 pts/12   Ss   16:44   0:00  \_ -bash
coder     6391 34.7  0.2 4647032 731712 pts/12 Rl+  18:43   5:36  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6520  0.0  0.0   5996  3948 pts/13   Ss   18:56   0:00  \_ -bash
coder     6536  0.0  0.0   7648  3292 pts/13   R+   18:59   0:00      \_ ps faux
```

- Noticed the process is spending a lot of time sleeping.

```console
$ while test 1; do ps faux | grep whisper | grep -v grep | tee -a mem.txt; sleep 0.2; done
coder     6391 34.4  0.2 4647032 733600 pts/12 Rl+  18:43   6:27  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.4  0.2 4647032 733600 pts/12 Rl+  18:43   6:27  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.4  0.2 4647032 733600 pts/12 Sl+  18:43   6:27  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.4  0.2 4647032 733600 pts/12 Sl+  18:43   6:28  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.4  0.2 4647032 733600 pts/12 Rl+  18:43   6:28  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.4  0.2 4647032 733600 pts/12 Sl+  18:43   6:28  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.4  0.2 4647032 733600 pts/12 Rl+  18:43   6:28  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.4  0.2 4647032 733600 pts/12 Sl+  18:43   6:29  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.3  0.2 4647032 733600 pts/12 Sl+  18:43   6:29  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.4  0.2 4647032 733600 pts/12 Rl+  18:43   6:29  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.3  0.2 4647032 733600 pts/12 Rl+  18:43   6:29  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.4  0.2 4647032 733600 pts/12 Sl+  18:43   6:29  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.3  0.2 4647032 733600 pts/12 Rl+  18:43   6:29  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.3  0.2 4647032 733600 pts/12 Rl+  18:43   6:30  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.3  0.2 4647032 733600 pts/12 Rl+  18:43   6:30  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.3  0.2 4647032 733600 pts/12 Sl+  18:43   6:30  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.3  0.2 4647032 733600 pts/12 Sl+  18:43   6:30  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.3  0.2 4647032 733600 pts/12 Sl+  18:43   6:30  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.3  0.2 4647032 733600 pts/12 Rl+  18:43   6:30  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.3  0.2 4647032 733600 pts/12 Rl+  18:43   6:31  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.3  0.2 4647032 733600 pts/12 Rl+  18:43   6:31  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
coder     6391 34.3  0.2 4647032 733600 pts/12 Sl+  18:43   6:31  |   \_ /.pyenv/versions/3.9.13/bin/python -uc import sys, whisper; print(whisper.load_model("base").transcribe(sys.argv[-1])["text"]) alan-watts-gnosticism-first-60-seconds.m4a
```

- Some serious OOM happening here (guessing)

```console
$ time python -uc 'import sys, whisper; print(whisper.load_model("tiny.en").transcribe(sys.argv[-1], language="en")["text"])' alan-watts-gnosticism.m4a
/home/coder/.local/lib/python3.9/site-packages/whisper/transcribe.py:70: UserWarning: FP16 is not supported on CPU; using FP32 instead
  warnings.warn("FP16 is not supported on CPU; using FP32 instead")
Killed

real    1m21.526s
user    0m13.171s
sys     0m12.903s
```