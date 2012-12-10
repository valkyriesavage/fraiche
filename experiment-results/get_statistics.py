import math, sys

times = []

for line in sys.stdin:
  if "time: " in line:
    times.append(float(line.split("time: ")[-1]))

average = sum(times)/len(times)
print "average : " + str(average)

sum_of_squares = 0

for time in times:
  sum_of_squares += math.pow(time-average, 2)

std_deviation = math.sqrt(sum_of_squares/(len(times) - 1))

print "standard deviation : " + str(std_deviation)
