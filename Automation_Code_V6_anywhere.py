import pandas as  pd
import math as Math
import csv,os
from xlsxwriter.workbook import Workbook
import time
from subprocess import call
from collections import deque
from xml.dom.minidom import parse
from shutil import rmtree,copy # just to clear things

"""
Hi
Here's a break down of the directories

All-Samples: The samples that will be placed on the cluster. Paste the entire folder onto the cluster
The code automatically create the all sample files. These are GCAM input files.

Original Copy: These are unmodified files that are kept as a reference, before modification.

folders in Original Copy: These are modied files from original copy that has just the technologies that you want to run

Makking the code run:

1. make sure you have a folder called Original Copy

2. inside of oringinal Copy, open the file called "BatchCSV_elec.xml" and change ALL the paths to your paths. 


General instructions**********************
If you would like to make changes to the configuration file, make your changes to the "Configuration_ref.mxl" inside of original copy
    
"""


def elicitation_Units_calc(sample_value, currentYear, Gcam_StartValue, costFloor, min, max_value): # THis caclulatees the elicitation units.
    # offset is the year that you start at 0 is 2015
    # make sure to fix the else ifs
    Max_Value = max(sample_value * (costFloor / 100),
                    Gcam_StartValue + ((sample_value -  Gcam_StartValue) / (1 - beta)) * (
                    1 - Math.pow(beta,(currentYear - startYear) / (baseYear-startYear))))
    if(currentYear==startYear): # if D18=start Year
        return Gcam_StartValue # Return B10
    else:
        if (currentYear == baseYear):#D$18=Base_Year
            return sample_value#,$B$9
        else:
            if (currentYear <baseYear):  # D$18<Base_Year

                return Gcam_StartValue+((sample_value-Gcam_StartValue)/(1-beta))*(
                1 - Math.pow(beta,(currentYear -startYear) / (baseYear-startYear)))
            else:
                if(Max_Value>max_value):
                    return max_value
                else:
                    if (Max_Value< min):
                        return min
                    else:
                        return Max_Value
def toXLXS(fileName): # This converts a CSV to Ecell.
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
    """This finds the index first row to start replacing values from
        """

# return a list with the row nad collum index
# if the 2015 postion is the exact same for all of the files
# Then get rid of this method to save like 1 or 2 seconds
    # we are looking for the right row ofr where we need to start in 2015
    ###################################
    #HERE i AM MAKING THE ASSUMPTIONS THAT FOR MOST FILES THE STARTING 2015 WILL NOT BE THE SAME
    ###########################
    for i in range(0,(df.shape)[0]):
        row=df.iloc[i].tolist()# This is the entire row. I'll keep this for now for debugging purposes
        if 2010 in row: #if 2015 is in that row, Return the row number
            return i
def clearAllandReset():# clears all files from the current working directory and restores the original files back
    dirList=list()
    [dirList.append(x[0]) for x in os.walk("Original copy")]
    print("Deleting directories")
    if(os.path.isdir("All Samples")):
        rmtree("All Samples") # clear the directory

    if (os.path.isdir("Junk")):
        rmtree("Junk")  # clear the junk directory

    if dirList.__len__()>=1: # if a directory exist
        [rmtree(directory) for directory in dirList if (directory!= "Original copy\\OffshoreWind Added" and directory!= "Original copy")] # delete direcotries except specific ones
    print("Restoring filles to original state and recreating deleted directories")
    copy("Original copy/Multi_scenario batch file.xml","Multi_scenario batch file.xml") # reserach lab will be home dit that I wil eventusll make
    copy("Original copy/BatchCSV_elec.xml", "BatchCSV_elec.xml")  # restore the the other file
    os.mkdir(junkPath)  # creates a junk directory in working directory
    os.mkdir("All Samples")  # creates a junk directory in working directory
def updatedic(sample_number):#This will upfate all the values in the dictioanry and prepate them to be repalcesd in the excelll
    """This will update the dicinary depenidng on what sample you need
                   """
    for key, value in techdic.items(): # update the main technologies with their capital cost
        if value[1]=="none":
            overnighCapCost=list()
            sample_value=sample_LCOE_MOD.loc[sample_number + 7, key]
            for year in range(2010, 2105,5):
                #Gcam_Start_year.loc[Gcam Start Values,"wind"])
                overnighCapCost.append(round(
                    elicitation_Units_calc(
                        sample_value,
                        year,
                        Gcam_Start_year.loc["Gcam Start Values",key] # Gcam Start values
                        ,techdic[key][0], # floor cost
                        sample_LCOE_MOD.loc[4,key],#min value
                        sample_LCOE_MOD.loc[5,key]) # Max value
                        /Elicitation_to_GCAM_Conversion_Factors))
            techdic[key][3] = deque(overnighCapCost)
    for key, value in techdic.items():
        # techdic[subtechName] = [parent_Tech, operation, constant_array, list()]  #These store 4 things for each sunnb tech
        if value[1]!= "none": # nwo we update all the sub technologies
            if value[1]=="+":
                newcapcost=list()# This is where the numbers for the new capcost will be stored
                constantValue=value[2] # The constant value weather it be the sotrage cost or the ratio
                capCostOfTech=techdic[value[0]][3]
                [newcapcost.append(round(capcost+value)) for capcost,value in zip(capCostOfTech, constantValue)] # doiing a list comphresniosn on both of them
                techdic[key][3]= deque(newcapcost)
            else:
                if value[1] == "/":
                    newcapcost = list()  # This is where the numbers for the new capcost will be stored
                    constantValue = value[2]  # The constant value weather it be the sotrage cost or the ratio
                    capCostOfTech = techdic[value[0]][3]
                    [newcapcost.append(round(capcost/value)) for capcost, value in zip(capCostOfTech, constantValue)]  # doiing a list comphresniosn on both of them
                    techdic[key][3] = deque(newcapcost)
