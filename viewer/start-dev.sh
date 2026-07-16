#!/bin/bash
# Bash script to start both the Neo4j API server and Vite dev server

echo "Starting Neo4j Graph Explorer..."
echo ""

# Check if server dependencies are installed
if [ ! -d "server/node_modules" ]; then
    echo "Installing server dependencies..."
    cd server
    npm install
    cd ..
fi

# Check if viewer dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing viewer dependencies..."
    npm install
fi

echo ""
echo "Starting servers..."
echo "  - Neo4j API: http://localhost:3001"
echo "  - Vite Dev:  http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Trap Ctrl+C to cleanup
trap 'echo "Stopping servers..."; kill $API_PID $VITE_PID; exit' INT

# Start both servers
cd server && node neo4j-api.js &
API_PID=$!

cd .. && npm run dev &
VITE_PID=$!

# Wait for both processes
wait
