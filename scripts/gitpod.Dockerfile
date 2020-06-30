FROM gitpod/workspace-full

USER gitpod

RUN echo 'unset PIP_USER' >> ~/.bashrc

USER root

RUN apt-get -q update && \
  apt-get install -yq tmux libboost-all-dev build-essential swig && \
  rm -rf /var/lib/apt/lists/* && \
  pyenv global $(pyenv global | grep 3\\.) && \
  curl -sSL "https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-unknown-linux-gnu.tar.gz" \
    | tar -xvz && \
  echo '22699e16e71f07ff805805d26ee86ecb9b1052d7879350f7eb9ed87beb0e6b84fbb512963d01b75cec8e80532e4ea29a  tokei' \
    | sha384sum -c - && \
  mv tokei /usr/bin/
