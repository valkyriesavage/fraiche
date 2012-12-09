#!/bin/sh

ssh pi@169.229.63.33 "ls"
# Note - if you tried to run and didn't get past here, remember to ssh-copy-id to the pi

for scheduler in "naive" "periodic" "hybrid" "load" "sensor" "predictive"
do
  for gardentype in "personal" "farm"
  do
    echo "$gardentype $scheduler:::::::"
    if [ $gardentype = "personal" ]
    then
      sensornum=5
      clientnum=1
      plantsperclient=5
    else
      sensornum=100
      clientnum=1
      plantsperclient=100
    fi
    cmdpi="python server.py --scheduler=$scheduler --freshness=$gardentype-$scheduler >>nohup-$gardentype-$scheduler.out 2>&1 &"
    ssh pi@169.229.63.33 "cd fraiche; echo $cmdpi > nohup-$gardentype-$scheduler.out; $cmdpi"
    sleep 5
    python logging_server.py 1&>experiment-results/$gardentype-$scheduler.log &
    echo $! > logging_server_pid
    python fake_sensors.py $sensornum 15 &
    echo $! > fake_sensors_pid
    python fake_clients.py $clientnum $plantsperclient 5 &
    echo $! > fake_clients_pid

    sleep 1800

    kill `cat logging_server_pid`
    kill `cat fake_sensors_pid`
    kill `cat fake_clients_pid`
    ssh pi@169.229.63.33 'killall python'
  done
done
