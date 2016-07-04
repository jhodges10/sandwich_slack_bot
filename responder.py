import csv
import subprocess
from fuzzywuzzy import fuzz,process

stdin = args


responses set-up
reader = csv.reader(open('responses.csv', 'r'))
qanda = {}
for row in reader:
   k, v = row
   qanda[k] = v



while True:
	if message.contains('lunch'):
	qanda[v] = 