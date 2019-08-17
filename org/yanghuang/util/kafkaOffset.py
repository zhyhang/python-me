# coding=UTF-8
import sys
import json

jsonFile = '/home/zhyhang/sh/cla_test_2_offset.2.json'
if len(sys.argv)>1:
    jsonFile = sys.argv[1]

jsonOffset = json.load(open(jsonFile))
partitions = jsonOffset.get('partitions')

offsetSum = 0
for partition in partitions:
    offsetSum += partition.get('newest')
    print(partition)
print(offsetSum)
