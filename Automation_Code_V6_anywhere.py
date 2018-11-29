import pandas as  pd
import math as Math
import csv,os
from xlsxwriter.workbook import Workbook
import time
from subprocess import call
from collections import deque
from xml.dom.minidom import parse
from shutil import rmtree,copy 
from numpy import log, exp

def formulacalc(val2030, currentYear, maxVal, minVal): # THis caclulatees the elicitation units with an updted formula
    if val_2015 > val2030:
        m = -(1 / 15) * log((val2030 - minVal) / (val_2015 - minVal))
        return minVal + (val_2015 - minVal) * exp(-m * (currentYear-2010))

    m = -(1 / 15) * log((val2030 - maxVal) / (val_2015 - maxVal))
    return maxVal + (val_2015 - maxVal) * exp(-m * (currentYear-2010))
def createVals(samplenum):
    #For a given sample , this will generate a Dictinoary of values for the technologies choosen
    #As well as the storage costs
    newdict= dict() # Dictionary to hold all of the values
    for Tech in techList: # THis gets all technologies in the intermediate feild
        if Tech=="rooftop_pv":
            continue
        temparry = list()
        temparry2=list()
        # Prices_2030.loc[["Max"]]["wind"][0] this will select the max value in the wind colum
        # Prices_2030.loc[1]["solar"] This will look at sample 1 in the solar collum
        sampleVal = Prices_2030.loc[samplenum][Tech]
        maxval = Prices_2030.loc[["Max"]][Tech][0]
        minVal = Prices_2030.loc[["Min"]][Tech][0]
        for t in range(2010,2105,5): ## calulate the values for each technology
            temparry.append(formulacalc(sampleVal,t,maxval,minVal)/Elicitation_to_GCAM_Conversion_Factors)
        intermediateTech= Prices_2030.loc[["intermediate Tech"]][Tech][0]

        newdict[intermediateTech]=deque(temparry)
        if(len(StorageCosts.loc[StorageCosts["Technology"]==intermediateTech].index.values)==0): # this checks if the choosen technology has a storage cost
            continue
        storageName=StorageCosts.loc[StorageCosts["Technology"]==intermediateTech].index.values[0]

        for pos in range(0,temparry.__len__()):
            temparry2.append(StorageCosts.loc[storageName][pos+2]+temparry[pos]) # the plus to is to offset for the two extra collums
        newdict[storageName]=deque(temparry2)
        if(Tech=="solar"): # This is doing the rooftop PV if SOlar was choosen
            temparry2 = list() #empty the list
            for pos in range(0, temparry.__len__()):
                temparry2.append(temparry[pos]/StorageCosts.loc["rooftop_pv"][pos + 2])  # the plus to is to offset for the two extra collums
            newdict["rooftop_pv"] = deque(temparry2)
    return newdict
def toXLXS(fileName): # This converts a CSV to Xl. 
    """ Converts CSV to excell. Takes in a parameter of the filepath for a csv
           """
    # Pandas was not used because it does some strange formatting
    # most of these files that are created as XLSX are just to extract the dataframe and nothing else,
    # hence this is why a kunk filepath was used
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
    """This finds the index of the first 2010 row in the dataframe"""
    ###################################
    #hERE i AM MAKING THE ASSUMPTIONS THAT FOR MOST FILES THE STARTING 2010 WILL NOT BE THE SAME
    ###########################
    for i in range(0,(df.shape)[0]):
        row=df.iloc[i].tolist()# This is the entire row. I'll keep this for now for debugging purposes
        if 2010 in row: #if 2010 is in that row, Return the row number
            return i
def claerAllsamples():
    """This clears the AllSamples, and junk directories"""
    dirList = list()
    [dirList.append(x[0]) for x in os.walk("Original copy")]
    print("Deleting directories")
    if (os.path.isdir(allSamplesDir)):
        print("deleting all samples")
        rmtree(allSamplesDir)  # clear the directory

    if (os.path.isdir("Junk")):
        print("Clearing junk files")
        rmtree("Junk")  # clear the junk directory

    print("Deleting directories in original copy")
    if dirList.__len__() >= 1:  # if a directory exist
        [rmtree(directory) for directory in dirList if (directory != "Original copy")]  # delete direcotries except specific ones
    print("\nRestoring files...")
    copy((os.path.join(Original_copyDir,"Multi_scenario batch file.xml")),os.getcwd()) # reserach lab will be home dit that I wil eventusll make
    copy(os.path.join(Original_copyDir,"BatchCSV_elec.xml"), os.getcwd())  # restore the the other file
    copy(os.path.join(Original_copyDir,"configuration _ref.xml"),os.getcwd())
    os.mkdir(junkPath)  # creates a junk directory in working directory
    os.mkdir(allSamplesDir)  # creates a junk directory in working directory chagning directoryies
