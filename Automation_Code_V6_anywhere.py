import pandas as  pd
import math as Math
import csv,os
from xlsxwriter.workbook import Workbook
import time
from subprocess import call
from collections import deque
from xml.dom.minidom import parse
from shutil import rmtree, copy  # just to clear things 		<Value name="policy">../input/policy/carbon_tax_0.xml</Value>

from numpy import log, exp


# THanks
def formulacalc(sample_value, currentYear, Gcam_StartValue, costFloor, min,
                max_value):  # THis caclulatees the elicitation units.
    # offset is the year that you start at 0 is 2015
    Max_Value = max(sample_value * (costFloor / 100),
                    Gcam_StartValue + ((sample_value - Gcam_StartValue) / (1 - beta)) * (
                            1 - Math.pow(beta, (currentYear - startYear) / (baseYear - startYear))))
    if (currentYear == startYear):  # if D18=start Year
        return Gcam_StartValue  # Return B10
    elif (currentYear == baseYear):  # D$18=Base_Year
        return sample_value  # ,$B$9

    elif (currentYear < baseYear):  # D$18<Base_Year
        return Gcam_StartValue + ((sample_value - Gcam_StartValue) / (1 - beta)) * (
                1 - Math.pow(beta, (currentYear - startYear) / (baseYear - startYear)))
    elif (Max_Value > max_value):
        return max_value
    elif (Max_Value < min):
        return min
    else:
        return Max_Value
def createVals(samplenum):
    #For a given sample , this will generate a Dictinoary of values for the technologies choosen
    #As well as the storage costs
    newdict= dict() # Dictionary to hold all of the values
    for Tech in techList: # THis gets all technologies in the intermediate feild
        if Tech=="rooftop_pv":
            continue
        # Temporary arrays to hold values
        temparry = list()
        temparry2=list()
        # Prices_2030.loc[["Max"]]["wind"][0] this will select the max value in the wind colum
        # Prices_2030.loc[1]["solar"] This will look at sample 1 in the solar collum
        sampleVal = Prices_2030.loc[samplenum][Tech]
        maxval = Prices_2030.loc[["Max"]][Tech][0]
        minVal = Prices_2030.loc[["Min"]][Tech][0]
        # val_2015 = Prices_2030.loc[["val 2015"]][Tech][0] # was used for the old equation
        Gcam_StartValue = Prices_2030.loc[["Gcam_StartValue"]][Tech][0]
        costfloor = 8  # This is going to be some set constant
        for t in range(2010,2105,5): ## calulate the values for each technology
            # print(str(sample_Num)+"here are the vals") debug statement
            # def formulacalc(sample_value, currentYear, Gcam_StartValue, costFloor, min, max_value):  # THis caclulatees the elicitation units.
            temparry.append(
                formulacalc(sampleVal,  # Expert elicitation for a specific technolgy and year
                            t,  # time 2015,2020 etc
                            Gcam_StartValue,
                            costfloor,
                            minVal,  # minimum value for the technology
                            maxval) / Elicitation_to_GCAM_Conversion_Factors)
            # Debug statements
            # print(Tech+ "Sample "+str(sample_Num))
            # print("val2030 : "+str(sampleVal))
            # print("val_2015: "+str(val_2015))
            # print("minVal: " + str(minVal))
            # print("maxVal: " + str(maxval))
            # print("val_2015 - minVal: "+ str(val_2015 - minVal))
        # The subtechnolgy/ intermediate technology name for the specified technology
        intermediateTech= Prices_2030.loc[["intermediate Tech"]][Tech][0]

        newdict[intermediateTech]=deque(temparry)
        if(len(StorageCosts.loc[StorageCosts["Technology"]==intermediateTech].index.values)==0): # this checks if the choosen technology has a storage cost
            continue
        storageName=StorageCosts.loc[StorageCosts["Technology"]==intermediateTech].index.values[0]
        temparry3 = list()
        for pos in range(0,temparry.__len__()):
            temparry2.append(StorageCosts.loc[storageName][pos+2]+temparry[pos]) # the plus to is to offset for the two extra collums
        newdict[storageName]=deque(temparry2)
        if(Tech=="solar"): # This is doing the rooftop PV if SOlar was choosen
            temparry2 = list() #empty the list
            for pos in range(0, temparry.__len__()):  # adding rooftop PV to the list of technologies
                temparry2.append(temparry[pos]/StorageCosts.loc["rooftop_pv"][pos + 2])  # the plus to is to offset for the two extra collums
            newdict["rooftop_pv"] = deque(temparry2)
            # thsi is where I would also add CSP

            temparry3 = list()  # A temp array to hold teh vales of csp
            temparry4 = list()  # temp aray to hold the values of cspstorage

            for pos in range(0, temparry.__len__()):  # Adding Csp cost to the list of prices
                temparry3.append(temparry[pos] + StorageCosts.loc["CSP"][
                    pos + 2])  # the plus to is to offset for the two extra collums
            newdict["CSP"] = deque(temparry3)

            for pos in range(0, temparry.__len__()):  # Adding Csp cost to the list of prices
                temparry4.append(temparry3[pos] + StorageCosts.loc["CSP_storage"][
                    pos + 2])  # the plus to is to offset for the two extra collums
            newdict["CSP_storage"] = deque(temparry4)
    #
    return newdict

def toXLXS(fileName):  # This converts a CSV to Ecell.
    """ Converts CSV to excell. Takes in a parameter of the filepath for a csv
           """
    # Pandas was not used because it does some strange formatting
    # most of these files that are created as XLSX are just to extract the dataframe and nothing else,
    # hence this is why a junk filepath was used
    name = os.path.basename(fileName).split(
        '\\')[-1].split('.csv')
    workbook = Workbook(os.path.join(junkPath,str(name[0])+ '.xlsx'), {'strings_to_numbers': True, 'constant_memory': True})
    worksheet = workbook.add_worksheet()
    #with open(os.path.join(savepath,fileName),'r') as f:
    with open(fileName,'r') as f:
        r = csv.reader(f)
        for row_index, row in enumerate(r):
            for col_index, data in enumerate(row):
                worksheet.write(row_index, col_index, data)
    workbook.close()
    return (str(name[0]))
