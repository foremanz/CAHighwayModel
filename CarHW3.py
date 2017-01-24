#Created by UC Denver MCM Team 2017

import numpy as np
import sys
import math
import random
import time
from collections import deque
import queue
import numpy as np

#Car class object used for storing each vehicle information
class Car():
    #Initialize Car with Speed (MPH) and Lane number)
    def __init__(self, sp = None, Ln = None):
        self.speed = sp                     #Car Speed
        self.LnNum = Ln                     #Lane number car is in currently
        self.OldSp = self.speed             #Old speed value
        self.Human = True                   #If human or self driving
        self.WrckDtct = False               #If wreck detected infront
        self.LeadCar = None                 #Set a lead car
        self.LeadCarD = 0                   #Lead/Wreck distance ahead
        self.ReactTime = 2.0                #Reaction time of vehicle


    #Set car to self driving
    #Reaction time is quicker
    def setSelfDrive(self):
        self.Human = False
        self.ReactTime = 1.0

    #Set a new reaction time
    def setReactTime(self, X):
        self.ReactTime = X

    #Return Safe following distance
    def getBigD(self):
        BigD = max(1, self.speed)
        return BigD

    #Call to change the speed of the car
    #Saves previous speed values
    def chngSpd(self, Sp):
        self.OldSp = self.speed
        self.speed = Sp

    #Call to change the lane number of the car
    def chngLn(self, Ln):
        self.LnNum = Ln


    #If wreck detected, set WrckDtct true
    def setWrckCar(self, WCar, D):
        self.LeadCar = WCar
        self.LeadCarD = D
        self.WrckDtct = True

    #Remove wrecked vehicle
    def removeWrck(self):
        self.WrckDtct = False

    #Stores lead car object and distance
    def setLeadCar(self, LCar, D):
        self.LeadCar = LCar
        self.LeadCarD = D

    #Delete lead car
    def delLeadCar(self):
        self.LeadCar = None


    #This is for future logic,
    #So when logic is implemented later it can be adjusted accordingly
    def setOptSpeed(self):

        self.chngSpd(min(4, self.speed + 1))
        if self.speed < 0:
            self.chngSpd(0)

    # If car is at optimal following distance, match observed leading car speed while obeying speed limit
    # Self driving cars perfectly match, human drivers attempt to match stochastically
    # All speed methods determined by whether human driver or not
    def maintainSpeed(self):
        if self.speed == 0:
            return
        if self.Human:
            self.chngSpd(min(4, self.LeadCar.OldSp + np.random.randint(-1,1)))
        elif self.LeadCar.Human:
            self.chngSpd(min(4, self.LeadCar.OldSp))
        else:
            self.chngSpd(min(4, self.LeadCar.speed))
        if self.speed < 0:
            self.chngSpd(0)

    #If following to close or crash observed so down deterministicly
    def decreaseSpeed(self):
        if self.Human:
            self.chngSpd(max(self.speed - 2, self.LeadCar.OldSp - 1))
        elif self.LeadCar.Human:
            self.chngSpd(max(self.speed - 2, self.LeadCar.OldSp - 1))
        else:
            self.chngSpd(max(self.speed - 2, self.LeadCar.speed - 1))
        if self.speed < 0:
            self.chngSpd(0)

    #If road is open increase speed deterministicly
    def increaseSpeed(self):
        if self.Human:
            optDist = self.speed
            slackSpeed = (self.LeadCarD - optDist)
            self.chngSpd(min(4, self.speed + 1, self.LeadCar.OldSp + slackSpeed))
        elif self.LeadCar.Human:
            optDist = round(self.speed/2)
            slackSpeed = (self.LeadCarD - optDist)
            self.chngSpd(min(4, self.speed + 1, self.LeadCar.OldSp + slackSpeed))
        else:
            optDist = round(self.speed / 2)
            slackSpeed = (self.LeadCarD - optDist)
            self.chngSpd(min(4, self.speed + 1, self.LeadCar.speed + slackSpeed))
        if self.speed < 0:
            self.chngSpd(0)


class HighWayCreator():
    #Highway creator class, creates number of cells
    def __init__(self, Mile, NumLan):
        self.Dis = Mile
        self.Lane = NumLan
        self.Mtrx = None

    #Creates a matrix of all Zero's
    def makeHW(self):
        self.Mtrx = np.zeros((int(self.Lane), int(self.Dis)), dtype = object)

    #Set number of lanes
    def setLanes(self, Lane):
        self.Lane = Lane

    #Set number of Columns, Dstnc is in miles converts to 20 ft section cell
    def setCol(self, Dstnc):
        ft = Dstnc * 5280
        self.Dis = ft/20

