#!/bin/bash

batches=2000
batchSize=1
input=""
output=""

for config in $@; do
    echo $config
    binariesDir="binaries/${config}"
    if [[ ! -d $binariesDir ]]; then
        echo "binaries for $config do not exists, skipping"
    else
        for bin in $(ls $binariesDir); do
            echo ${bin}
            outputDir="results/${config}/${bin}"
            outputPath="${outputDir}/time_out"
            usagePath="${outputDir}/memory_usage"
            input=`cat input/${bin}`
            output=`cat output/${bin}`
            rm -rf $usagePath
            for i in $(seq 1 3); do
                /bin/time -v -o ${outputPath} $binariesDir/$bin $batches $batchSize "$input" "$output" > /dev/null
                cat ${outputPath} | grep "Maximum resident set size" -| awk '{print $NF}' >> "${outputDir}/memory_usage"
            done
        done
    fi

done