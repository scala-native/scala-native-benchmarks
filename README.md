# Scala Native Benchmarks

This repo includes work-in-progress modernization of
Scala Native benchmarks. Unlike the previous infrastructure
we compile every single benchmark in its own isolated binary.
The results are recorded over multiple runs, not just
multiple iterations. The results for each iteration are dumped
as-is and summarized in a separate post-processing step.

## Running benchmarks

```
python scripts/run.py
```

## Creating result summary

```
python scripts/summary.py
```

The reports can be viewed in the `reports` directory.

## Advanced use

### Comparing specific versions

You can run just the configurations you are interested in
```bash
scripts/run.py stable latest
```

Compare the lastest `stable` relesea vs `latest` snapshot
```bash
REPORT=$(scripts/summary.py stable latest)
```

### Comparing an experimental feature with latest from master
1. build `scala-native` from latest master
2. run the benchmark for it
```bash
scripts/run.py latest
```
3. build `scala-native` from your branch
4. specify a suffix to identify it
```bash
NAME=PR9001-adding-a-kitchen-sink
```
5. run the benchmark and get the summary report
```bash
scripts/run.py --suffix "$NAME" latest &&
REPORT=$(scripts/summary.py --comment "$NAME" latest latest_"$NAME")
```

## Persisting reports
The following commands assume that you have a git repository checked out at `gh-pages` under `../scala-native-benchmark-results`.

Also that there is an executable script `just-upload.sh` in the root of that repository.
```bash
#just-upload.sh


#!/bin/bash
# move to the directory of the script
cd $(dirname "$0")

git add . &&
git commit -m "automated commit" && git push
```

### saving experiment data
```bash
cp -r results/ ../scala-native-benchmark-results &&
../scala-native-benchmark-results/just-upload.sh
```

### restoring experiment data
```bash
cp -r ../scala-native-benchmark-results results/
```

### uploading a report
```bash
mkdir -p ../scala-native-benchmark-results/reports
cp -r "$REPORT" ../scala-native-benchmark-results/reports &&
../scala-native-benchmark-results/just-upload.sh
```