def findStartingRow(df):
    """This finds the index of the first 2015 row in the dataframe
        since all of our datat starts in 2015
"""
    ###################################
    #hERE i AM MAKING THE ASSUMPTIONS THAT FOR MOST FILES THE STARTING 2015 WILL NOT BE THE SAME
    ###########################
    for i in range(0,(df.shape)[0]):
        row=df.iloc[i].tolist()# This is the entire row. I'll keep this for now for debugging purposes
        if 2010 in row: #if 2010 is in that row, Return the row number
            return i
def claerAllsamples():
    """This clears the AllSamples, and junk directories"""
    dirList = list()
    [dirList.append(x[0]) for x in os.walk("Scatchspace_bigsimulation")]
    print("Deleting directories")
    if (os.path.isdir(allSamplesDir)):
        print("deleting all samples")
        rmtree(allSamplesDir)  # clear the directory

    if (os.path.isdir("Junk")):
        print("Clearing junk files")
        rmtree("Junk")  # clear the junk directory,

    print("Deleting directories in original copy")
    if dirList.__len__() >= 1:  # if a directory exist
        [rmtree(directory) for directory in dirList if (
                    directory != "Scatchspace_bigsimulation" and directory != "Scatchspace_bigsimulation\\Resource_fixed_and_floating_added" and directory != "Scatchspace_bigsimulation\\En_Tranformation")]  # delete direcotries except specific ones
    print("\nRestoring files...")
    copy((os.path.join(Original_copyDir,"Multi_scenario batch file.xml")),os.getcwd()) # reserach lab will be home dit that I wil eventusll make
    copy(os.path.join(Original_copyDir,"BatchCSV_elec.xml"), os.getcwd())  # restore the the other file
    copy(os.path.join(Original_copyDir,"configuration _ref.xml"), os.getcwd())
    copy(os.path.join(Original_copyDir, "Resource_fixed_and_floating_added", "batch_resource_fixed_floating.xml"),
         os.getcwd())  # restore the the other file
    copy("Scatchspace_bigsimulation/En_Tranformation/batch_en_transformation.xml",
         os.getcwd())  # restore the the other file

    # Scatchspace/Resource_fixed_and_floating_added/batch_resource_fixed_floating.xml
    os.mkdir(junkPath)  # creates a junk directory in working directory
    os.mkdir(allSamplesDir)  # creates a junk directory in working directory chagning directoryies


def updateConfig(cconfigPath, samplenum, elecfileLInk, rsrcfileLInk, entransform_outfilepath):  # path to CSV really....
    """This creates a config file for each sample and points the config to a corresponding Electricity file
               """
    # change the path of the elctricity file and the resource file
    #    ConfigFile.getElementsByTagName("ScenarioComponents")[0].getElementsByTagName("Value")[44].firstChild.data="../input/All-Samples/Sample-"+samplenum+"/carbon_tax-"+samplenum+".xml" # Changing tname for electricity file
    ConfigFile.getElementsByTagName("ScenarioComponents")[0].getElementsByTagName("Value")[
        43].firstChild.data = elecfileLInk  # Changing tname for electricity file
    ConfigFile.getElementsByTagName("ScenarioComponents")[0].getElementsByTagName("Value")[
        42].firstChild.data = rsrcfileLInk  # Changing the path for the resource file
    ConfigFile.getElementsByTagName("ScenarioComponents")[0].getElementsByTagName("Value")[
        44].firstChild.data = entransform_outfilepath  # Changing tname for electricity file

    if (techList.__len__() >= 1):
        ConfigFile.getElementsByTagName("Strings")[0].getElementsByTagName("Value")[
            0].firstChild.data = "Ctax" + "All-Tech" + "-" + samplenum  # This is teh scenartio name
        # tech_specDir.split("\\")[6]
    else:
        ConfigFile.getElementsByTagName("Strings")[0].getElementsByTagName("Value")[0].firstChild.data = tech_specDir.split("\\")[6] + "-"+samplenum
    #ConfigFile.getElementsByTagName("Strings")[0].getElementsByTagName("Value")[0].firstChild.data=ConfigFile.getElementsByTagName("Strings")[0].getElementsByTagName("Value")[0].firstChild.data+str(sample_Num)

    newXMLFile = open(os.path.join(cconfigPath, "configuration.xml"), "w")  # save the final xml file

    ConfigFile.writexml(newXMLFile, indent="\n", addindent="", newl="")  # save changes to in the custom inputs.
def toXMLpath (fullpath,type): # Convert from Normal path to xml path
    """ Convert a normal filePath on windwos to a XML filepath for GCAM
    ex: on windows we have
    C:\Users\owner\Documents
    for GCAM xpath is used so in Xpath it is
    C:/Users/owner/Documents
    """
    splitted = (fullpath.split('\\'))  # splits the file path by \
    newPath=""
    if "file" ==type:
        if "" in splitted:
            splitted.remove("")  # removes spaces
        for part in range(0,splitted.__len__()-1):
            newPath=newPath+splitted[part]+"/"
        newPath=newPath+"/"+splitted[splitted.__len__()-1]
    else: # This means file type is path
        if "" in splitted:
            splitted.remove("")
        for part in range(0,splitted.__len__()):
            newPath=newPath+splitted[part]+"/"
    return newPath
def toNormalFilePath (xmlPath):
    """ converts XML to Normal file path"""
    xmlPath = (xmlPath.split('/'))
    drive = xmlPath[0]
    xmlPath.remove(drive)
    if "" in xmlPath:
        xmlPath.remove("")
    correctPath = os.path.join(drive+"\\", *xmlPath)  # this has the csv

    return correctPath


