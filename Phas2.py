#Created by UC Denver 2017 ACM team

import pandas as pd
import math
import random
import networkx as nx
import matplotlib.pyplot as plt

#Provided Excel Column Names
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


Rt5 = []
Rt90 = []
Rt405 = []
Rt520 = []

#Node class object
class Node():
    def __init__(self):
        self.MileMark = None

    def setMM(self, A):
        self.MileMark = A

#State Highway Graph object hold data from excel file
class StrGrph():
    def __init__(self):
        self.NodeA = Node()
        self.NodeB = Node()
        self.AvgT = 0
        self.FlwN = 0
        self.FlwS = 0
        self.RT = None

    def setAdjN(self, NodA, NodB, W, N, S, HW):
        self.NodeA.setMM(NodA)          #Start MileM
        self.NodeB.setMM(NodB)          #End MileM
        self.AvgT = W                   #Average Daily Flow
        self.FlwN = N                   #Number of lanes INCR
        self.FlwS = S                   #Number of lanes DECR
        self.RT = HW                    #Highway descriptor

#Return data file
def getDTfrFile():
    File = pd.ExcelFile("2017_MCM_Problem_C_Data.xlsx")
    return File

#Parse data sheet into pandas data frame
def parseSht(File):
    DTS = File.parse("parsed mile posts")
    return DTS

#Creates a Node Edge graph of all mile markers
#Milemarkers are nodes, edge are highway segments
def crtGrph(Graph, Routes):
    for rt in Routes:
        for x in rt:
            Graph.add_edge(x.NodeA.MileMark, x.NodeB.MileMark, weight = x.AvgT)
            Graph.add_edge(x.NodeB.MileMark, x.NodeB.MileMark, weight = x.AvgT/2)
    return Graph

def getData(DT, Grph):
    global Rt5
    global Rt90
    global Rt405
    global Rt520

    Grph.setAdjN(row[ClmHdr['sMile']], row[ClmHdr['eMile']], row[ClmHdr['avgD']],
                    row[ClmHdr['nLan']], row[ClmHdr['sLan']], row[ClmHdr['rTyp']])

    if row[ClmHdr['rId']] == 5:
        Rt5.append(TempNd)
    elif row[ClmHdr['rId']] == 90:
        Rt90.append(TempNd)
    elif row[ClmHdr['rId']] == 405:
        Rt405.append(TempNd)
    else:
        Rt520.append(TempNd)

    return Grph


#Main function for testing file
def main():
    FL = getDTfrFile()
    DT = parseSht(FL)

    NdGrph = nx.MultiDiGraph()

    for index, row in DT.iterrows():
        TempNd = StrGrph()
        TempNd.setAdjN(row[ClmHdr['sMile']], row[ClmHdr['eMile']], row[ClmHdr['avgD']],
                       row[ClmHdr['nLan']], row[ClmHdr['sLan']], row[ClmHdr['rTyp']])

        if row[ClmHdr['rId']] == 5:
            Rt5.append(TempNd)
        elif row[ClmHdr['rId']] == 90:
            Rt90.append(TempNd)
        elif row[ClmHdr['rId']] == 405:
            Rt405.append(TempNd)
        else:
            Rt520.append(TempNd)

    Routes = [Rt5, Rt90, Rt405, Rt520]

    NdGrph = crtGrph(NdGrph, Routes)

    nx.draw_networkx(NdGrph, pos=nx.nx_pydot.graphviz_layout(NdGrph), arrows=True, with_labels=True)

    print("Rt 5 = {} \t Rt90 = {} \t Rt405 = {} \t Rt520 = {}".format(len(Rt5), len(Rt90), len(Rt405), len(Rt520)))

    plt.show()

if __name__ == '__main__':main()