#Highway class object used for modeling highway sections
class HighWay(HighWayCreator):
    #Initialize Highway is derived from HighWayCreator can access same methods and properties
    def __init__(self, Name=None, FlowRate=None):
        self.ID = Name
        self.Vol = FlowRate
        self.NumCars = 0
        self.NewAcc = 0
        self.Accident = {}
        self.AccTimer = 10
        self.exitq = deque()
        self.adjlist = []
        self.enterqLen = 0
        self.sumVel = 0
        self.beginSec = False
        self.endSec = False
    
    #Return average velocity of all cars in current segment	
    def getAvgVel(self):
        if self.NumCars == 0:
            return 0
        return (self.sumVel/self.NumCars)
    
    #If starting node mark true
    def setBegin(self):
        self.beginSec = True

    #If ending node mark true
    def setEnd(self):
        self.endSec = True

    #Hold list of adjacent segments of road
    def addAdj(self, HWid):
        self.adjlist.append(HWid)

    #Returns number of new accidents that occured per shifts
    def getNewAcc(self):
        return self.NewAcc

    #Reset the number of new accidents 
    def reNewAcc(self):
        self.NewAcc = 0

    #Determine the length of the Enter queue
    #This reflects how many cars trying to enter
    def setEnterQuLen(self, enterQ):
        self.enterqLen = len(enterQ)

    #Determine the total number of cars on the section of highway
    #Count the number trying to enter and exit as well as currently on the road
    def getTotalCars(self):
        return (self.NumCars + self.enterqLen + len(self.exitq))

    #Determine if car will exit on next iteration
    def exitChck(self, Vel, Xpos):
        futCell = Vel
        if (futCell + Xpos) > self.Dis:
            return True
        return False

    #Count of current accidents on the road obstructing traffic
    def getAccCount(self):
        return len(self.Accident)

    #Counter to remove accident from highway
    def AccCounter(self):
        self.AccTimer = np.random.exponential(2)
        AccMarks = self.Accident.keys()
        delPairs = []
        for pair in AccMarks:
            self.Accident[pair] -= 1
            if self.Accident[pair] == 0:
                x, y = pair
                delPairs.append(pair)
                self.Mtrx[x, y] = 0

        for pr in delPairs:
            del self.Accident[pr]

    #Method to determine if there is available room for car to exit this section
    #If the entry Queue is full for the next segment, it is assumed the next segment is full
    def passHW(self, edgeD):
        count = 0
        while self.exitq:
            try:
                k = self.exitq.popleft()
            except IndexError:
                break
            trackprob = 0

            p = np.random.uniform(0, 1, 1)

            totalvol = 0

            for hw in self.adjlist:
                entryq, vol = edgeD[hw]
                totalvol += vol

            for hw in self.adjlist:
                entryq, vol = edgeD[hw]
                trackprob += vol / totalvol

                if p < trackprob:
                    if len(entryq) > 2*self.Lane:
                        count += 1
                        self.exitq.append(k)
                        break

                    entryq.append(k)
                    edgeD[hw] = (entryq, vol)
                    count += 1
                    break

            if count == self.Lane:
                break

    #Update the car positions on the highway
    #Starts at end of row works back
    def upDateHW(self):
        Lanes, Pos = self.Mtrx.shape
	
	#Updates all velocities first, before moving vehicles
        #Update Velocities loop
        for y in range(Lanes):
            for x in reversed(range(Pos)):
                if self.Mtrx.item((y,x)) != 0 and self.Mtrx.item((y,x)) is not '+':
                    CurCar = self.Mtrx.item((y,x))
                    self.sumVel -= CurCar.speed

                    #If no lead car, meaning no car infront to influence decisions set opt speed
                    if CurCar.LeadCar == None:
                        CurCar.setOptSpeed()
                        if self.exitChck(CurCar.speed, x):
                            if len(self.exitq) > (2*self.Lane):
                                ExitRamp = Car(3, y)
                                ExitRamp.chngSpd(3)
                                CurCar.setLeadCar(ExitRamp, 4)		#Done so car can adjust entering new system
                                CurCar.decreaseSpeed()
                        self.Mtrx[y,x] = CurCar

                    #Else we know lead car exists and will influence velocity
                    else:
                        LdCar = CurCar.LeadCar
                        LdCarD = CurCar.LeadCarD
                        LdCarSpd = LdCar.speed
                        optDist = CurCar.speed

                        #If lead car is less then 20 feet away, adjust speed to become 20 feet away
                        if LdCarD < optDist:
                            CurCar.decreaseSpeed()
                        elif LdCarD == optDist:
                            CurCar.maintainSpeed()
                            if self.exitChck(CurCar.speed, x):
                                if len(self.exitq) > (2*self.Lane):
                                    ExitRamp = Car(3, y)
                                    CurCar.setLeadCar(ExitRamp, 4)
                                    CurCar.decreaseSpeed()
                        else:
                            CurCar.increaseSpeed()
                            if self.exitChck(CurCar.speed, x):
                                if len(self.exitq) > (2*self.Lane):
                                    ExitRamp = Car(3, y)
                                    CurCar.setLeadCar(ExitRamp, 4)
                                    CurCar.decreaseSpeed()

                        self.Mtrx[y,x] = CurCar
                    self.sumVel += CurCar.speed

	#Loop to move all vehicles
	#After velocities have all been adjusted we now move all vehicles
        for y in range(Lanes):
            for x in reversed(range(Pos)):
                if self.Mtrx.item((y,x)) != 0 and self.Mtrx.item((y,x)) is not '+':
                    CurCar = self.Mtrx.item((y,x))
                    CurMPH = CurCar.speed
                    if CurMPH == 0:
                        numCells = 0
                    else:
                        numCells = CurMPH

                    #Solely detects if collision will occur during movement, if it occurs programs stops
                    for NC in range(1, numCells+1):

                        #If larger then range continue car will exit this portion of highway
                        if (x+NC) > Pos - 1:
                            continue

                        #If empty continue
                        elif self.Mtrx.item((y,x+NC)) == 0:
                            continue

                        else:
                            self.Mtrx[y, x+NC] = '+'
                            self.Mtrx[y, x] = 0