def createCCSvals(samplenum, samplestore):
    ' This function will replace the CCS files in the GlobalTechCapital_elec or GlobalIntTechCapital_elec files this '
    """samplestore: This is basically a dictonary that comes out of create vals
        samplenum: The current sample that youare on
    """


    # This is a dictionary that will hold the base cost of technologies for which we want to add our own
    CCSvals = dict()  # THis si the dictionary that will be returned to replace the value
    CCSbasecost = {  # These are base costs that will never change . They are constant
        "coal (conv pul)": [850, 898, 887, 877, 867, 858, 849, 840, 832, 824, 817, 810, 803, 797, 791, 785, 780, 774,
                            769],
        "gas (CC)": [320, 325, 321, 318, 314, 311, 307, 304, 301, 298, 296, 293, 291, 288, 286, 284, 282, 280, 279],
        "refined liquids (CC)": [325, 325, 321, 318, 314, 311, 307, 304, 301, 298, 296, 293, 291, 288, 286, 284, 282,
                                 280, 279],
        "coal (IGCC)": [1239, 1239, 1187, 1142, 1103, 1070, 1041, 1017, 996, 977, 962, 949, 937, 927, 919, 912, 905,
                        900, 895]
    }
    # l= list(samplestore["biomass (conv)"].copy())[0]
    if "biomass (conv)" in samplestore:  # I haveto manually add biomass here since it is changing with each smaple
        CCSbasecost["biomass (conv)"] = list(samplestore["biomass (conv)"].copy())
        CCSbasecost["biomass (IGCC)"] = list(samplestore["biomass (IGCC)"].copy())

    # This dictionary is the name of the technologies that we are going to replace inte excell with our ccs costs
    CCSadded = {
        "coal (conv pul)": "coal (conv pul CCS)",
        "gas (CC)": "gas (CC CCS)",
        "refined liquids (CC)": "refined liquids (CC CCS)",
        "coal (IGCC)": "coal (IGCC CCS)",
        "biomass (conv)": "biomass (conv CCS)",
        "biomass (IGCC)": "biomass (IGCC CCS)"
    }
    # samplestore=dict()
    costfloor = 50
    sampleVal = CCS_costs.loc[samplenum][0]
    maxval = CCS_costs.loc["Max"][0]
    manval = CCS_costs.loc["Min"][0]
    Gcam_StartValue = CCS_costs.loc["Val2010"][0]
    CalculatedCCS = list()  # these will hold the calculated CCS cvalues
    Ccsval = list()
    for currentYear in range(2010, 2105, 5):  # This is where I put hte CCS costs through the equation for each year
        CalculatedCCS.append(formulacalc(sampleVal, currentYear, Gcam_StartValue, costfloor, manval,
                                         maxval) / Elicitation_to_GCAM_Conversion_Factors)

    for key, val in CCSbasecost.items():  # This is where I add the CCS cost to each base cost
        Ccsval = [x + y for x, y in zip(CalculatedCCS, val)]
        ccsname = CCSadded[key]
        samplestore[ccsname] = deque(Ccsval)

    # No need to return anything because we are changing the dictionary


def createEffvals(sample):
    results = dict()
    ' This function creates the values used to replace the ones in GlobalTechEff_elec.csv'
    'again, the parameter sample is the current sample number'

    Effbasevals = {  # These are the base cost of the efficeiencies
        "coal (IGCC)": [0.407, 0.407, 0.426, 0.442, 0.458, 0.471, 0.484, 0.495, 0.505, 0.514, 0.522, 0.530, 0.536,
                        0.543, 0.548, 0.553, 0.558, 0.562, 0.565],
        "gas (CC)": [0.576, 0.565, 0.577, 0.588, 0.598, 0.608, 0.617, 0.625, 0.633, 0.640, 0.646, 0.653, 0.658, 0.663,
                     0.668, 0.673, 0.677, 0.681, 0.684],
        "refined liquids (CC)": [0.555, 0.555, 0.568, 0.579, 0.590, 0.601, 0.610, 0.619, 0.627, 0.634, 0.641, 0.648,
                                 0.654, 0.659, 0.664, 0.669, 0.674, 0.678, 0.682],
        "coal (conv pul)": [0.397, 0.397, 0.41, 0.422, 0.434, 0.444, 0.454, 0.463, 0.472, 0.48, 0.487, 0.494, 0.5,
                            0.506, 0.511, 0.516, 0.521, 0.525, 0.529]

    }

    IGCC_addon = [0.054, 0.054, 0.059, 0.064, 0.069, 0.071, 0.075, 0.078, 0.08, 0.082, 0.082, 0.084, 0.085, 0.085,
                  0.085, 0.086, 0.086, 0.086, 0.087]  # IGCC values to add to base cost

    # Playing around with how I'd actually do this
    # CCS_EnPen_val=Effsamplevals.loc[1][' CCS energy penalty']

    # if "biomass (conv)" in samplestore:  # I haveto manually add biomass here since it is changing
    #   Effbasevals["biomass (conv)"] = list(samplestore["biomass (conv)"].copy())
    #  Effbasevals["biomass (IGCC)"] = list(samplestore["biomass (IGCC)"].copy())

    # This dictionary is the name of the technologies that we are going to replace in the excell with our ccs costs
    Effnames = {
        "coal (IGCC)": "coal (IGCC CCS)",
        "gas (CC)": "gas (CC CCS)",
        "refined liquids (CC)": "refined liquids (CC CCS)",
        "coal (conv pul)": "coal (conv pul CCS)",
        "biomass (conv)": "biomass (conv CCS)",
        "biomass (IGCC)": "biomass (IGCC CCS)"
    }
    costfloor = 50
    maxval = Effsamplevals.loc['Max'][0]  # The max value of the Eff costs
    minval = Effsamplevals.loc['Min'][0]  # The min value of the Eff costs
    Gcam_StartValue = Effsamplevals.loc['Val 2010'][0]
    samplevalue = Effsamplevals.loc[sample][0]
    calcualtedvals = list()
    biomass_eff_val = Effsamplevals.loc[sample][' Electricity from biomass efficiency']
    maxval_bioeff = Effsamplevals.loc[['Max']][' Electricity from biomass efficiency'][0]  # max value for bioeff
    minval_bioeff = Effsamplevals.loc[['Min']][' Electricity from biomass efficiency'][0]  # min value for bioeff
    startVal_Bioeff = Effsamplevals.loc[['Val 2010']][' Electricity from biomass efficiency'][0]
    HHVLHV_Conv = .921
    biomass_conv_calc = list()
    IGCC_pos = 0

    for year in range(2010, 2105, 5):
        calcualtedvals.append(formulacalc(samplevalue, year, Gcam_StartValue, costfloor, minval, maxval))
        biomass_conv_value = (formulacalc(biomass_eff_val, year, startVal_Bioeff, costfloor, minval_bioeff,
                                          maxval_bioeff) / 100) / HHVLHV_Conv
        biomass_conv_calc.append(min(1, biomass_conv_value))
        IGCC_pos += 1
    biomass_IGCC_calc = [x + y for x, y in zip(biomass_conv_calc, IGCC_addon)]
    # CCSbasecost["biomass (conv)"] = list(samplestore["biomass (conv)"].copy())
    # CCSbasecost["biomass (IGCC)"]
    Effbasevals["biomass (conv)"] = biomass_conv_calc
    Effbasevals["biomass (IGCC)"] = biomass_IGCC_calc
    results["biomass (conv)"] = deque(biomass_conv_calc)
    results["biomass (IGCC)"] = deque(biomass_IGCC_calc)

    for key, val in Effbasevals.items():
        CCSpenaltyval = [conveff - conveff * (eleci_units / 100) for eleci_units, conveff in
                         zip(calcualtedvals, val)]  # this will calculate the effeciency vals
        Effname = Effnames[key]
        results[Effname] = deque(CCSpenaltyval)
    return results


