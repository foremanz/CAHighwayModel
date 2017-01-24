#Created by UC Denver MCM 2017 Team

import time
import Phas2
import CarHW3
import random
import tqdm

#Column headers of Provided Excel Files
ClmHdr = {
    'rId' : 'Route_ID',
    'sMile' : 'startMilepost',
    'eMile' : 'endMilepost',
    'avgD' : 'Average daily traffic counts Year_2015',
    'sLan' : 'Number of Lanes DECR MP direction ',
    'nLan' : 'Number of Lanes INCR MP direction',
    'com' : 'Comments',
    'rTyp' : 'RteType (IS= Interstate, SR= State Route)',
}

#Parse pandas DataFrame store as a State Highway Graph Object
def ParseAndStore(Data, InterS):
    for index, row in Data.iterrows():
        TempNd = Phas2.StrGrph()
        TempNd.setAdjN(row[ClmHdr['sMile']], row[ClmHdr['eMile']],
                       row[ClmHdr['avgD']], row[ClmHdr['nLan']],
                       row[ClmHdr['sLan']], row[ClmHdr['rTyp']])
        if row[ClmHdr['rId']] == 5:
            InterS[5].append(TempNd)
        elif row[ClmHdr['rId']] == 90:
            InterS[90].append(TempNd)
        elif row[ClmHdr['rId']] == 405:
            InterS[405].append(TempNd)
        else:
            InterS[520].append(TempNd)

#Create highway sections of INCR flow
def CreateHwNoFlSect(IntGLst):
    I5Sec = []
    S520Sec = []
    I405Sec = []
    I90Sec = []

    for HW, sections in IntGLst.items():
        for count, section in enumerate(sections):
            tempID = str(HW) + '_' + str(section.NodeA.MileMark)
            TempHW = CarHW3.HighWay(tempID, (section.AvgT/2))
            TempHW.setLanes(section.FlwN)
            TempHW.setCol(abs(section.NodeB.MileMark - section.NodeA.MileMark))
            TempHW.makeHW()
            if count == 0:
                TempHW.setBegin()
            #if last highway segment, no more adj. nodes
            if count < len(sections)-1:
                adjN = str(HW) + '_' + str(section.NodeB.MileMark)
                TempHW.addAdj(adjN)
            else:
                TempHW.setEnd()
                if HW == 5:
                    TempHW.addAdj('5_100.93')
                elif HW == 90:
                    TempHW.addAdj('90_1.94')
                elif HW == 405:
                    TempHW.addAdj('405_0.0')
                else:
                    TempHW.addAdj('520_0.0')

            if HW == 5 and section.NodeA.MileMark == 152.72:
                TempHW.addAdj('405_0.0')
            elif HW == 5 and section.NodeA.MileMark == 181.31:
                TempHW.addAdj('405_30.21')
            elif HW == 5 and section.NodeA.MileMark == 167.8:
                TempHW.addAdj('520_0.0')
            elif HW == 5 and section.NodeA.MileMark == 164.22:
                TempHW.addAdj('90_2.79')
            elif HW == 90 and section.NodeA.MileMark == 2.79:
                TempHW.addAdj('5_164.22')
            elif HW == 90 and section.NodeA.MileMark == 11.64:
                TempHW.addAdj('405_10.93')
            elif HW == 405 and section.NodeA.MileMark == 0:
                TempHW.addAdj('5_152.72')
            elif HW == 405 and section.NodeA.MileMark == 30.21:
                TempHW.addAdj('5_181.31')
            elif HW == 405 and section.NodeA.MileMark == 10.93:
                TempHW.addAdj('90_11.64')
            elif HW == 405 and section.NodeA.MileMark == 14.83:
                TempHW.addAdj('520_6.93')
            elif HW == 520 and section.NodeA.MileMark == 0:
                TempHW.addAdj('5_167.8')
            elif HW == 520 and section.NodeA.MileMark == 6.93:
                TempHW.addAdj('405_14.83')

            if HW == 5:
                I5Sec.append(TempHW)
            elif HW == 520:
                S520Sec.append(TempHW)
            elif HW == 405:
                I405Sec.append(TempHW)
            else:
                I90Sec.append(TempHW)

    HWList = [I5Sec, S520Sec, I405Sec, I90Sec]

    return HWList


