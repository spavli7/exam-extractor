from bs4 import BeautifulSoup
import re
from os import listdir
from os.path import isfile, join
import numpy as np
from scipy.optimize import curve_fit

# Initialise some arrays for analyses later
exam_difficulties = []
master_questions_arr = []

# Allow user to choose which folder to ultimately extract converted pdf->html files from.
yn = input("methods (y) or spec (n): ")
if yn.lower() == "y":
    folder = 'Methods-Exams'
else:
    folder = 'Spec-Exams'

allPDFs = [f for f in listdir(folder) if isfile(join(folder, f))] #Get list of files in spec-exams folder

for file in range(0,len(allPDFs)):
    #Setup Variables
    code = data = open(folder+"/"+allPDFs[file], encoding="utf8")
    html = code.read()
    allQuestions = []

    allTables = []
    allH3 = []


    #
    # EXTRACT DATA AND FILTER DATA
    #
    soup = BeautifulSoup(html, "html.parser")
    tabletag = soup.body.findAll('table')
        
    exam_id = soup.findAll('title')[0].text #Info about this exam
    #print(exam_id)

    #required funciton
    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)


    #filter tables
    for table in tabletag:
        if table.text.find("Marks") != -1:
            allTables.append(table)

    # Identify questions
    for i in range(2,6):
        h3tag = soup.body.findAll('h'+str(i))
        for h3 in h3tag: 
            if h3.text.find("Question") != -1 and hasNumbers(h3.text):
                allH3.append(h3)
        if len(allH3) > 0:
            break




    #
    # ACCOUNT FOR POSSIBLE HOLES IN THE DATA
    #
    if len(allH3) != len(allTables): #ONLY IF THERE IS NO 'One-to-one' RELATIONSHIP (else the data has holes)
        indexes_of_elements = [] #array to store 'positions' of each element in html

        # Fill array of positions for titles
        for i in range(0,len(allH3)):
            if html.count(allH3[i].text) > 1:
                if html.strip().find(allH3[i].text+"</h3") != -1:
                    indexes_of_elements.append([html.strip().find(allH3[i].text+"</h3"),"h3"])
                elif html.strip().find(allH3[i].text+"</a") != -1:
                    indexes_of_elements.append([html.strip().find(allH3[i].text+"</a"),"h3"])
                elif html.strip().find(allH3[i].text+"</h4") != -1:
                    indexes_of_elements.append([html.strip().find(allH3[i].text+"</h4"),"h3"])
                elif html.strip().find(allH3[i].text+"</h2") != -1:
                    indexes_of_elements.append([html.strip().find(allH3[i].text+"</h2"),"h3"])
            elif html.count(allH3[i].text) == 1:
                indexes_of_elements.append([html.strip().find(allH3[i].text),"h3"])

        previous_search_s = indexes_of_elements[0][0]
        index1 = 0

        # Fill array of positions for tables
        while index1 != -1:
            index1 = html.strip().find("<table",previous_search_s) #the left point

            if index1 != -1:
                indexes_of_elements.append([index1, "table"])
                previous_search_s = index1+1


        #Sort by order of appearance         
        indexes_of_elements = sorted(indexes_of_elements,key=lambda x: x[0])

        running_index = 0
        output = []

        #Iterate with a running index to find inconsistencies in the data
        for i in range(0,len(indexes_of_elements)):
            #print(indexes_of_elements[i][1] + " ----- " + str(indexes_of_elements[i][0]) + " ------- " + html[indexes_of_elements[i][0]:indexes_of_elements[i][0]+20])
            if indexes_of_elements[i][1] == "table":
                running_index = running_index - 1
                output.append("T")
                
            elif indexes_of_elements[i][1] != "table":
                running_index = running_index + 1
                output.append("H")
                
            if running_index == -1:
                #Mismatch has occured, input a dummy title
                output[len(output)-1] = "E"
                output.append("T")
                running_index = 0
            elif running_index == 2:
                #Mismatch has occured, input a dummy title
                output[len(output)-1] = "M"
                output.append("H")
                running_index = 1
                
        #Create one-to-one relationship array
        j1=0
        j2=0
        #print(output)
        for i in range(1, len(output)+1):
            if i % 2 == 0: #Every H-T pair
                if output[i-2] != "E" and output[i-1] != "M":
                    #print(j1,len(allH3),j2,len(allTables))
                    allQuestions.append([allH3[j1].text,allTables[j2]])
                    j1+=1
                    j2+=1
                elif output[i-2] == "E":
                    try:
                        allQuestions.append(["Missing (between " + allH3[j1-1].text + " and " + allH3[j1].text + ")",allTables[j2]])
                    except:
                        allQuestions.append(["Missing (Unknown location)",allTables[j2]])
                    j2+=1
                elif output[i-1] == "M":
                    allQuestions.append([allH3[j1].text,"Missing"])
                    j1+=1
                
    else:
        for i in range(0, len(allH3)):
            allQuestions.append([allH3[i].text,allTables[i]]) 


    #print(str(len(allQuestions)) + " Questions. From Hardest-Easiest:") #print the length (i.e-#of questions)



    #
    #DATA MANIPULATION
    #

    #Calculate difficulty ratings
    for i in range(0, len(allQuestions)):
        if allQuestions[i][1] != "Missing":
            marks = int(allQuestions[i][1].text.split('A')[0].strip()[-1])

            try:   
                marks = int(allQuestions[i][1].text.split('A')[0].strip()[-1])

                data = []
                table = allQuestions[i][1]

                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    data.append([ele for ele in cols if ele]) # Get rid of empty values
                

                percentages = data[1]
                average = 0
                mark = 0
                for j in range(1,marks+2):
                    average += (int(percentages[j])/100)*mark
                    mark += 1

                diff = average/marks
                allQuestions[i].append(diff)
            except:
                try:
                    avg = float(re.findall("\d\.\d", allQuestions[i][1].text)[0])
                    diff = avg/marks
                    allQuestions[i].append(diff)
                except:
                    try:
                        avg = float(allQuestions[i][1].text[len(allQuestions[i][1].text)-1:len(allQuestions[i][1].text)])
                        diff = avg/marks
                        if diff <= 1:
                            allQuestions[i].append(diff)
                        else:
                            print("error" + 1)
                    except:
                        avg = -1
                    
                    
        else:
            allQuestions[i].append(-2)

    #Sort allQuestions list by difficulty
    #allQuestions = sorted(allQuestions,key=lambda x: x[2])

    sum_diff = 0
    
    #Add exam year to allQuestions and display questions
    for i in range(0, len(allQuestions)):
        allQuestions[i].append(exam_id)
        
        #print(allQuestions[i][0], "-", allQuestions[i][2])
        sum_diff += allQuestions[i][2]

        master_questions_arr.append(allQuestions[i])
        
    avgDiff = sum_diff/len(allQuestions)

    exam_difficulties.append([avgDiff,exam_id])


    #print("Overall Difficulty: ", avgDiff)

