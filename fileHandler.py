import os
import io
import time
import shutil
import pandas as pd
from pathlib import Path
from pdfminer.high_level import extract_text
from pypdf import PdfReader, PdfWriter

import logger

# find all files in specified folder
def getFileList(folder):
    try:
        # need to test this more
        return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(".pdf")]
    except FileNotFoundError:
        print(f"Error: Folder not found!")
        return []
    
# load all pages in file
def loadPages(path):
    startTime = time.time()
    totalPages = len(PdfReader(path).pages)

    fullText = ""
    logger.vprint(f"Extracting from: {path}, {totalPages} pages")

    # extract text
    for page_number in range(1, totalPages + 1):
        pageStartTime = time.time()

        pageText = extract_text(path, page_numbers=[page_number - 1])  # pdfminer uses zero-based index
        fullText += pageText
        fullText += "\n----------\n"

        pageEndTime = time.time()
        logger.vprint(f"page {page_number} of {totalPages} ({pageEndTime - pageStartTime:.2f} seconds)")

    endTime = time.time()
    logger.vprint(f"Total time: {endTime - startTime:.2f} seconds")

    return fullText

def detectLargeFiles(folder, files, splitThreshold):
    maxPages = 0
    largeFiles = []

    for file in files:
        path = os.path.join(folder, file)
        totalPages = len(PdfReader(path).pages)

        # if current file has more than max, then it is the new max
        if totalPages > maxPages:
            maxPages = totalPages
        
        # if file is large, add to large file list
        if totalPages > splitThreshold:
            largeFiles.append(file)

    if maxPages > splitThreshold:
        return largeFiles
    else:
        return []
    
def detectLongNames(files, filenameThreshold):
    longNames = False
    for file in files:
        if len(file) > filenameThreshold:
            longNames = True

    return longNames

def shortenNames(folder, tempFolder, filenameLength):
    # create temp folder
    if Path(tempFolder).exists() and Path(tempFolder).is_dir():
        shutil.rmtree(tempFolder)
    os.makedirs(tempFolder)

    # copy out all files
    for filename in os.listdir(folder):

        #print(f"original filename = {filename}")
        origFile = os.path.join(folder, filename)
        

        if os.path.isfile(origFile) and filename.lower().endswith('.pdf'):
            if len(filename) > filenameLength:
                newFilename = filename[-filenameLength:]
                logger.vprint(f"{filename} renamed to {newFilename}")
            else:
                newFilename = filename

        copyFile = os.path.join(tempFolder, newFilename)
        logger.vprint(f"{origFile} shortened to: {copyFile}")
        shutil.copy(origFile, copyFile)

    
def splitPdf(tempFolder, filename, splitThreshold):
    # split big file
    filepath = os.path.join(tempFolder, filename)

    logger.vprint(f"Splitting file: {filepath}")
    reader = PdfReader(filepath)
    totalPages = len(reader.pages)
    #print(totalPages)

    for start in range(0, totalPages, splitThreshold):
        writer = PdfWriter()
        end = min(start + splitThreshold, totalPages)

        for i in range(start, end):
            writer.add_page(reader.pages[i])
    
        output = f"{filename} (pg{start + 1}-{end}).pdf"
        outputPath = os.path.join(tempFolder, output)

        with open(outputPath, "wb") as outputFile:
            writer.write(outputFile)
        logger.vprint(f"Saved: {outputPath}")

    # delete original file
    os.remove(filepath)


def largeFileSplitter(folder, tempFolder, largeFiles, splitThreshold):
    # create temp folder
    if Path(tempFolder).exists() and Path(tempFolder).is_dir():
        shutil.rmtree(tempFolder)
    os.makedirs(tempFolder)

    # copy out all files
    for filename in os.listdir(folder):
        origFile = os.path.join(folder, filename)
        copyFile = os.path.join(tempFolder, filename)

        if os.path.isfile(origFile) and filename.lower().endswith('.pdf'):
            shutil.copy(origFile, copyFile)
            logger.vprint(f"Copied: {filename} from {folder} to {tempFolder}")

    for filename in os.listdir(tempFolder):
        if filename in largeFiles:  # if the file is in the large file list
            copyFile = os.path.join(tempFolder, filename)

            splitPdf(tempFolder, filename, splitThreshold)

