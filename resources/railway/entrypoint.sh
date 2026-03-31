#!/bin/bash

set -e

BENCH_DIR=/home/frappe/frappe-bench
SITES_DIR=${BENCH_DIR}/sites
BENCH=${BENCH_DIR}/env/bin/bench

cd ${BENCH_DIR}

mkdir -p ${SITES_DIR}
if [ ! -f ${SITES_DIR}/common_site_config.json ]; then
  echo '{}' >${SITES_DIR}/common_site_config.json
fi

ls -1 apps >${SITES_DIR}/apps.txt

if [ -n "${DB_HOST:-}" ]; then
  ${BENCH} set-config -g db_host "${DB_HOST}"
fi
if [ -n "${DB_PORT:-}" ]; then
  ${BENCH} set-config -gp db_port "${DB_PORT}"
fi
if [ -n "${REDIS_CACHE:-}" ]; then
  ${BENCH} set-config -g redis_cache "redis://${REDIS_CACHE}"
fi
if [ -n "${REDIS_QUEUE:-}" ]; then
  ${BENCH} set-config -g redis_queue "redis://${REDIS_QUEUE}"
  ${BENCH} set-config -g redis_socketio "redis://${REDIS_SOCKETIO:-${REDIS_QUEUE}}"
fi
if [ -n "${SOCKETIO_PORT:-}" ]; then
  ${BENCH} set-config -gp socketio_port "${SOCKETIO_PORT}"
else
  ${BENCH} set-config -gp socketio_port "9000"
fi
if [ -n "${CHROMIUM_PATH:-}" ]; then
  ${BENCH} set-config -g chromium_path "${CHROMIUM_PATH}"
else
  ${BENCH} set-config -g chromium_path "/usr/bin/chromium-headless-shell"
fi

if [ -n "${SITE_NAME:-}" ] && [ ! -d "${SITES_DIR}/${SITE_NAME}" ]; then
  if [ -z "${ADMIN_PASSWORD:-}" ]; then
    echo "ADMIN_PASSWORD is required to create a new site."
    exit 1
  fi
  if [ -z "${DB_ROOT_PASSWORD:-}" ]; then
    echo "DB_ROOT_PASSWORD is required to create a new site."
    exit 1
  fi

  DB_ROOT_USER=${DB_ROOT_USER:-root}
  DB_PORT_VALUE=${DB_PORT:-3306}
  INSTALL_APPS=${INSTALL_APPS:-erpnext,hrms,crm}

  ${BENCH} new-site "${SITE_NAME}" \
    --admin-password "${ADMIN_PASSWORD}" \
    --db-root-username "${DB_ROOT_USER}" \
    --db-root-password "${DB_ROOT_PASSWORD}" \
    --db-host "${DB_HOST}" \
    --db-port "${DB_PORT_VALUE}" \
    --no-mariadb-socket

  IFS=',' read -ra APPS <<<"${INSTALL_APPS}"
  for app in "${APPS[@]}"; do
    app=$(echo "${app}" | xargs)
    if [ -n "${app}" ]; then
      ${BENCH} --site "${SITE_NAME}" install-app "${app}"
    fi
  done
fi

exec /usr/bin/supervisord -c /etc/supervisord.conf
