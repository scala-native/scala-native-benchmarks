# Scala Native Benchmarks

This repo includes work-in-progress modernization of
Scala Native benchmarks. Unlike the previous infrastructure
we compile every single benchmark in its own isolated binary.
The results are recorded over multiple runs, not just
multiple iterations. The results for each iteration are dumped
as-is and summarized in a separate post-processing step.

## Running benchmarks

Use Python version 3.

```
python scripts/run.py
```

## Viewing result summary

```
python scripts/summary.py
```