#Initial random car seeder
#Before simulation runs populates highway sections with vehicles
def RandCarSeeder(HWList, frac):
    for HW in HWList:
        for x in range(random.randint(1,2)):
            tempCar = CarHW3.Car(4,random.randint(0,HW.Lane-1))
            if random.uniform(0,1) < frac:
                tempCar.setSelfDrive()

            HW.addCar(tempCar)
            HW.upDateHW()
            HW.upDateHW()


#Create highway sections of DECR flow
def CreateHwSoFlSect(IntGLst):
    I5Sec = []
    S520Sec = []
    I405Sec = []
    I90Sec = []

    for HW, sections in IntGLst.items():
        for count, section in enumerate(sections):
            tempID = str(HW) + '_' + str(section.NodeA.MileMark)
            TempHW = CarHW3.HighWay(tempID, (section.AvgT/2))
            TempHW.setLanes(section.FlwS)
            TempHW.setCol(abs(section.NodeB.MileMark - section.NodeA.MileMark))
            TempHW.makeHW()
            if count == 0:
                TempHW.setBegin()
            #if last highway segment, no more adj. nodes
            if count < len(sections)-1:
                adjN = str(HW) + '_' + str(section.NodeB.MileMark)
                TempHW.addAdj(adjN)
            else:
                TempHW.setEnd()

            if HW == 5 and section.NodeA.MileMark == 152.72:
                TempHW.addAdj('405_0.0')
            elif HW == 5 and section.NodeA.MileMark == 181.31:
                TempHW.addAdj('405_30.21')
            elif HW == 5 and section.NodeA.MileMark == 167.8:
                TempHW.addAdj('520_0.0')
            elif HW == 5 and section.NodeA.MileMark == 164.22:
                TempHW.addAdj('90_2.79')
            elif HW == 90 and section.NodeA.MileMark == 2.79:
                TempHW.addAdj('5_164.22')
            elif HW == 90 and section.NodeA.MileMark == 11.64:
                TempHW.addAdj('405_10.93')
            elif HW == 405 and section.NodeA.MileMark == 0:
                TempHW.addAdj('5_152.72')
            elif HW == 405 and section.NodeA.MileMark == 30.21:
                TempHW.addAdj('5_181.31')
            elif HW == 405 and section.NodeA.MileMark == 10.93:
                TempHW.addAdj('90_11.64')
            elif HW == 405 and section.NodeA.MileMark == 14.83:
                TempHW.addAdj('520_6.93')
            elif HW == 520 and section.NodeA.MileMark == 0:
                TempHW.addAdj('5_167.8')
            elif HW == 520 and section.NodeA.MileMark == 6.93:
                TempHW.addAdj('405_14.83')

            if HW == 5:
                I5Sec.append(TempHW)
            elif HW == 520:
                S520Sec.append(TempHW)
            elif HW == 405:
                I405Sec.append(TempHW)
            else:
                I90Sec.append(TempHW)

    HWList = [I5Sec, S520Sec, I405Sec, I90Sec]

    return HWList


#Initial random car seeder
#Logic for handling reserved lanes
def RandResCarSeeder(HWList, frac):
    for HW in HWList:
        for x in range(random.randint(1,2)):
            tempCar = CarHW3.Car(4,random.randint(1,HW.Lane-1))
            if random.uniform(0,1) < frac:

                tempCar.setSelfDrive()
                tempCar.chngLn(0)

            HW.addCar(tempCar)
            HW.upDateHW()
            HW.upDateHW()

