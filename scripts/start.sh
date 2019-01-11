#!/usr/bin/env bash
echo $$ | tee .pid

if [ -f jobs.sh ]; then
  mkdir -p logs
  ./jobs.sh | tee logs/job_$(date +%Y%m%d_%H%M%S).log
fi

rm .pid