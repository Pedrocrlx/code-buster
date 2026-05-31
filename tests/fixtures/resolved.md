# Docker Daemon Not Running in Devcontainer

**Resolved:** yes

## Problem
Docker daemon not running inside the devcontainer. docker ps returns Cannot connect to the Docker daemon.

## Solutions Tried
- Mounted /var/run/docker.sock from the host into the devcontainer

## Lesson
Remember: Mount /var/run/docker.sock from the host.

## Tags
docker, daemon, devcontainer, socket