def createBioliquidcosts(sample):
    # bioliquid_costs
    ' This function is used to generate the values to replace the ones in the L222.GlobalTechCost_en.csv file '
    'Parameters: '
    'Sample: The current sampple number'
    conversionA = 0.000000001
    conversionB = 116100000
    newvals = dict()
    cellulosic_ethanolCostCCS = {
        "cellulosic ethanol CCS level 1": [0.2518, 0.2291, 0.2114, 0.1977, 0.1872, 0.1791, 0.1727, 0.1678, 0.164,
                                           0.1611, 0.1588, 0.1571, 0.1557, 0.1546, 0.1539, 0.1532, 0.1528,
                                           0.1524, 0.1521],
        "cellulosic ethanol CCS level 2": [2.1106, 1.9196, 1.7718, 1.6574, 1.569, 1.5006, 1.4476, 1.4065, 1.3748,
                                           1.3503, 1.3313, 1.3166, 1.3052, 1.2964, 1.2896, 1.2844, 1.2803,
                                           1.2771, 1.2747],
    }
    biofuels_CCScosts = {
        "FT biofuels CCS level 1": [0.7146, 0.65, 0.5999, 0.5612, 0.5312, 0.508, 0.4902, 0.4762, 0.4655, 0.4572, 0.4508,
                                    0.4458, 0.442, 0.439, 0.4366, 0.4348, 0.4335, 0.4324, 0.4315],
        "FT biofuels CCS level 2": [1.173, 1.0669, 0.9847, 0.9211, 0.8719, 0.8339, 0.8045, 0.7817, 0.7641, 0.7504,
                                    0.7399, 0.7317, 0.7254, 0.7205, 0.7167, 0.7138, 0.7115, 0.7098, 0.7084],
    }

    costfloor = 50
    maxval = bioliquid_costs.loc["Max"][0]  # The max value of the Eff costs
    minval = bioliquid_costs.loc['Min'][0]  # The min value of the Eff costs
    Gcam_StartValue = bioliquid_costs.loc['Val 2010'][0]
    samplevalue = bioliquid_costs.loc[sample][0]
    cellulosic_ethanol = list()
    FTbiofuels_BASE = [3.0623, 2.9325, 2.8211, 2.7254, 2.6432, 2.5727, 2.512, 2.46, 2.4153, 2.3769, 2.3439, 2.3156,
                       2.2913, 2.2704, 2.2526, 2.2372, 2.224, 2.2126, 2.2029]

    for year in range(2010, 2105, 5):
        cellulosic_ethanol.append(formulacalc(samplevalue, year, Gcam_StartValue, costfloor, minval, maxval) / (
                    Elicitation_to_GCAM_Conversion_Factors * conversionA * conversionB))

    for key, val in cellulosic_ethanolCostCCS.items():  # This will calculate the values for Cellulosic ethanol
        temparr = [basecosts + ethanolcost for basecosts, ethanolcost in
                   zip(val, cellulosic_ethanol)]  # this will calculate the effeciency vals
        newvals[key] = deque(temparr)

    FTbiofuels_CCS = [ftbase + cellulosic_ethanol for ftbase, cellulosic_ethanol in
                      zip(FTbiofuels_BASE, cellulosic_ethanol)]  # this will create the new FT biofuels costs
    # cellulosic_ethanol_ccsL1= [ cellulosic_ethanolCCS1 + cellulosic_ethanol for cellulosic_ethanolCCS1, cellulosic_ethanol in zip(FTbiofuels_BASE, cellulosic_ethanol)]  # this will create the new FT biofuels costs

    for key, val in biofuels_CCScosts.items():
        temparr2 = [basecosts + biofuelcost for basecosts, biofuelcost in
                    zip(val, FTbiofuels_CCS)]  # this will calculate the effeciency vals
        newvals[key] = deque(temparr2)

    newvals['cellulosic ethanol'] = deque(cellulosic_ethanol)
    newvals['FT biofuels'] = deque(FTbiofuels_CCS)

    return newvals  # # Th # This is