master_questions_arr = sorted(master_questions_arr,key=lambda x: x[2]) #Sort all questions by difficulty

print("Loaded " + str(len(master_questions_arr)) + " total questions from " + str(len(exam_difficulties)) + " exams.")

user = input("Do you want questions with missing tables to be displayed? (y/n): ")

#Display ALL QUESTIONS:
for question in master_questions_arr:
    if question[2] == -2:
        #Lost data
        if user.lower() == "y":
            print(question[0], "-", "MISSING TABULAR DATA", " from: ", question[3])
    elif question[2] == -1 or question[2] > 1:
        #Edge Case
        print(question[0], " - EXTREME EDGE CASE, from: ", question[3])
    elif question[2] >= 0 and question[2] <= 1:
        print(question[0], "-", question[2], " from: ", question[3])



#Display difficulty distribution graph
import csv
import matplotlib.pyplot as plt
import numpy as np


average_list = []
for question in master_questions_arr:
    if question[2] > 0 and question[2] <= 1:
        average_list.append(question[2])

plt.hist(average_list, bins = 10)
plt.show()    
    
np.mean(average_list)
np.median(average_list)
def prob(lst, mini, maxi):
    ctr = 0
    for x in lst:
        if mini<= x <=maxi:
            ctr += 1
    return ctr/len(lst)
        
prob(average_list, 0, 0.597)

lst = [] 

def analyse(lst):
    plt.hist(lst, bins = 20, density=True)
    if yn.lower() == "y":
        plt.title("Methods*")
    else:
        plt.title("Specialist*")
    plt.xlabel("Proportion of Marks")
    plt.xticks(np.arange(0, 1.0, 0.1))
    plt.show() 
    print("Mean: " + str(np.mean(lst)))
    print("Median: " + str(np.median(lst)))
    print("Standard Deviation: " + str(np.std(lst)))

### Curve of Best Fit
from scipy.stats import norm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

# best fit of data
(mu, sigma) = norm.fit(average_list)

# the histogram of the data
n, bins, patches = plt.hist(average_list, 20, normed=1, facecolor='green', alpha=0.75)

# add a 'best fit' line
y = mlab.normpdf( bins, mu, sigma)
l = plt.plot(bins, y, 'r--', linewidth=2.5)

plt.xlabel('Proportion of Marks')
plt.title(r'$\mathrm{SpecExam1*:}\ \mu=%.3f,\ \sigma=%.3f$' %(mu, sigma))
plt.grid(True)
plt.show()  

#### EXPERIMENTAL Score simulation ####
## approximate method, attempt to simulate randomised exam scores. (Experimental)

avgMarkTotal = 2
trial = round(40/avgMarkTotal)
from random import *

totalMarkList = []
skew = 0.5 # This is a value between 0 and 1 which biases the probability that a given question is done correctly judging by how well someone did a previous question.
skew_list = []
for i in range(1,10000):
    phi = 0
    skew = 0.5
    for j in range(0,trial):
        alpha = 1 - normalvariate(mu,sigma)
        if alpha > 1:
            alpha = 1
        if alpha < 0:
            alpha = 0
        skew = (skew+alpha)/2
        phi+=2*skew*alpha*avgMarkTotal
    skew_list.append(skew)
    totalMarkList.append(phi/40)
   
    
###Display exam difficulties
##exam_difficulties = sorted(exam_difficulties,key=lambda x: x[0])
##
##for dif in exam_difficulties:
##    print(dif)
    
#dfficulty -1 means lost tabular data
#difficulty of -2 means edge case
