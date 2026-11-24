#!/usr/bin/env bash
# OhMyGame 을 소스로(daemon + 웹 화면) 세션과 떨어진 프로세스로 띄우고 끈다.
# 쓰는 법: scripts/mac-dev.sh start|stop|status   화면: http://127.0.0.1:43120
set -u
cd "$(dirname "$0")/.."
PID_FILE=.mac-dev.pid
LOG=.mac-dev.log

running() { [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; }

case "${1:-status}" in
  start)
    if running; then echo "이미 켜져 있음 (pid $(cat "$PID_FILE"))"; exit 0; fi
    # setsid 가 없는 macOS 라 nohup + 새 프로세스 그룹(set -m)으로 띄운다
    ( set -m; nohup bun run dev > "$LOG" 2>&1 & echo $! > "$PID_FILE" )
    for _ in $(seq 1 90); do
      curl -sf -o /dev/null http://127.0.0.1:43120 && { echo "켜짐: http://127.0.0.1:43120 (로그 $LOG)"; exit 0; }
      running || { echo "꺼짐. 로그 끝:"; tail -20 "$LOG"; exit 1; }
      sleep 1
    done
    echo "90초 안에 응답 없음. 로그 끝:"; tail -20 "$LOG"; exit 1 ;;
  stop)
    if running; then pid=$(cat "$PID_FILE"); kill -- "-$pid" 2>/dev/null || kill "$pid"; sleep 1; fi
    pkill -f "src/daemon/server.ts --dev" 2>/dev/null
    pkill -f "vite.js --host 127.0.0.1 --port 43120" 2>/dev/null
    rm -f "$PID_FILE"; echo "꺼짐" ;;
  status)
    if running; then echo "켜짐 (pid $(cat "$PID_FILE")) http://127.0.0.1:43120"; else echo "꺼짐"; fi ;;
  *) echo "쓰는 법: $0 start|stop|status"; exit 2 ;;
esac
