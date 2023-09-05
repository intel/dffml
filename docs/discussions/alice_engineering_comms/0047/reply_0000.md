## 2022-10-06 @pdxjohnny Engineering Logs

- https://comunica.github.io/Article-ISWC2018-Demo-GraphQlLD/
- https://c2pa.org/principles/
- https://c2pa.org/specifications/specifications/1.0/guidance/_attachments/Guidance.pdf
- https://c2pa.org/specifications/specifications/1.1/index.html
- https://koxudaxi.github.io/datamodel-code-generator/
  - for generating data models (classes) for use with dataflows/overlays.
- https://twitter.com/mfosterio/status/1578191604585680896
  - > I pulled some resources out of my research doc around Linked Data RDF Data Shaping and Framing for anyone wanting to look into the Semantic Web methods:
    > - [https://ruben.verborgh.org/blog/2019/06/17/shaping-linked-data-apps/…](https://t.co/UqHwbufnfM)
    > - [https://weso.es/shex-author/](https://t.co/Ad4wA1Kne7)
    > - [https://w3.org/TR/json-ld11-framing/…](https://t.co/hm5eHwXKCH)
    > - [https://google.github.io/schemarama/demo/…](https://t.co/GKPGJpJGgv)

```powershell
> Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
> pip install -U pip setuptools wheel pyenv-win --target %USERPROFILE%\\.pyenv
> [System.Environment]::SetEnvironmentVariable('PYENV',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
> [System.Environment]::SetEnvironmentVariable('PYENV_ROOT',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
> [System.Environment]::SetEnvironmentVariable('PYENV_HOME',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
> [System.Environment]::SetEnvironmentVariable('path', $env:USERPROFILE + "\.pyenv\pyenv-win\bin;" + $env:USERPROFILE + "\.pyenv\pyenv-win\shims;" + [System.Environment]::GetEnvironmentVariable('path', "User"),"User")
> [System.Environment]::SetEnvironmentVariable('path', $env:USERPROFILE + "\Downloads\ffmpeg-2022-10-02-git-5f02a261a2-full_build\bin;" + [System.Environment]::GetEnvironmentVariable('path', "User"),"User")
```

- References
  - https://www.gyan.dev/ffmpeg/builds/
    - https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-2022-10-02-git-5f02a261a2-full_build.7z
  - https://pyenv-win.github.io/pyenv-win/#installation
  - https://gist.github.com/nateraw/c989468b74c616ebbc6474aa8cdd9e53
    - stable diffusion walk over outputs