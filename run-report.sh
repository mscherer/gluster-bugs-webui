#!/bin/bash
#
# This script is used by a cron job to run the report on a regular basis and
# refresh the data in a place where the apache server to pick up
#
# Create a symlink under /etc/cron.daily/ and this script will do the rest.
#

# exit on failure
set -e

SELF="$(readlink -f ${0})"
WORKDIR="$(dirname "${SELF}")"

cd ${WORKDIR}

python gluster-bugs.py
mv bugs-refresh.json bugs.json