def claerAllsamples():
    """This clears the AllSamples, and junk directories
               """
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
    """This creates a a config file for each sample and poinnts the config to a corresponding Electricity file
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
    """ Convert a normal filePath on windwos to a XML filepath for GCAm
               """
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
    """ converts XML to Normal file path
               """
    xmlPath = (xmlPath.split('/'))
    drive = xmlPath[0]
    xmlPath.remove(drive)
    if "" in xmlPath:
        xmlPath.remove("")
    correctPath = os.path.join(drive+"\\", *xmlPath)  # this has the csv

    return correctPath

allSamplesDir = os.path.join(os.getcwd(), "All-Samples")# The generated samples will be in the all samples folder
junkPath=os.path.join(os.getcwd(),"Junk") # randomly generated files are stored heere. Don;t worry about this
Original_copyDir=os.path.join(os.getcwd(),"Original copy") # The directory where the "orginal copy" folder will reside
claerAllsamples()# This empties the All-Samples directories
ConfigFile = parse("configuration _ref.xml")
baseYear=2030
startYear=2010
beta=.2

Elicitation_to_GCAM_Conversion_Factors=3.23675216405277
raw_Data_file = pd.ExcelFile("All Inputs.xlsx")  # Load the entire Excell sheet
Onshore_Wind = raw_Data_file.parse('Onshore Wind', skiprows=0) #onshore wind sheet
sample_LCOE = raw_Data_file.parse('Sampled_LCOE', skiprows=0) #sample LCOE sheet
sample_LCOE_MOD=raw_Data_file.parse("Sample_LCOE_MOD",skiprows=0) # a sheet that has data needed to do calculations later int the code
BatchCSVXML = parse("BatchCSV_elec.xml") # The batch CSV to Excell file.
Gcam_Start_year=raw_Data_file.parse("Gcam Start year values")
nodeList=BatchCSVXML.getElementsByTagName("command")[0].childNodes # get the list of elemtns in the csv

outputXMLName= "Electricity" # output XML name for the samples
positionOfchanged_file=list()# This is the postion of the changed file in the XML.
CsvFiles=list()# list of CSV files to change
dfToModify =list()# this will store the dataframwes that need to be changed
techList=list() # will hold the name of technologies that we slecected want
techDF=list()# will hold the dataframes of hte tecchs we want
subtechList=list()# Will hold all of hte sub techs
techdic= dict() # empyt dictionariy to hold the subtech and their capital costs
origFilename=list() # A list to hold the orginal file naems


for tech in range(0,raw_Data_file.sheet_names.__len__()): # This prints out all the sheets in the All inputs excell file
    print(raw_Data_file.sheet_names[tech]+" is index "+str(tech))

user_input = input("\nPlease specify what technologies you want by index , in the order shown, separated by a single space only: ")

num_of_samples=int(input("\nHow many samples do you want: "))+1
print("\n")
[techList.append(raw_Data_file.sheet_names[int(i)]) for i in user_input.split(' ') if i.isdigit()] # create a list with teh tech that hte user wants

[techDF.append(raw_Data_file.parse(sheet, skiprows=0)) for sheet in techList] # Tuens the techs into dfs

techList=list()# clear the tech sheet list of previous entries

[techList.append((i.iloc[14,0].split(','))[1]) for i in techDF] # add the overall technology to a list. for ecample. Wind, solar , and nuvlear are the overall technologies.
if"solar" in techList: # I had to add an exception ,since Rooftop PV is actually its own entry
    techList.append("rooftop_pv")

# this will create a directory based on teh technologies you choose
tech_specDir=os.path.join(Original_copyDir,techList[0])
if(techList.__len__()>=1):
    for x in range(1,techList.__len__()):
        tech_specDir=tech_specDir+"-"+techList[x]
os.mkdir(tech_specDir)

newBatchFilePath=os.path.join(tech_specDir,"techSpecBatch.xml")# new file path for the modified batch file


# recname conif file appropiately
# this part of the code will filter out olny the technologies you want from the CSVs.
# so if you want WInd,solar, and Nuclear everyt other technology will be filtered out.
for node in range(13, nodeList.length-2):
    if(nodeList[node].nodeType==1): # check if this is an element with a file path

        unformat_Path = nodeList[node].firstChild.data  #get the unformatted file path
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
            new_input_file.drop(rowstoDelete,inplace=True) # delete the rows to get rid of wind
            Onlytech = os.path.join(tech_specDir, FileName + ".csv") # new file paht in a differnt folder just for that tech
            new_input_file.to_csv(Onlytech, encoding='utf-8', index=False)  # write the CSV to anew path for tech specific tech
            # here we reformatt the path so that it is in xml GCAM formatt
            #splitted = (Onlytech.split('\\'))
            xmlFormmated_path= toXMLpath(Onlytech,"file") # this is just to let me konw this is a file
            # Now we join the list to make the xmlformatted path
            #nodeList[node].data=xmlFormmated_path# here we replace the current xml with a new one, To constrsuct a new batch file
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

print("Done removing selected technologies")

# THis is where we initialize the dictionary
# the format goes as follows
# Key: value
# Sub technologies would be like rooftop PV, or offshore wind global
# Overall Tech woulud be somthing liek wind, solar, nuclear
#subtech:[OverallTech,operation to do, constnat, overallCap cost]
for sheet in techDF:# This part assigns each subtechnology to a place in the dictionary
    parent_Tech= sheet.iloc[15, 0]# this is similar to the overall tech
    for row in range(13,70,5):
        if (row>=sheet.shape[0]):
            break # straright up leave homeie if the row excededs the max rows
        operation= sheet.iloc[row,0] # this lets us know what operaiton to do
        subtechName = sheet.iloc[row+2, 0] # subtech name
        constant_array= sheet.iloc[row+3].tolist() # the array of constants wit hteh sub technologies
        if operation=="none": # This is a parent technolgogy so just create an entry for it in the dictionary
            techdic[parent_Tech]=[sheet.iloc[3, 1],"none",list(),list()]
            # cost Floor Value,empty list
        else:
            del constant_array[0]# delete a couple uncessary things at the beggining of the constant array
            del constant_array[0]
            techdic[subtechName] = [parent_Tech, operation, constant_array, list()]  #These store 4 things for each sunnb tech


############ end of creating dictionary
print("Start!")
#updatedic(1)


start=time.clock() # timer to keep track of how long it takes
for sample_Num in range(1,num_of_samples): # This part of the code replaces the values for the technologies we want, and creates a new electricity file
    sample_Num_asSTR = str(sample_Num) # sample number as a string because I somehow had problems earlier during testing
    subdir = 'Sample-' + sample_Num_asSTR # name of sub directory by sample

    sampledir=os.path.join(allSamplesDir, subdir) # create a folder for that sample number
    os.mkdir(sampledir)

    OvernightCapCostWIND = list() # a List to hold the overnight capital cost.
    # creata lsit of list ofor all technologies
    updatedic(sample_Num) # update the dictioanry with the values for hte current sample
    for CsvFile, name in zip(dfToModify, origFilename): # Here we start to replace the values in the csv files
        techdicCopy=dict(techdic) # we create a copy of the dictinary as to not affect the main dictionary
        OvernightCapCostWIND_copy = deque(OvernightCapCostWIND)  # this will let me pop each value as we replace them
        startingRow=findStartingRow(CsvFile) # this tells us which row to start at.
        for row in range(startingRow, (CsvFile.shape)[0]):
            techFromCsv=CsvFile.iloc[row, 2]
            if techFromCsv in techdicCopy: # This is a check just to make sure those technologies are int the dictionary
               CsvFile.iloc[row, 5] = techdicCopy[techFromCsv][3].popleft() # replace the value in teh CSV

        changed_File_path=os.path.join(sampledir,name+".csv")# This is the file plath of the changed file
        CsvFile.to_csv(changed_File_path, encoding='utf-8', index=False) # We then conver to CSV file to overwrtie the previous one.

    outputXMLPAth =toXMLpath(sampledir,"path")
    BatchCSVXML.getElementsByTagName("outFile")[0].firstChild.data = outputXMLPAth + "/"+outputXMLName +"-"+ str(sample_Num) + ".xml"  # changing the output filename in the batch file
    for name,postion in zip(origFilename,positionOfchanged_file): # put each file in the config file

        modedFIlePath= outputXMLPAth + "/" + name + ".csv"
        BatchCSVXML.getElementsByTagName("command")[0].childNodes[postion].firstChild.data=modedFIlePath

    newBatch=open("BatchCSV_elec_techspec.xml","w")
    BatchCSVXML.writexml(newBatch)# save changes to file
    newBatch.close()
    call(['java', '-jar', 'CsvTOXML.jar', "BatchCSV_elec_techspec.xml"]) # batch convert The CSV to XML file.
    updateConfig(sampledir,str(sample_Num),"../input/All-Samples/"+subdir + "/" + outputXMLName +"-" + str(sample_Num) + ".xml" ) # Now we update the config file
    print("sample-"+str(sample_Num)+" is done")



end = time.clock()
Ex_time = (end - start) / 60
print("All samples are done. this took " + str(Ex_time) + " min")





