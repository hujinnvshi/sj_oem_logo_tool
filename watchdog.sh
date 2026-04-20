#!/bin/bash
# Secsmart_Reskin_Tool Watchdog
# Checks server health every 30s, auto-restarts if down
# Managed as a cron job

PORT=47191
WORKDIR="/opt/SECSMART_MOD_PIFU/MULTI_AGENT/logo_resource/Secsmart_Reskin_Tool"
START_SCRIPT="${WORKDIR}/start_server.sh"
WATCHDOG_LOG="${WORKDIR}/watchdog.log"
MAX_LOG_LINES=500

check_and_restart() {
    # Health check via HTTP request
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:${PORT}/" 2>/dev/null)

    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
        return 0
    fi

    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] Server check FAILED (HTTP: $HTTP_CODE), restarting..." >> "$WATCHDOG_LOG"

    # Try to restart
    bash "$START_SCRIPT" restart >> "$WATCHDOG_LOG" 2>&1
    sleep 2

    # Verify restart
    HTTP_CODE2=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:${PORT}/" 2>/dev/null)
    if [ "$HTTP_CODE2" = "200" ] || [ "$HTTP_CODE2" = "301" ] || [ "$HTTP_CODE2" = "302" ]; then
        echo "[$TIMESTAMP] Restart SUCCESS" >> "$WATCHDOG_LOG"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Restart FAILED (HTTP: $HTTP_CODE2)" >> "$WATCHDOG_LOG"
    fi
}

# Rotate log if too large
if [ -f "$WATCHDOG_LOG" ]; then
    LINES=$(wc -l < "$WATCHDOG_LOG")
    if [ "$LINES" -gt "$MAX_LOG_LINES" ]; then
        tail -200 "$WATCHDOG_LOG" > "${WATCHDOG_LOG}.tmp" && mv "${WATCHDOG_LOG}.tmp" "$WATCHDOG_LOG"
    fi
fi

check_and_restart
