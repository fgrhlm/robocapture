#!/bin/bash
set -e

CPROFILE_DATA="${HOME}/.robocapture/logs/cprofile.out"

function main () {
    snakeviz "${CPROFILE_DATA}" 
}

main
