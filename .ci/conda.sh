#!/usr/bin/env bash
set -ex

SRC_ROOT=${SRC_ROOT:-"${PWD}"}
CONTAINER_NAME='conda_docker'
if [ $(docker inspect --format='{{.State.Running}}' ${CONTAINER_NAME} 2>/dev/null) = "true" ]; then
  echo "Container already running"
  echo $PWD
  docker exec ${CONTAINER_NAME} ./.ci/run.sh;
else
  echo "Starting new container"
  echo $PWD
  echo $SRC_ROOT
  sudo docker run --name $CONTAINER_NAME --rm -ti -v $SRC_ROOT:$SRC_ROOT -w $SRC_ROOT --entrypoint /bin/bash continuumio/anaconda3 -c ./.ci/run.sh
fi