def updateConfig(cconfigPath, samplenum, elecfileLInk): # path to CSV really....
    """This creates a config file for each sample and poinnts the config to a corresponding Electricity file
               """

    ConfigFile.getElementsByTagName("ScenarioComponents")[0].getElementsByTagName("Value")[43].firstChild.data=elecfileLInk # reoalce link

    if (techList.__len__() >= 1):
        ConfigFile.getElementsByTagName("Strings")[0].getElementsByTagName("Value")[0].firstChild.data = tech_specDir.split("\\")[6] + "-"+samplenum # change the XML reference name
    else:
        ConfigFile.getElementsByTagName("Strings")[0].getElementsByTagName("Value")[0].firstChild.data = tech_specDir.split("\\")[6] + "-"+samplenum
    #ConfigFile.getElementsByTagName("Strings")[0].getElementsByTagName("Value")[0].firstChild.data=ConfigFile.getElementsByTagName("Strings")[0].getElementsByTagName("Value")[0].firstChild.data+str(sample_Num)

    newXMLFile = open(os.path.join(cconfigPath, "configuration.xml"), "w")  # save the final xml file

    ConfigFile.writexml(newXMLFile, indent="\n", addindent="", newl="")  # save changes to in the custom inputs.
def toXMLpath (fullpath,type): # Convert from Normal path to xml path
    """ Convert a normal filePath on windwos to a XML filepath for GCAm"""
    splitted=(fullpath.split('\\'))
    newPath=""
    if "file" ==type:
        if "" in splitted:
            splitted.remove("")
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

allSamplesDir = os.path.join(os.getcwd(), "All-Samples")# The generated samples will be in the all samples folder
junkPath=os.path.join(os.getcwd(),"Junk") # randomly generated files are stored heere. Don't worry about this
Original_copyDir=os.path.join(os.getcwd(),"Original copy") # The directory where the "orginal copy" folder will reside
claerAllsamples()# This empties the All-Samples directories of the previous run
ConfigFile = parse("configuration _ref.xml") # this open the configuration file
val_2015=1800 ### Change this to constant as needed

Elicitation_to_GCAM_Conversion_Factors=3.23675216405277
raw_Data_file = pd.ExcelFile("newEL.xlsx") # Load the entire Excell sheet
Prices_2030 = raw_Data_file.parse('2030Values', skiprows=0) # Open the sheet of 2030 values
StorageCosts=raw_Data_file.parse('StorageCosts', skiprows=0) # opens the sheet of storage cost and the PC ratios
BatchCSVXML = parse("BatchCSV_elec.xml") # The batch CSV to Excell file.
nodeList=BatchCSVXML.getElementsByTagName("command")[0].childNodes # get the list of elemtns in the csv

outputXMLName= "Electricity" # output XML name for the samples
positionOfchanged_file=list()# This is the postion of the changed file in the XML.
CsvFiles=list()# list of CSV files to change
dfToModify =list()# this will store the dataframwes that need to be changed
techList=list() # will hold the name of technologies that we selected
techDF=list()# will hold the dataframes of hte tecchs we want
subtechList=list()# Will hold all of hte sub techs
techdic= dict() #empty dictionary to hold the subtech and their capital costs
origFilename=list() # A list to hold the original file names

#list(Prices_2030) returns all the collum names of the dataframe
for tech in range(0,list(Prices_2030).__len__()): # THis prints the technologues current availble in the input excell file
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


