#!/bin/bash

echo "Setting up development environment..."

# Wait for workspace to be mounted
sleep 2

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "pyproject.toml not found in current directory: $(pwd)"
    echo "Contents of current directory:"
    ls -la
    echo "Trying to install from dev-requirements.txt..."
    if [ -f "dev-requirements.txt" ]; then
        pip install -r dev-requirements.txt
    else
        echo "Neither pyproject.toml nor dev-requirements.txt found!"
        exit 1
    fi
else
    echo "Installing project in development mode..."
    pip install -e .[dev]
fi

echo "Development environment setup complete!"