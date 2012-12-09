import sys

total_time = 0
count = 0

for line in sys.stdin:
  if "time: " in line:
    total_time += float(line.split("time: ")[-1])
    count += 1

print "average : " + str(total_time/count)
