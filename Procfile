web: export PYTHONPATH=src

web: gunicorn --bind 0.0.0.0:${PORT} src.app:app_server --preload --timeout 10