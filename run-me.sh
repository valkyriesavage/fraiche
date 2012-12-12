#!/bin/sh

ssh pi@169.229.63.33 "ls"
# Note - if you tried to run and didn't get past here, remember to ssh-copy-id to the pi

for scheduler in "naive" "periodic" "hybrid" "load" "sensor" "predictive"
do
  for gardentype in "personal" "farm" "community"
  do
    echo "$gardentype $scheduler:::::::"
    if [ "$gardentype" == "personal" ]; then
      sensornum=5
      clientnum=1
      plantsperclient=5
    elif [ "$gardentype" == "farm" ]; then
      sensornum=100
      clientnum=1
      plantsperclient=100
    else # "$gardentype" == "community"
      sensornum=99
      clientnum=33
      plantsperclient=3
    fi

    sensordelay=15
    clientdelay=5

    cmdpi="python server.py --scheduler=$scheduler --freshness=$gardentype-$scheduler >>nohup-$gardentype-$scheduler.out 2>&1 &"
    ssh pi@169.229.63.33 "cd fraiche; echo $cmdpi > nohup-$gardentype-$scheduler.out; $cmdpi"
    sleep 5
    python fake_sensors.py $sensornum $sensordelay &
    echo $! > fake_sensors_pid
    python fake_clients.py $clientnum $plantsperclient $clientdelay 1&>experiment-results/$gardentype-$scheduler.log &
    echo $! > fake_clients_pid

    sleep 900

    kill `cat fake_sensors_pid`
    kill `cat fake_clients_pid`
    kill `ps aux | grep firefox | cut -d " " -f 3`
    ssh pi@169.229.63.33 "killall python"
    sleep 5
  done
done
rm fake_sensors_pid
rm fake_clients_pid
