#!/bin/bash

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    case $color in
        "green") echo -e "\033[32m$message\033[0m" ;;
        "red") echo -e "\033[31m$message\033[0m" ;;
        "yellow") echo -e "\033[33m$message\033[0m" ;;
        *) echo "$message" ;;
    esac
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null; then
        print_status "yellow" "⚠️  Port $port is in use. Attempting to free it..."
        lsof -ti :$port | xargs kill -9 2>/dev/null
        sleep 2
        if lsof -i :$port > /dev/null; then
            print_status "red" "❌ Failed to free port $port"
            return 1
        fi
    fi
    return 0
}

# Function to wait for a port to be available
wait_for_port() {
    local port=$1
    local retries=5
    while [ $retries -gt 0 ]; do
        if ! lsof -i :$port > /dev/null; then
            return 0
        fi
        retries=$((retries-1))
        sleep 1
    done
    return 1
}

# Change to the project root directory
cd "$(dirname "$0")"

print_status "yellow" "🛑 Stopping any running servers..."

# Kill any running servers
pkill -f "uvicorn"
pkill -f "http.server"
pkill -f "http-server"

# Wait for ports to be freed
sleep 2

# Check both ports
check_port 8000 || exit 1
check_port 8080 || exit 1

print_status "green" "🚀 Starting backend server..."
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
backend_pid=$!

# Wait for backend to start
sleep 2

# Check if backend started successfully
if ! ps -p $backend_pid > /dev/null; then
    print_status "red" "❌ Backend server failed to start. Check backend.log for details."
    exit 1
fi

print_status "green" "🌐 Starting frontend server..."
cd src/frontend
python3 -m http.server 8080 > ../../frontend.log 2>&1 &
frontend_pid=$!

# Wait for frontend to start
sleep 2

# Check if frontend started successfully
if ! ps -p $frontend_pid > /dev/null; then
    print_status "red" "❌ Frontend server failed to start. Check frontend.log for details."
    kill $backend_pid
    exit 1
fi

print_status "green" "✨ Both servers started successfully!"
print_status "green" "📱 Frontend: http://localhost:8080/index.html"
print_status "green" "🔌 Backend: http://localhost:8000"
print_status "yellow" "📝 Logs:"
print_status "yellow" "   Backend: tail -f backend.log"
print_status "yellow" "   Frontend: tail -f frontend.log"
print_status "yellow" "⚡ Press Ctrl+C to stop the servers"

# Wait for user interrupt
wait 