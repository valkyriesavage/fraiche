#!/bin/sh

ssh pi@169.229.63.33 "ls"
# Note - if you tried to run and didn't get past here, remember to ssh-copy-id to the pi

python logging_server.py 1&>experiment-results/personal-naive.log &
echo $! > logging_server_pid
ssh pi@169.229.63.33 "/home/pi/fraiche/run-me-on-pi.sh `</dev/null` >nohup.out 2>&1 &"
python fake_sensors.py 5 15 &
echo $! > fake_sensors_pid
python fake_clients.py 1 5 5 &
echo $! > fake_clients_pid

sleep 30

kill `cat logging_server_pid`
kill `cat fake_sensors_pid`
kill `cat fake_clients_pid`
ssh pi@169.229.63.33 "killall python"
