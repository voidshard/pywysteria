#!/bin/bash

#
# Integration test suite launcher.
#
# You'll want to make sure you build the appropriate docker images first (build scripts are in
# the main Go repo) wysteria/docker/images/
#
# These tests explicitly check network functions & compatibility with the server build(s).
#

# set fail on error
set -eu


# ------------------ globals
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SLEEP_TIME=2
PYTHON=python3.6
TEST_DIR=${DIR}"/tests"
PY_DIR=${DIR}"/../../"
# ------------------


# add local wysteria python lib to the python path
export PYTHONPATH=${PY_DIR}:${PYTHONPATH}

# ------------------ functions
dotest () {
    # Args:
    #    (1) service to launch (as defined in docker-compose)

    echo "> running test:" $1

    docker-compose up -d $1

    # sleep for a bit to allow things to start up
    sleep ${SLEEP_TIME}

    # permit failures
    set +e

    # throw it over to pytest
    ${PYTHON} -m pytest ${TEST_DIR} -vvs

    # set fail on error
    set -eu

    docker-compose down
}
# ------------------


# ------------------ start
export WYSTERIA_CLIENT_INI=test-nats.ini
dotest "local_wysteria_nats"

export WYSTERIA_CLIENT_INI=test-grpc.ini
dotest "local_wysteria_grpc"
