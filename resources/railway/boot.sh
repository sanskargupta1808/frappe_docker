#!/bin/bash

set -e

if [ "${RAILWAY_SINGLE_SERVICE:-}" = "1" ]; then
  exec /usr/local/bin/railway-entrypoint.sh
fi

exec "$@"