def createBioliquidcoeff(sample):
    # bioliquid non energy costs
    # Celluoistic l1
    # Celluastic L2
    # Create the values to replace in the energy transofmation files
    ' This function is used to generate the values to replace the ones in the L222.GlobalTechCoef_en.csv file '
    'Parameters: '
    'Sample: The current sampple number'
    constant = 0.921
    newvals = dict()
    cellulosic_ethanolCostCCS = {
        "cellulosic ethanol CCS level 1": [0.961664329, 0.961664329, 0.961664329, 0.961652961, 0.961641392, 0.961629616,
                                           0.961617629, 0.961605425, 0.961592997, 0.961580339, 0.961567445, 0.961554309,
                                           0.961540923, 0.96152728, 0.961513372, 0.961499193, 0.961484734, 0.961469986,
                                           0.96145494],
        "cellulosic ethanol CCS level 2": [0.908970393, 0.908970393, 0.908970393, 0.908979467, 0.908988701, 0.9089981,
                                           0.909007669, 0.909017411, 0.909027333, 0.909037438, 0.909047732, 0.909058221,
                                           0.909068909, 0.909079803, 0.909090909, 0.909102233, 0.909113781, 0.90912556,
                                           0.909137577],
    }
    ftbiofuels_basecosts = {
        "FT biofuels CCS level 2": [0.953639314, 0.953639314, 0.953639314, 0.952083577, 0.950505526, 0.948904677,
                                    0.947280534, 0.945632584, 0.9439603, 0.942263139, 0.940540541, 0.93879193,
                                    0.937016712, 0.935214277, 0.933383992, 0.931525207, 0.929637252, 0.927719435,
                                    0.92577104],
        "FT biofuels CCS level 1": [1.008827857, 1.008827857, 1.008827857, 1.00716182, 1.005471956, 1.00375775,
                                    1.002018673, 1.000254178, 0.998463705, 0.996646676, 0.994802495, 0.992930549,
                                    0.991030207, 0.989100817, 0.987141709, 0.98515219, 0.983131547, 0.981079043,
                                    0.978993919],
    }

    costfloor = 50
    maxval = bleff_costs.loc["Max"][0]  # The max value of the Eff costs
    minval = bleff_costs.loc['Min'][0]  # The min value of the Eff costs
    Gcam_StartValue = bleff_costs.loc['Val2010'][0]
    samplevalue = bleff_costs.loc[sample][0]
    cellulosic_ethanol = list()
    FTbiofuels_BASE = [1.048954615, 1.048954615, 1.048954615, 1.047249149, 1.045519203, 1.043764246, 1.041983731,
                       1.040177096, 1.038343762, 1.036483133, 1.034594595, 1.032677514, 1.030731239, 1.028755098,
                       1.026748398, 1.024710425, 1.022640441, 1.020537688, 1.01840138]

    for year in range(2010, 2105, 5):
        calculatedVal = formulacalc(samplevalue / 100, year, Gcam_StartValue, costfloor, minval / 100, maxval / 100)
        cellulosic_ethanol.append(max(1, 1 / samplevalue, 1 / (calculatedVal / constant)))

    for key, val in cellulosic_ethanolCostCCS.items():  # This will calculate the values for Cellulosic ethanol
        temparr = [ethanolcost / basecosts for basecosts, ethanolcost in
                   zip(val, cellulosic_ethanol)]  # this will calculate the effeciency vals
        newvals[key] = deque(temparr)

    FTbiofuels_CCS = [max(1, cellulosic_ethanol / ftbase) for ftbase, cellulosic_ethanol in
                      zip(FTbiofuels_BASE, cellulosic_ethanol)]  # this will create the new FT biofuels costs

    for key, val in ftbiofuels_basecosts.items():
        temparr2 = [cellulosic_ethanol / basecosts for basecosts, cellulosic_ethanol in
                    zip(val, cellulosic_ethanol)]  # this will calculate the effeciency vals
        newvals[key] = deque(temparr2)
    newvals['cellulosic ethanol'] = deque(cellulosic_ethanol)
    newvals['FT biofuels'] = deque(FTbiofuels_CCS)

    return newvals


baseYear = 2030  # Constant
startYear = 2010  # Constant
beta = .2  #Constant
allSamplesDir = os.path.join(os.getcwd(), "All-Samples")# The generated samples will be in the all samples folder
junkPath = os.path.join(os.getcwd(), "Junk")  # randomly generated files are stored heere. Don;t worry about this
Original_copyDir = os.path.join(os.getcwd(),
                                "Scatchspace_bigsimulation")  # The directory where the "orginal copy" folder will reside
offshoreFixedDIR = os.path.join(Original_copyDir, "Resource_fixed_and_floating_added")
claerAllsamples()  # This empties the All-Samples directories
#Offshore_batch=parse("batch_resource_fixed_floating.xml") # batch file for offshore wind
ConfigFile = parse("configuration _ref.xml") # this open the configuration file
# valon_2015=2007 ### Value in 2015 for onshore wind, Change this to whatever that constant is
# valoff_2015=5000 ### Value in 2015 for fixed and floating offshore wind, Change this to whatever that constant is
Elicitation_to_GCAM_Conversion_Factors = 3.236752164

raw_Data_file = pd.ExcelFile(os.path.join(Original_copyDir, "newEL_All_updated.xlsx"))  # Load the entire Excell sheet
Prices_2030 = raw_Data_file.parse('2030Values', skiprows=0) # Open the sheet of 2030 values
StorageCosts=raw_Data_file.parse('StorageCosts', skiprows=0) # opens the sheet of storage cost and the PC ratios
BatchCSVXML = parse("BatchCSV_elec.xml") # The batch CSV to Excell file.
Batch_en_transformation = parse("batch_en_transformation.xml")  # The batch file for EnergyTrans

Offshore_batch = parse("batch_resource_fixed_floating.xml")  # batch file for offshore wind
Raw_resultsXL = pd.ExcelFile(os.path.join(Original_copyDir, "correctedResults_fixed.xlsx"))
Raw_resultsXL_float = pd.ExcelFile(os.path.join(Original_copyDir, "correctedResults_float.xlsx"))
CCS_costs = raw_Data_file.parse("CCS Costs")  # These are our ccs cost for each samples,  Efficiency vals
bioliquid_costs = raw_Data_file.parse("Bioliquids")  # These are our ccs cost for each samples,  Efficiency vals
bleff_costs = raw_Data_file.parse(
    "Liquid biofuels efficiency")  # These are our ccs cost for each samples,  Efficiency vals

Effsamplevals = raw_Data_file.parse('Efficiency vals')  # Open the sheet of 2030 values
nodeList=BatchCSVXML.getElementsByTagName("command")[0].childNodes # get the list of elemtns in the csv
outputXMLName= "Electricity" # output XML name for the samples
# Scatchspace_bigsimulation
toXLXS(
    "Scatchspace_bigsimulation/Resource_fixed_and_floating_added/L210.RenewRsrcCurves_offshore_all.csv")  # convert Csv to xlsx
RenewRsrcCurves_oweRAW = pd.ExcelFile("Junk/L210.RenewRsrcCurves_offshore_all.xlsx")  # load fixed offshore
RenewRsrcCurves_owe = RenewRsrcCurves_oweRAW.parse("Sheet1",skiprows=0)
positionOfchanged_file=list()# This is the postion of the changed file in the XML.
CsvFiles=list()# list of CSV files to change
dfToModify =list()# this will store the dataframwes that need to be changed
techList=list() # will hold the name of technologies that we selected
techDF=list()# will hold the dataframes of hte tecchs we want
subtechList=list()# Will hold all of hte sub techs
techdic = dict()  # empty dictionary to hold the subtech and their capital costs
origFilename=list() # A list to hold the original file names

