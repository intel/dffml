#!/usr/bin/env bash

echo "#!/usr/bin/env bash" > /usr/bin/cmd.sh
chmod 755 /usr/bin/cmd.sh
runit () {
  exec /usr/bin/cmd.sh
}
if [ "x$USER" != "x" ] && [ "x$UID" != "x" ]; then
  export HOME="/home/$USER"
  mkdir -p $HOME/.cache
  useradd -o -u $UID $USER
  chown $UID $HOME
  chown $UID $HOME/.cache
  runit () {
    exec su - $USER -m -s /usr/bin/cmd.sh
  }
fi

if [ "$1" == "pip" ]; then
  # Run pip. Used in case the user want to install something
  echo "$@" >> /usr/bin/cmd.sh
else
  # Run dffml otherwise.
  echo "dffml $@" >> /usr/bin/cmd.sh
fi

runit
