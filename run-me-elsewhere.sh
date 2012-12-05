python logging_server.py 1&>experiment-results/personal-naive.log &
python fake_sensors.py 5 15 &
python fake_clients.py 1 5 &
