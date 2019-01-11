#!/usr/bin/env bash

if [ -f .pid ]; then
  PID=$(cat .pid)
  kill -9 $PID
  rm .pid
fi

