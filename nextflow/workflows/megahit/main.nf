#!/usr/bin/env nextflow

// Set output directory
params.output = "/assembly"

process MEGAHIT {
    publishDir params.output , mode: 'copy', overwrite: true
    input:
    path read1
    path read2

    output:
    path 'assembly/*', emit: assembly

    script:
    if (params.read_type == 2) {
        """
        megahit -1 ${read1} -2 ${read2} -o assembly
        """
    } else if (params.read_type == 1) {
        """
        megahit -r ${read1} -o assembly
        """
    } else {
        error 'Invalid value for read_type. Use 1 for single-end or 2 for paired-end.'
    }
}

workflow {
    if (params.read_type == 2) {
        // Paired-end reads: Two files passed via parameters
        read1_ch = Channel.fromPath(params.read1)
        read2_ch = Channel.fromPath(params.read2)

        // Execute assembly for paired-end reads
        MEGAHIT(read1_ch, read2_ch)

    } else if (params.read_type == 1) {
        // Single-end reads: One file passed via parameters
        read1_ch = Channel.fromPath(params.read1)

        // Execute assembly for single-end reads
        MEGAHIT(read1_ch, null)

    } else {
        error 'Invalid read_type parameter. Use 1 for single-end or 2 for paired-end.'
    }
}
