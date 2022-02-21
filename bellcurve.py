# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 20:03:15 2021

"""

import csv
import matplotlib.pyplot as plt
import numpy as np
with open('Book1.csv', newline='') as f: # Open mark data for a particular subject
    reader = csv.reader(f)
    data = list(reader)


print(data)
average_list = [] ## list of difficulties
for i in range(0,len(data)):
    average_list.append(round(float(data[i][0]),2))
    ## extracts diffculties from csv

plt.hist(totalMarkList, bins = 10) ## plots a histogram
plt.title("Specialist")
plt.show()    
    
print(np.mean(difficulty_list)) ##gives mean difficulty
print(np.median(difficulty_list)) ## give median difficulty
print(np.std(difficulty_list))

np.mean(average_list) ##gives mean difficulty
np.median(average_list) ## give median difficulty
np.std(average_list)

def prob(lst, mini, maxi): ## a probability CDF
    ctr = 0
    for x in lst:
        if mini<= x <=maxi:
            ctr += 1
    return ctr/len(lst)
        
prob(totalMarkList, 0.8, 1)







