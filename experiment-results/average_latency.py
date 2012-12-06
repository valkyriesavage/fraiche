import sys

count = 0
total = 0

for line in sys.stdin:
  if "time" in line and "logging_server" in line:
    time = float(line.split(":")[-1].strip())
    total += time
    count += 1

average = total / count

print "average latency : " + str(average)