#Part one of program, parse excel file store as State Highway Graph Obj
#Returns list of lists of objects ordered by highway
def Phase1():
    I5Lst = []
    SR520Lst = []
    I405Lst = []
    I90Lst = []
    IntGrphList = {5:I5Lst, 520:SR520Lst, 405:I405Lst, 90:I90Lst}

    FilNam = Phas2.getDTfrFile()
    ParsedData = Phas2.parseSht(FilNam)
    ParseAndStore(ParsedData, IntGrphList)

    return IntGrphList


#Random car seeder while simulation is running
#Logic for handling reserved lanes
def RandResCarRunningSeeder(HWList, frac):
    for HW in HWList:
        tempCar = CarHW3.Car(4,random.randint(1,HW.Lane-1))
        if random.uniform(0,1) < frac:
            tempCar.setSelfDrive()
            tempCar.chngLn(0)
        HW.addCar(tempCar)


#Random car seeder while simulation is running
def RandCarRunningSeeder(HWList, frac):
    for HW in HWList:
        tempCar = CarHW3.Car(4,random.randint(0,HW.Lane-1))
        if random.uniform(0,1) < frac:
            tempCar.setSelfDrive()
        HW.addCar(tempCar)


#Tests for running simulation on full highway system
#Takes arguments of a lists of highways with lists of sections
#Second argument is a shared dictionary object for passing
# vehicles from one section to the next
def TestPhase1(HWList, ShareDict):
    #Seed highways
    print('Populating Highways')
    selffrac = 0.9
    for i in tqdm.tqdm(range(17)):                      #Range determines
        for HW in HWList:                               # how many vehicles to
            RandResCarSeeder(HW, selffrac)              # populate

    #Run simulation
    print('Running Simulation')
    for x in tqdm.tqdm(range(600)):
        for HW in HWList:
            if x%60 == 0:                               #Every 60 Iterations
                RandResCarRunningSeeder(HW, selffrac)   #Add new car to system
                                                        #To sim. new cars
            for highW in HW:                            #Iter every section of HW
                highW.AccCounter()
                entryQ, vol = ShareDict[highW.ID]
                highW.addFromEntryQ(entryQ)

                if highW.getTotalCars() > 0:
                    highW.upDateHW()
                highW.passHW(ShareDict)

            for highW in HW:                        #Store each timestep data
                ch = str(highW.ID)
                if '405' in ch:
                    fName = 'Test1_405temp.txt'
                elif '90' in ch:
                    fName = 'Test1_90temp.txt'
                elif '520' in ch:
                    fName = 'Test1_520temp.txt'
                else:
                    fName = 'Test1_I5temp.txt'

                f = open(fName, 'a')

                miles = ((highW.Dis)/5280)*20
                ro = highW.getTotalCars()/(miles+highW.Lane)

                txt = str(x)+',N,'+str(highW.ID)+','+str(highW.getTotalCars())
                txt += ','+str(highW.getAvgVel())
                txt += ','+str(highW.getNewAcc())
                txt += ','+str(highW.Lane)
                txt += ','+str(miles)
                txt += ','+str(ro)

                f.write(txt+'\n')
                f.close()
                highW.reNewAcc()            #Reset New Accident Counter


def main():

    mainSt = time.time()
    #Return a Dictionary of lists of StrGrph() class objects of parsed data
    #This dictionary object is then used to create HWList of INCR and DECR HWs
    TestInter = Phase1()

    #Creates list of highways of lists of highway sections
    HWList = CreateHwNoFlSect(TestInter)

    #Create shared dictionary for passing objects between sections
    ShrDict = {}
    for HW in HWList:
        CarHW3.createDict(ShrDict, HW)
    print('Shared Dict Created')

    TestPhase1(HWList, ShrDict)         #Run simulation

    endM = time.time()                  #Measure time
    print('done')
    print(endM - mainSt)

if __name__ == '__main__':main()
