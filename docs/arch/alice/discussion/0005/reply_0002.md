Let's combine this with the hangouts call center VNC stuff to get screen recordings, or maybe there is a VNC recorder, or an XServer that just streams to OGG. Or somethign esle. Look into to see if they ever got that vnc / qemu / over websockets with webui working, can't remember the project right now

```powershell
&"C:\Program Files\VideoLAN\VLC\vlc.exe" -I dummy screen:// :screen-fps=120.000000 :screen-caching=100 ":sout=#transcode{vcodec=theo,vb=800,scale=0,width=600,height=480,acodec=mp3}:http{mux=ogg,dst=127.0.0.1:8080/desktop.ogg}" :no-sout-rtp-sap :no-sout-standard-sap :ttl=1 :sout-keep
```