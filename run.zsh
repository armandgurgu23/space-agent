#!/bin/zsh

# Helper function to run backend
run_backend() {
    echo "running backend"
    uv run python -m src.backend.app
}

# Helper function to run frontend
run_frontend() {
    echo "running frontend"
    uv run python -m streamlit run src/frontend/chat_app.py
}

# Main function that orchestrates the script
main() {
    run_backend
    run_frontend
}

# Execute main function
main