def exportTasks(allTasks, output, origFolder, files, engineType):
    # allTasks pairs: [dfHeaderDict, taskDict]
    #print("exportTasks")
    #print(allTasks)
    logger.vprint("Exporting tasks")
    fullDfList = []

    for file in allTasks:

        fullDf = pd.DataFrame(columns=["Task", "Task Title", "Subtask", "Subtask Title", "Subtask Text"])  # init
        index = 0

        #print(f"\nsingle file: {file}")
        taskDict, subtaskDict = file[0], file[1]

        separator = " | "
        # something weird happening here
        for task, taskTitle in taskDict.items():

            # for each task:
            # using task, find subtasks from subtaskDict
            subtaskList = subtaskDict[task]
            #print(task, subtaskList)
            
            # write into df
            for subtaskContent in subtaskList:
                subtask, subtaskTitle, subtaskText = subtaskContent[0], subtaskContent[1], separator.join(subtaskContent[2])
                #print(task, taskTitle, subtask, subtaskTitle, subtaskText)
                fullDf.loc[len(fullDf)] = [task, taskTitle, subtask, subtaskTitle, subtaskText]

        index +=1
        fullDfList.append(fullDf)
        logger.tprint(fullDf)
        
    filename = f"{output}_tasks_{origFolder}.csv"

    while True:
        try:
            with open(filename, 'wb') as rawFile:
                with io.TextIOWrapper(rawFile, encoding='utf-8', errors='ignore', newline='') as f:
                    f.write(f'"TYPE: {engineType}"\n')  # tells which engine type
                    f.write("\n")
                    
                    for i, df in enumerate(fullDfList):
                        f.write(f'"FILE: {files[i]}"\n')
                        df.to_csv(f, index=True, header=False)
                        f.write("\n")
            logger.vprint(f"{filename} saved")
            break

        except PermissionError as e:
            print(f"Error saving {filename}")
            print(f"PermissionError: {e}")
            response = input("If the file is open, please close the file: (y/n): ").strip().lower()

            if response != 'y':
                logger.vprint("File not saved")
                break



    

def exportSteps(stepsDict, output, folder, merge):
    #print(f"exportSteps stepsDict {stepsDict}")
    filename = f"{output}_steps_{folder}.xlsx"

    while True:
        try:

            with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
                workbook = writer.book
                worksheet = workbook.add_worksheet()
                writer.sheets['Sheet1'] = worksheet

                borderFormat = workbook.add_format({'border': 1})  # 1 = thin border

                row = 0
                for file, df in stepsDict.items():
                    #print(file)
                    #print(stepsDf)

                    # write filename
                    worksheet.write(row, 0, file)
                    row += 1

                    #startDataRow = row  # for data to start merging
                    # write header row
                    for colIdx, colName in enumerate(df.columns):
                        worksheet.write(row, colIdx, colName, borderFormat)
                    headerRow = row  # set to current row
                    row += 1

                    # write data
                    dataStartRow = row  # set to current row
                    nRows, nCols = df.shape

                    subtaskTitles = 4  # column
                    # check if there are subtask titles (col idx 4)
                    if (df.iloc[:, subtaskTitles] == "").all():  # xwb has no subtask titles
                        nonStepsCols = [0, 1, 2, 3]
                        stepsCols = [4, 5]
                    else:
                        nonStepsCols = [0, 1, 2, 3, 4]
                        stepsCols = [5]
                
                    for colIdx in nonStepsCols:
                        r = 0

                        if merge:
                            while r < nRows:
                                
                                value = df.iat[r, colIdx]

                                start = r  # start counting
                                while ((r+1) < nRows) and (df.iat[r+1, colIdx] == value):
                                    r += 1
                                end = r

                                chunkStart = dataStartRow + start
                                chunkEnd = dataStartRow + end

                                if start == end:  # single row
                                    worksheet.write(chunkStart, colIdx, value, borderFormat)

                                else:
                                    worksheet.merge_range(chunkStart, colIdx,
                                                          chunkEnd, colIdx,
                                                          value,
                                                          borderFormat)
                                r += 1

                            row = dataStartRow + nRows + 1  # move to next file
                        else:
                            while r < nRows:
                                value = df.iat[r, colIdx]
                                worksheet.write(dataStartRow + r, colIdx, value, borderFormat)
                                r += 1

                            row = dataStartRow + nRows + 1
                    
                    # don't merge steps
                    for colIdx in stepsCols:
                        r = 0
                        while r < nRows:
                            value = df.iat[r, colIdx]
                            worksheet.write(dataStartRow + r, colIdx, value, borderFormat)
                            r += 1

                        row = dataStartRow + nRows + 1


                break

        except PermissionError as e:
            print(f"Error saving {filename}")
            print(f"PermissionError: {e}")
            response = input("If the file is open, please close the file: (y/n): ").strip().lower()

            if response != 'y':
                logger.vprint("File not saved")
                break


            


