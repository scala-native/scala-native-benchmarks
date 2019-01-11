#!/usr/bin/env bash
echo $$ | tee .pid

if [ -f jobs.sh ]; then
  ./jobs.sh
fi

rm .pid