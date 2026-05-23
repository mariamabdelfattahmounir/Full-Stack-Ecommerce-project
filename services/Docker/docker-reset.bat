@echo off
echo ==========================================
echo Docker CLEAN RESET for E-Commerce Project
echo ==========================================

docker compose --env-file .env.docker down --volumes --remove-orphans
docker builder prune -af
docker volume prune -f

echo.
echo ==========================================
echo Rebuilding from scratch...
echo ==========================================
docker compose --env-file .env.docker build --no-cache

echo.
echo ==========================================
echo Starting fresh stack...
echo ==========================================
docker compose --env-file .env.docker up -d

echo.
echo ==========================================
echo Current containers
echo ==========================================
docker compose --env-file .env.docker ps