#                            print('CRASH!')
#                            print('At lane {} position {}'.format(y,x+NC))
                            self.Accident[(y,x+NC)] = self.AccTimer
                            self.sumVel -= CurMPH
                            self.NewAcc += 1
                            self.NumCars -= 1
                            break
                    else:
                        if (x+numCells) > Pos -1:
                            # print('Car exited section {}'.format(self.ID))
                            self.exitq.append(CurCar)
                            self.Mtrx[y, x] = 0
                            self.sumVel -= CurCar.speed
                            self.NumCars -= 1
                        else:
                            #BigD = max(4, round((2*CurMPH*1.4667)/20))
                            BigD = CurCar.getBigD()
                            TrafCheck = False
                            SafeRange = self.Mtrx[y, (x+numCells+1):(x+numCells+BigD)]
                            for d, Hazard in enumerate(SafeRange):
                                TrafCheck = True
                                if Hazard != 0:
                                    if Hazard is '+':
                                        Wreck = Car(0, y)
                                        CurCar.setWrckCar(Wreck, d)
                                        self.Mtrx[y, x+numCells] = CurCar
                                        break
                                    else:
                                        CurCar.setLeadCar(Hazard, d)
                                        self.Mtrx[y, x+numCells] = CurCar
                                        break
                            else:
                                if TrafCheck:
                                    CurCar.removeWrck()
                                    CurCar.delLeadCar()
                                self.Mtrx[y, x+numCells] = CurCar

                            if numCells > 0:
                                self.Mtrx[y,x] = 0
    
    #Method for adding car into current segment
    def addCar(self, CurCar):

        MaxOpen = -2
        OptLane = 0

        #Used for simulating a reserved lane
        #Future adjustment it's own method 
        if not CurCar.Human:
            LookOut = self.Mtrx[0, 0:4]
            for x, chck in enumerate(LookOut):
                if chck != 0:
                    if x == 0:
                        return False
                    elif chck is '+':
                        Wreck = Car(0, 0)
                        CurCar.setWrckCar(Wreck, x)
                        self.Mtrx[0, 0] = CurCar
                        break
                    else:
                        CurCar.setLeadCar(chck, x)
                        self.Mtrx[0,0] = CurCar
                        break
            else:
                self.Mtrx[0,0] = CurCar

            self.NumCars += 1
            self.sumVel += CurCar.speed
            return True

	#Finds optimal lane to place new vehicle
        for x in range(1, self.Lane):
            OptLookAhead = self.Mtrx[x, 0:4]
            for y, checker in enumerate(OptLookAhead):
                if checker == 0:
                    if y > MaxOpen:
                        MaxOpen = y
                        OptLane = x
                else:
                    break

        if MaxOpen == -1:
            #print('Full')
            return False

        CurCar.chngLn(OptLane)

        BigD = CurCar.getBigD()

        if BigD > (MaxOpen+1):
            CloseOb = self.Mtrx[OptLane, (MaxOpen+1)]
            if CloseOb is '+':
                WrckCar = Car(0, OptLane)
                CurCar.setWrckCar(WrckCar, MaxOpen)
                self.Mtrx[OptLane, 0] = CurCar
            elif isinstance(CloseOb, Car):
                CurCar.setLeadCar(CloseOb, MaxOpen)
                self.Mtrx[OptLane, 0] = CurCar
            else:
                self.Mtrx[OptLane, 0] = CurCar
        else:
            self.Mtrx[OptLane, 0] = CurCar

        self.NumCars += 1
        self.sumVel += CurCar.speed
        return True

    #Place random obstructions
    def addObstrctn(self):
        #self.Mtrx[random.randint(0,2), random.randint(0,self.Dis)] = '+'
        self.Mtrx[0, 100] = '+'
        self.Mtrx[1, 100] = '+'
        self.Mtrx[2, 100] = '+'

    #Remove obstructions randomly placed
    def removeObstrctn(self):
        self.Mtrx[0, 100] = 0
        self.Mtrx[1, 100] = 0
        self.Mtrx[2, 100] = 0

    #Print highway section to screen
    # + represents any obstruction
    # 0 represents open cell
    # X represents car in cell
    def showHW(self):
        for i in range(self.Lane):
            ln = self.Mtrx[i,0:]
            print('Lane: '+ str(i+1))
            for c in ln:
                if c == 0:
                    print('0', end = '')
                elif c is '+':
                    print('+', end = '')
                else:
                    print('X', end = '')
            print('\n')

    #Add cars from entry queue into section
    def addFromEntryQ(self, entryQ):
        while entryQ:
            try:
                if not self.addCar(entryQ.popleft()):
                    break
            except IndexError:
                break

