#!/usr/bin/env bash

if [ -f .pid ]; then
  PID=$(cat .pid)
  kill -9 $(ps -s $PID -o pid=)
  rm .pid
fi