x = createEffvals(1)

# GlobalTechCostVals = createBioliquidcosts(1)

#createEffvals(5)


#list(Prices_2030) returns all the collum names of the dataframe
for tech in range(0, list(
        Prices_2030).__len__()):  # THis loop prints out the technologues current availble for the simulation
    print(list(Prices_2030)[tech]+" is index "+str(tech))

user_input = input("\nPlease specify what technologies you want by index , in the order shown, separated by a single space only: ")

num_of_samples=int(input("\nHow many samples do you want: "))+1
print("\n")

[techList.append(list(Prices_2030)[int(i)]) for i in user_input.split(' ') if i.isdigit()] # create a list with the tech that the user wants
if"solar" in techList: # I had to add an exception ,since Rooftop PV is actually its own entry
    techList.append("rooftop_pv")

# this will create a folder path based on the technologies you choose
# folder path is located in the current working directory
tech_specDir=os.path.join(Original_copyDir,techList[0][:3])

if(techList.__len__()>=1):
    for x in range(1,techList.__len__()):
        tech_specDir=tech_specDir+"-"+techList[x][:3]
os.mkdir(tech_specDir)

newBatchFilePath=os.path.join(tech_specDir,"techSpecBatch.xml")# new file path for the modified batch file

# testing the code for some errors in values
# newvals = createVals(1)  # Create t
# "CSP_storage"
# print(newvals["CSP"])
# print(newvals["CSP_storage"])

# exit(1) # force stop the program

############# end of debug code

# This part will Filter out every other technology that is not needed.
#
# for node in range(5, nodeList.length-2):
#     if(nodeList[node].nodeType==1): # check if this is an element with a file path
#
#         unformat_Path = nodeList[node].firstChild.data  #get the unformatted file path from our BatchCSV file
#         correctPath=toNormalFilePath(unformat_Path)# converting the path to a proper one we can use
#         FileName = toXLXS(correctPath)  # convert the input file to xlsx so we can keep the technologies that we want
#         raw_file_as_XL = pd.ExcelFile(os.path.join(junkPath,FileName + '.xlsx'))  # Load the entire Excell sheet
#         new_input_file = raw_file_as_XL.parse("Sheet1", skiprows=0)  #Dataframe of input file
#         row_df =  new_input_file.iloc[3].tolist()  # This is the entire label row as a list
#         #subSec_collumn=list()# initializing an empty list to be referenced later on
#         rowstoDelete = list() # initialize an empty list to hold all the rows to be deleted
#
#         if "subsector.name" in row_df: # checking for subsector name in the files that are not consistant
#             subSec_collumn=row_df.index("subsector.name") # the collum that subsector is located
#         else:
#             if "subsector" in row_df:
#                 subSec_collumn = row_df.index("subsector")  # the collum that subsector is located
#             else:
#                 continue
#
#         for row in range(4, (new_input_file.shape)[0]):  # This is where we choose the row to start from in each excell file since it changes
#             if not set([new_input_file.iloc[row, subSec_collumn]]).issubset(techList):
#                 rowstoDelete.append(row)
#                 # This is supposed to be the filtering but there are much much better ways to do
#         # if (nodeList[node + 1].nodeType == 8): # anticipating wind and solar specifically because in some cases, we can selected those technolgoeis and have no rows to remove.
#         #     if (nodeList[node + 1].data == 'Wind Solar' and (set(['wind', "offshore",'solar', 'rooftop_pv']).issubset(techList) or "wind" in techList or "offshore" in techList)):
#         #         # CsvFiles.append(Onlytech) set(techList).issubset(set(['wind', "offshore",'solar', 'rooftop_pv']))
#         #         origFilename.append(FileName)  # this will write the file name to a blank spot
#         #         positionOfchanged_file.append(node)
#         #         dfToModify.append(new_input_file)
#         if rowstoDelete:
#             new_input_file.drop(rowstoDelete,inplace=True) # delete the rows
#             if (FileName == 'L223.GlobalTechCapital_elec' or FileName == 'L223.GlobalIntTechCapital_elec') and len(new_input_file) > 4:
#                 origFilename.append(FileName)  # add original filename to the list
#                 dfToModify.append(new_input_file)
#                 positionOfchanged_file.append(node)
#             Onlytech = os.path.join(tech_specDir, FileName + ".csv") # new file path in a differnt folder just for that tech
#             new_input_file.to_csv(Onlytech, encoding='utf-8', index=False)  # write the CSV to anew path for tech specific tech
#             # here we reformat the path so that it is in xml GCAM formatt
#             #splitted = (Onlytech.split('\\'))
#             xmlFormmated_path= toXMLpath(Onlytech,"file") # Convert the file path to an XML one.
#             # Now we join the list to make the xmlformatted path
#             BatchCSVXML.getElementsByTagName("command")[0].childNodes[node].firstChild.data=xmlFormmated_path # updates the file with only specific techs
#             # if (nodeList[node + 1].nodeType == 8 ):  # add the files that we need to change to thaat list
#             #     if(nodeList[node + 1].data== 'Change this'):
#             #         #CsvFiles.append(Onlytech)
#             #         origFilename.append(FileName) # this will write the file name to a blank spot
#             #         positionOfchanged_file.append(node)
#             #         dfToModify.append(new_input_file)
# This is a dictionary that will hold the base cost of technologies for which we want to add our own


# CCS vakues to

CCStoreplace =["coal (conv pul)",]
print("Done filtering tech")
newBatch = open(newBatchFilePath, "w") # save a new batch file with the changes that we made
BatchCSVXML.writexml(newBatch)  # save changes to file
newBatch.close()

BatchCSVXML = parse(newBatchFilePath) #Load the variable with the new batch file.

print("Done filtering uneeded technologies")

print("Start!")
################### right now


