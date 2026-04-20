#!/bin/bash
# Secsmart_Reskin_Tool HTTP Server Startup Script
# Static file server using Python 3

PORT=47191
WORKDIR="/opt/SECSMART_MOD_PIFU/MULTI_AGENT/logo_resource/Secsmart_Reskin_Tool"
LOG="${WORKDIR}/server.log"
PIDFILE="${WORKDIR}/server.pid"

cd "$WORKDIR"

start() {
    if [ -f "$PIDFILE" ]; then
        OLD_PID=$(cat "$PIDFILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            echo "Server already running (PID: $OLD_PID)"
            return 1
        fi
        rm -f "$PIDFILE"
    fi

    nohup python3 "${WORKDIR}/server.py" >> "$LOG" 2>&1 &

    echo $! > "$PIDFILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Server started on port $PORT (PID: $(cat $PIDFILE))" >> "$LOG"
    echo "Server started on http://0.0.0.0:$PORT (PID: $(cat $PIDFILE))"
}

stop() {
    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Server stopped (PID: $PID)" >> "$LOG"
            echo "Server stopped (PID: $PID)"
        fi
        rm -f "$PIDFILE"
    else
        echo "No PID file found, server may not be running"
    fi
}

status() {
    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Server is running (PID: $PID) on port $PORT"
            return 0
        else
            echo "Server is NOT running (stale PID: $PID)"
            return 1
        fi
    else
        echo "Server is NOT running (no PID file)"
        return 1
    fi
}

case "$1" in
    start)   start ;;
    stop)    stop ;;
    restart) stop; sleep 1; start ;;
    status)  status ;;
    *)       echo "Usage: $0 {start|stop|restart|status}" ;;
esac
