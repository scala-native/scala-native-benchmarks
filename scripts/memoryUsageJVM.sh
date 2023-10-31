#!/bin/bash

batches=2000
batchSize=1
input=""
output=""

benchmarks=(
    "bounce.BounceBenchmark"
    "list.ListBenchmark"
    "histogram.Histogram"
    "queens.QueensBenchmark"
    "richards.RichardsBenchmark"
    "permute.PermuteBenchmark"
    "deltablue.DeltaBlueBenchmark"
    "tracer.TracerBenchmark"
    "json.JsonBenchmark"
    "sudoku.SudokuBenchmark"
    "brainfuck.BrainfuckBenchmark"
    "cd.CDBenchmark"
    "kmeans.KmeansBenchmark"
    "nbody.NbodyBenchmark"
    "rsc.RscBenchmark"
    "gcbench.GCBenchBenchmark"
    "mandelbrot.MandelbrotBenchmark"
)

for config in $@; do
    echo $config
    cp "confs/${config}/build.properties" project/
    cp "confs/${config}/plugins.sbt" project/
    cp "confs/${config}/build.sbt" .

    # sbt assembly 
    runCmdTemplate=$(cat confs/${config}/run)
    for benchmark in ${benchmarks[@]}; do
        echo "$benchmark"    
        BENCH=$benchmark
        runCmd="$(eval echo $runCmdTemplate)"

        outputDir="results/${config}/${benchmark}"
        outputPath="${outputDir}/time_out"
        usagePath="${outputDir}/memory_usage"
        input=`cat input/${benchmark}`
        output=`cat output/${benchmark}`
        rm -rf $usagePath
        
        for i in $(seq 1 3); do
            /bin/time -v -o ${outputPath} ${runCmd} "$batches" "$batchSize" "$input" "$output" > /dev/null
            cat ${outputPath} | grep "Maximum resident set size" -| awk '{print $NF}' >> "${outputDir}/memory_usage"
        done
    done
done