# C:\Users\owner\PycharmProjects\REU_ResearchLab\Scatchspace_bigsimulation\L223.GlobalIntTechCapital_elec.csv
#  I have to manually import both of these files since these are the only ones we will be changing
raw_Data_file1 = pd.ExcelFile('Saved files/L223.GlobalIntTechCapital_elec.xlsx')  # Load the entire Excell sheet
raw_Data_file2 = pd.ExcelFile('Saved files/L223.GlobalTechCapital_elec.xlsx')  # Load the entire Excell sheet
raw_Data_file3 = pd.ExcelFile('Saved files/L223.GlobalTechEff_elec.xlsx')  # Load the entire Excell sheet
raw_Data_file4 = pd.ExcelFile('Saved files/L222.GlobalTechCost_en.xlsx')  # Load the entire Excell sheet
raw_Data_file5 = pd.ExcelFile('Saved files/L222.GlobalTechCoef_en.xlsx')  # Load the entire Excell sheet

# Liquid biofuels efficiency

L223_GlobalIntTechCapital = raw_Data_file1.parse('Sheet1', skiprows=0)  # Open the sheet of 2030 values
L223_GlobalTechCapital = raw_Data_file2.parse('Sheet1', skiprows=0)  # Open the sheet of 2030 values
GlobalTechEff_elec = raw_Data_file3.parse('Sheet1', skiprows=0)  # open the sheet of Eff values
GlobalTechCost_en = raw_Data_file4.parse('L222.GlobalTechCost_en', skiprows=0)
GlobalTechCoef_en = raw_Data_file5.parse('L222.GlobalTechCoef_en', skiprows=0)
effstartingrow = 70  # This is the first row that has 2015 vlaues L222.GlobalTechCoef_en
GlobalTechCoef_enstart = findStartingRow(GlobalTechCoef_en)
GlobalTechCost_en_start = findStartingRow(GlobalTechCost_en)
dfToModify = [L223_GlobalTechCapital, L223_GlobalIntTechCapital]
origFilename = ['L223.GlobalTechCapital_elec', 'L223.GlobalIntTechCapital_elec']
positionOfchanged_file = [16, 17]

start = time.clock()  # timer to keep track of how long it takes
## because of the fact that we want to do CCS replacementes in L223 Global Tech Caputal, There is no need to filter out technoologies that aren't in our
# initial selection.
for sample_Num in range(1, num_of_samples):
    # This part of the code replaces the values for the technologies we want.