# This part will Filter out every other technology that is not needed. This is necesarry for GCAM
for node in range(13, nodeList.length-2):
    if(nodeList[node].nodeType==1): # check if this is an element with a file path

        unformat_Path = nodeList[node].firstChild.data  #get the unformatted file path from our BatchCSV file
        correctPath=toNormalFilePath(unformat_Path)# converting the path to a proper one we can use
        FileName = toXLXS(correctPath)  # convert the input file to xlsx so we can keep the technologies that we want
        raw_file_as_XL = pd.ExcelFile(os.path.join(junkPath,FileName + '.xlsx'))  # Load the entire Excell sheet
        new_input_file = raw_file_as_XL.parse("Sheet1", skiprows=0)  #Dataframe of input file
        row_df =  new_input_file.iloc[3].tolist()  # This is the entire label row as a list
        #subSec_collumn=list()# initializing an empty list to be referenced later on
        rowstoDelete = list() # initialize an empty list to hold all the rows to be deleted

        if "subsector.name" in row_df: # checking for subsector name in the files that are not consistant
            subSec_collumn=row_df.index("subsector.name") # the collum that subsector is located
        else:
            if "subsector" in row_df:
                subSec_collumn = row_df.index("subsector")  # the collum that subsector is located


        for row in range(4, (new_input_file.shape)[0]):  # This is where we choose the row to start from in each excell file since it changes
            if not set([new_input_file.iloc[row, subSec_collumn]]).issubset(techList):
                rowstoDelete.append(row)

        if (nodeList[node + 1].nodeType == 8): # anticipating wind and solar specifically because in some cases, we can selected those technolgoeis and have no rows to remove.
            if (nodeList[node + 1].data == 'Wind Solar' and (set(['wind', "offshore wind",'solar', 'rooftop_pv']).issubset(techList) or "wind" in techList or "offshore wind" in techList)):
                # CsvFiles.append(Onlytech)
                origFilename.append(FileName)  # this will write the file name to a blank spot
                positionOfchanged_file.append(node)
                dfToModify.append(new_input_file)

        if rowstoDelete:
            new_input_file.drop(rowstoDelete,inplace=True) # delete the rows
            Onlytech = os.path.join(tech_specDir, FileName + ".csv") # new file path in a differnt folder just for that tech
            new_input_file.to_csv(Onlytech, encoding='utf-8', index=False)  # write the CSV to anew path for tech specific tech
            # here we reformat the path so that it is in xml GCAM formatt
            #splitted = (Onlytech.split('\\'))
            xmlFormmated_path= toXMLpath(Onlytech,"file") # Convert the file path to an XML one.
            # Now we join the list to make the xmlformatted path
            BatchCSVXML.getElementsByTagName("command")[0].childNodes[node].firstChild.data=xmlFormmated_path # updates the file with only specific techs
            if (nodeList[node + 1].nodeType == 8 ):  # add the files that we need to change to thaat list
                if(nodeList[node + 1].data== 'Change this'):
                    #CsvFiles.append(Onlytech)
                    origFilename.append(FileName) # this will write the file name to a blank spot
                    positionOfchanged_file.append(node)
                    dfToModify.append(new_input_file)

print("Done filtering tech")
newBatch = open(newBatchFilePath, "w") # save a new batch file with the changes that we made
BatchCSVXML.writexml(newBatch)  # save changes to file
newBatch.close()

BatchCSVXML = parse(newBatchFilePath) #Load the variable with the new batch file.

print("Done filtering uneeded technologies")

print("Start!")

start=time.clock() # timer to keep track of how long it takes.
for sample_Num in range(1,num_of_samples):
# This part of the code replaces the values in GCAM CSVS for the technologies we want.
# It then palces the modified files for the given sameple in a parent folder called All-Samples.
# A sub folder is then created for each sample called Sample-X where X is the sample number

    sample_Num_asSTR = str(sample_Num) # sample number as a string because I somehow had problems earlier during testing
    subdir = 'Sample-' + sample_Num_asSTR # name of sub directory by sample
    sampledir=os.path.join(allSamplesDir, subdir) # create a folder for that sample number
    os.mkdir(sampledir)

    newvals=createVals(sample_Num) #Create the new values to repalce
    for CsvFile, name in zip(dfToModify, origFilename): # Here we start to replace the values in the csv files
        startingRow=findStartingRow(CsvFile) # this tells us which row to start at. It looks at teh first row with 2010
        for row in range(startingRow, (CsvFile.shape)[0]): # This will let us replace all the values up to the last element in the CSV
            techFromCsv=CsvFile.iloc[row, 2] # This gets the name of the technology in the third collumn at a certain row
            if techFromCsv in newvals: # This is a check just to make sure those technologies are int the dictionary
               CsvFile.iloc[row, 5] = newvals[techFromCsv].popleft() # replace the value of the technology in the CSV

        changed_File_path=os.path.join(sampledir,name+".csv")# This is the fileplath of the changed file
        CsvFile.to_csv(changed_File_path, encoding='utf-8', index=False) # We then conver to CSV file to overwrtie the previous one.

    outputXMLPAth =toXMLpath(sampledir,"path") # THis converts our directory path to the appropriate XML format
    BatchCSVXML.getElementsByTagName("outFile")[0].firstChild.data = outputXMLPAth + "/"+outputXMLName +"-"+ str(sample_Num) + ".xml"  # changing the output filename in the batch file
    for name,postion in zip(origFilename,positionOfchanged_file): # put each file in the config file
        modedFIlePath= outputXMLPAth + "/" + name + ".csv"
        BatchCSVXML.getElementsByTagName("command")[0].childNodes[postion].firstChild.data=modedFIlePath

    newBatch=open("BatchCSV_elec_techspec.xml","w")
    BatchCSVXML.writexml(newBatch)# save changes to file
    newBatch.close()
    call(['java', '-jar', 'CsvTOXML.jar', "BatchCSV_elec_techspec.xml"]) # batch convert The CSVs to XML file using GCAMS CSV to XML file
    updateConfig(sampledir,str(sample_Num),"../input/All-Samples/"+subdir + "/" + outputXMLName +"-" + str(sample_Num) + ".xml" ) # Now we update the config file
    print("sample-"+str(sample_Num)+" is done")

end = time.clock()
Ex_time = (end - start) / 60
print("All samples are done. this took " + str(Ex_time) + " min")