#Create dictionary of associated adjacent segments
def createDict(Dct, HWLst):
    for HW in HWLst:
        tempQ = deque()
        Dct[HW.ID] = (tempQ, HW.Vol)

#Main function, used to test class objects
def main():
    start = time.time()
    HW = HighWay('temp1', 40000)
    HW2 = HighWay('temp2', 40000)

    #Creates a blank highway 1 mile long (264, 20Ft cells) 3 lanes wide
    HW.setLanes(3)
    HW.setCol(1)
    HW.makeHW()
    HW.addAdj(HW2.ID)

    HW2.setLanes(3)
    HW2.setCol(1)
    HW2.makeHW()
    HW2.addAdj(HW.ID)

    HWList = [HW, HW2]

    #Starts with 3 cars in each lane
    HW.addCar(Car(4, 0))
    HW.upDateHW()
    HW.addCar(Car(4, 1))
    HW.upDateHW()
    HW.addCar(Car(4, 2))
    HW.upDateHW()

    HW2.addCar(Car(4, 0))
    HW2.upDateHW()
    HW2.addCar(Car(4, 1))
    HW2.upDateHW()
  #  HW2.addCar(Car(4, 2))
  #  HW2.upDateHW()

    TestDict = {}
    createDict(TestDict, HWList)

    #HW.addObstrctn()

    x = 0
    while x < 300:
        for highW in HWList:
            HW.AccCounter()
            entryQ, vol = TestDict[highW.ID]
            if x%2 == 0 and x < 70:
                entryQ.append(Car(4, random.randint(0,2)))
            highW.addFromEntryQ(entryQ)
            highW.upDateHW()
            highW.passHW(TestDict)
        for highW in HWList:
            entryQ, vol = TestDict[highW.ID]
            highW.setEnterQuLen(entryQ)
            print('HW {} has {} cars'.format(highW.ID, highW.getTotalCars()))
            print('HW {} has {} Acc.'.format(highW.ID, highW.getAccCount()))
        #Randomly adds 1 car per iteration (1 second) at random speed and random lane
        #HW.AccCounter()
        # if x == 200:
        #     HW.removeObstrctn()


        # if x%3 == 1:
        #     HW.addCar(Car(random.randint(55, 65),random.randint(0,2)))
        x += 1

    end = time.time()
    print(end-start)

if __name__=='__main__':main()