# It then palces the modified files for the given sameple in a parent folder called All-Samples.
# A sub folder is then created for each sample called Sample-X where X is the sample number

    sample_Num_asSTR = str(sample_Num) # sample number as a string because I somehow had problems earlier during testing
    subdir = 'Sample-' + sample_Num_asSTR # name of sub directory by sample
    sampledir=os.path.join(allSamplesDir, subdir) # create a folder for that sample number
    os.mkdir(sampledir)

    newvals=createVals(sample_Num) #Create the new values to repalce
    createCCSvals(sample_Num, newvals)
    for CsvFile, name in zip(dfToModify,
                             origFilename):  # Here we start to replace the values in the both of the L223.GlobaalTechcap files
        startingRow=findStartingRow(CsvFile) # this tells us which row to start at. It looks at teh first row with 2010
        for row in range(startingRow, (CsvFile.shape)[0]): # This will let us replace all the values up to the last element in the CSV
            techFromCsv=CsvFile.iloc[row, 2] # This gets the name of the technology in the third collumn at a certain row
            if techFromCsv in newvals:  # This is a check just to make sure those technologies are in the dictionary
               CsvFile.iloc[row, 5] = newvals[techFromCsv].popleft() # replace the value of the technology in the CSV

        changed_File_path=os.path.join(sampledir,name+".csv")# This is the fileplath of the changed file
        CsvFile.to_csv(changed_File_path, encoding='utf-8', index=False) # We then conver to CSV file to overwrtie the previous one.

    outputXMLPAth =toXMLpath(sampledir,"path") # THis converts our directory path to the appropriate XML format
    BatchCSVXML.getElementsByTagName("outFile")[0].firstChild.data = outputXMLPAth + "/"+outputXMLName +"-"+ str(sample_Num) + ".xml"  # changing the output filename in the batch file
    for name,postion in zip(origFilename,positionOfchanged_file): # put each file in the config file
        modedFIlePath= outputXMLPAth + "/" + name + ".csv"
        BatchCSVXML.getElementsByTagName("csvFile")[postion].firstChild.data = modedFIlePath

        # parsing fixed offshore
    newresult_sample = Raw_resultsXL.parse("sample_" + str(sample_Num), skiprows=0)
    newresult_sample_float = Raw_resultsXL_float.parse("sample_" + str(sample_Num), skiprows=0)
    # constraieddf.loc[:,"exponent"][1] Grab the exponnet collum at row blah
    # RenewRsrcCurves_owe file to replace
    counter = 4  # this is the counter for the seconds sheet
    for country in range(0, (newresult_sample.shape)[0]):  # replaces values un both resource files of fixed and flaot
        # Raw_resultsXL_float

        RenewRsrcCurves_owe.loc[counter][3] = newresult_sample.loc[:, "maxSubResource"][country]
        RenewRsrcCurves_owe.loc[counter][4] = newresult_sample.loc[:, "mid_price"][country]
        RenewRsrcCurves_owe.loc[counter][5] = newresult_sample.loc[:, "exponent"][country]

        counter += 1
        RenewRsrcCurves_owe.loc[counter][3] = newresult_sample_float.loc[:, "maxSubResource"][country]
        RenewRsrcCurves_owe.loc[counter][4] = newresult_sample_float.loc[:, "mid_price"][country]
        RenewRsrcCurves_owe.loc[counter][5] = newresult_sample_float.loc[:, "exponent"][country]
        counter += 1

    # This is where we still start to replace files in the L223.GlobalTechEff_elec.csv file
    CCS_Energy_Penalty = createEffvals(sample_Num)
    for row in range(effstartingrow, (GlobalTechEff_elec.shape)[0]):
        currentefftech = GlobalTechEff_elec.iloc[
            row, 2]  # This gets the name of the technology in the third collumn at current row
        if currentefftech in CCS_Energy_Penalty:  # check if that technolgy has a value to be replaced
            # print("current tech is " + currentefftech)
            # print("I am currently on " + currentefftech)
            GlobalTechEff_elec.iloc[row, 5] = CCS_Energy_Penalty[currentefftech].popleft()
    GlobalTechEff_elec_path = os.path.join(sampledir,
                                           "L223.GlobalTechEff_elec.csv")  # This is the fileplath of the changed file
    GlobalTechEff_elec.to_csv(GlobalTechEff_elec_path, encoding='utf-8',
                              index=False)  # We then conver to CSV file to overwrtie the previous one.
    outputXMLPAth = toXMLpath(sampledir, "path")  # THis converts our directory path to the appropriate XML format
    BatchCSVXML.getElementsByTagName("csvFile")[15].firstChild.data = \
        outputXMLPAth + "/L223.GlobalTechEff_elec.csv"  # This changes the path name to our name

    # findStartingRow(df)
    # GlobalTechCost_en
    # This is where we replace the values needed to make the energy transofrmation file
    # first we do bioliqud costs
    GlobalTechCostVals = createBioliquidcosts(sample_Num)
    for row in range(GlobalTechCost_en_start, GlobalTechCost_en.shape[0]):
        currentefftech = GlobalTechCost_en.iloc[row, 2]
        if currentefftech in GlobalTechCostVals:  # check if that technolgy has a value to be replaced
            GlobalTechCost_en.iloc[row, 5] = GlobalTechCostVals[currentefftech].popleft()  # replace the val
    GlobalTechCost_path = os.path.join(sampledir,
                                       "L222.GlobalTechCost_en.csv")  # This is the fileplath of the changed file
    GlobalTechCost_en.to_csv(GlobalTechCost_path, encoding='utf-8',
                             index=False)  # We then conver to CSV file to overwrtie the previous one.

    # starting row GlobalTechCoef_enstart
    # The file to change GlobalTechCoef_en
    GlobalTechCoef_enVALS = createBioliquidcoeff(sample_Num)
    for row in range(GlobalTechCoef_enstart, GlobalTechCoef_en.shape[0]):
        currtech = GlobalTechCoef_en.iloc[row, 2]  # the technology that it is currently on
        if currtech in GlobalTechCoef_enVALS:  # check if that technolgy has a value to be replaced
            GlobalTechCoef_en.iloc[row, 5] = GlobalTechCoef_enVALS[currtech].popleft()  # replace the val
    GlobalTechCoef_path = os.path.join(sampledir,
                                       "L222.GlobalTechCoef_en.csv")  # This is the fileplath of the changed file
    GlobalTechCoef_en.to_csv(GlobalTechCoef_path, encoding='utf-8',
                             index=False)  # We then conver to CSV file to overwrtie the previous one.

    # This is where we change the energy transofmration batch file
    # Batch_en_transformation outFile
    # toXMLpath(allSamplesDir,"")
    # entransform_outfilepath="C:/Users/owner/PycharmProjects/REU_ResearchLab/All-Samples/Sample-"+sample_Num_asSTR+"//en_transformationALL-"+sample_Num_asSTR+".xml"
    entransform_outfilepath = toXMLpath(allSamplesDir,
                                        "") + "/" + subdir + "//" + "en_transformationALL-" + sample_Num_asSTR + ".xml"

    Batch_en_transformation.getElementsByTagName("csvFile")[11].firstChild.data = toXMLpath(GlobalTechCoef_path, 'file')
    Batch_en_transformation.getElementsByTagName("csvFile")[12].firstChild.data = toXMLpath(GlobalTechCost_path, 'file')
    Batch_en_transformation.getElementsByTagName("outFile")[
        0].firstChild.data = entransform_outfilepath  # changing outfile name

    newBatch_en_transformation = open("batch_en_transformation.xml", "w")
    Batch_en_transformation.writexml(newBatch_en_transformation)  # save changes to file
    newBatch_en_transformation.close()

    # save replaceed Data into the sample folder
    RenewRsrcCurves_owe.to_csv(os.path.join(sampledir, "L210.RenewRsrcCurves_wind.csv"), encoding='utf-8', index=False)
    # pdate batch file with location of  changed file
    # change the ouput file
    Offshore_batch.getElementsByTagName("command")[0].getElementsByTagName("outFile")[
        0].firstChild.data = outputXMLPAth + "Fixed_offshoreWind" + "-" + str(sample_Num) + ".xml"
    # change teh location of the updated csv file
    Offshore_batch.getElementsByTagName("command")[0].getElementsByTagName("csvFile")[
        2].firstChild.data = outputXMLPAth + "L210.RenewRsrcCurves_wind.csv"

    newBatch_offshore = open("Offshore_batch_techspec.xml", "w")
    Offshore_batch.writexml(newBatch_offshore)  # save changes to file
    newBatch_offshore.close()

    newBatch_config = open("BatchCSV_elec_techspec.xml", "w")
    BatchCSVXML.writexml(newBatch_config)  # save changes to file
    newBatch_config.close()
    # create the new resource file

    # batch_en_transformation.xml
    call(['java', '-jar', 'CsvTOXML.jar',
          "BatchCSV_elec_techspec.xml"])  # batch convert The CSVs to XML file. Electricity file
    call(['java', '-jar', 'CsvTOXML.jar',
          "Offshore_batch_techspec.xml"])  # batch convert The CSVs to XML file. Resource file
    call(['java', '-jar', 'CsvTOXML.jar',
          "batch_en_transformation.xml"])  # batch convert The CSVs to XML file. Resource file

    # All-Samples/Sample-1/en_transformationALL-1.xml
    updateConfig(sampledir,  # Directory of the sample number
                 str(sample_Num),  # sample number
                 "../input/All-Samples/" + subdir + "/" + outputXMLName + "-" + str(sample_Num) + ".xml",
                 # directory for electricity file
                 "../input/All-Samples/" + subdir + "/" + "Fixed_offshoreWind" + "-" + str(sample_Num) + ".xml",
                 "../input/All-Samples/" + subdir + "/" + "en_transformationALL" + "-" + str(sample_Num) + ".xml"
                 )  # add directory for the new resource

    print("sample-"+str(sample_Num)+" is done")

end = time.clock()
Ex_time = (end - start) / 60
print("All samples are done. this took " + str(Ex_time) + " min")

