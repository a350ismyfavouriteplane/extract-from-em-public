import os
import sys
import shutil
import re
from tabulate import tabulate  # for nice tables
import fileHandler
import logger
import dictionaries
import pandas as pd
from pathlib import Path
from openpyxl import Workbook

def rawText(folder, files, combine, output, origFolder):
    if combine:  # init a string for combined text if combined mode is on
        combinedText = ""

    for file in files:
        fullText = fileHandler.loadPages(os.path.join(folder, file))

        if combine:  # combined mode ON
            filename = f"{output}_raw_combined.txt"
            combinedText += f"\n### [{file}] ###\n"
            combinedText += fullText
            
            # only write the file when it is the last file of the files list
            if file == files[-1]:
                with open(filename, "w", encoding="utf-8") as file:
                    logger.vprint(f"Written file: {filename}")
                    file.write(combinedText)

        else:  # combined mode OFF
            foldername = Path(f"{output}_rawText_{origFolder}")
            filename = f"{output}_raw_{Path(file).stem}.txt"
            filepath = foldername / filename

            # only do a folder check if it is the first file of the files list
            if file == files[0]:
                # if the folder exists, delete it
                if foldername.exists() and foldername.is_dir():
                    shutil.rmtree(foldername)
                    logger.vprint(f"Existing folder deleted: {foldername}")

                # create a new folder if it doesn't exist and add new files inside
                os.makedirs(foldername)
                logger.vprint(f"Folder created: {foldername}")

            with open(filepath, "w", encoding="utf-8") as file:
                logger.vprint(f"Written file: {filename}")
                file.write(fullText)

def sectionSplit(fullText, engineType, tables):
    logger.vprint("Splitting sections")
    #print(f"tables = {tables}")

    # apply appropriate splitting
    pattern = dictionaries.splitterDict.get(engineType)
    splitText = fullText.split("----------")
    splitText = [re.split(pattern, section.strip()) for section in splitText]
    # not working for xwb!! :(

    # change to dataframe
    df = pd.DataFrame(splitText)
    try: logger.tprint(df)
    except: pass
    df.columns = ["header", "main", "footer"]
    df = df.dropna()

    '''
    # for debug
    if tables:
        logger.tprint(df)  # doesn't show the newlines but trust me they are there
    '''
        
    # handle header
    # may need to add something to handle different lengths of task titles
    taskListHeader = []  # init
    for header in df['header']:
        line = header.split("\n")

        # depending on each engine type
        if (engineType == "1000") or (engineType == "7000"):
            matchIndex = [i for i, item in enumerate(line) if 'Engine Manual' in item]
            #print(matchIndex)

            if len(matchIndex) == 2:
                # align to where the task is
                matchIndex = [matchIndex[1] + 1, matchIndex[1] + 3] # to get task and task title
                task = [line[i] for i in matchIndex]

                # alternate (when slicing is a bit wonky)
                # check if this even applies to T1000
                if 'export rating' in task[1].lower():
                    matchIndex[1] += 2
                    task = [line[i] for i in matchIndex]
            
                #print(task)
                taskListHeader.append(task)
            else:
                taskListHeader.append(['', ''])

        elif engineType == "XWB":
            matchIndex = [i for i, item in enumerate(line) if 'Engine Manual' in item]

            if len(matchIndex) == 2:
                matchIndex = [matchIndex[1] + 1, matchIndex[1] + 3] # to get task and task title
                task = [line[i] for i in matchIndex]
                
                if (task[0] == '') or (task[1] == ''):
                    matchIndex = [matchIndex[0] + 1, matchIndex[1] + 1, matchIndex[1] + 2]
                    task = [line[i] for i in matchIndex]
                    task[1] = task[1] + ' ' + task[2]
                    del task[2]

                if 'export rating' in task[1].lower():
                    matchIndex = [matchIndex[0], matchIndex[1] + 4, matchIndex[1] + 5, matchIndex[1] + 6]
                    task = [line[i] for i in matchIndex]
                    task[1] = task[1] + ' ' + task[2] + ' ' + task[3]
                    del task[2:4]

                taskListHeader.append(task)
            else:
                taskListHeader.append(['', ''])

        elif engineType == "900":
            matchIndex = [i for i, item in enumerate(line) if 'Engine Manual' in item]
            
            if len(matchIndex) == 2:
                matchIndex = [matchIndex[1] + 1, matchIndex[1] + 3] # to get task and task title
                
                task = [line[i] for i in matchIndex]
                
                if (task[0] == '') or (task[1] == ''):
                    matchIndex = [matchIndex[0] + 1, matchIndex[1] + 1, matchIndex[1] + 2]
                    task = [line[i] for i in matchIndex]
                    task[1] = task[1] + ' ' + task[2]
                    del task[2]
                    # might want to fix this for efficiency
                #print(task)

                if 'export rating' in task[1].lower():
                    matchIndex[1] += 2
                    task = [line[i] for i in matchIndex]
                    #print(task)
                
                taskListHeader.append(task)
            else:
                taskListHeader.append(['', ''])

        # for checking individual headers
        #headers = pd.DataFrame(line)
        #logger.tprint(headers)

    dfHeader = pd.DataFrame(taskListHeader)
    dfHeader.columns = ["Task", "Task Title"]
    #logger.tprint(dfHeader)

    # handle footer (optional)
    taskListFooter = []  # init
    for footer in df['footer']:
        line = footer.split("\n")

        if (engineType == "1000") or (engineType == "7000") or (engineType == "XWB") or (engineType == "900"):
            try:
                matchIndex = next(i for i, item in enumerate(line) if 'Page' in item)
                matchIndex -= 2 # to get task
                #print(matchIndex)
                task = line[matchIndex]
                #print(task)

                # impose min 16 char length for task title and need contain '-'
                if (len(task) >= 16) and ('-' in task):
                    taskListFooter.append(task)
                else:
                    taskListFooter.append('')
            except:
                taskListFooter.append('')

    dfFooter = pd.DataFrame(taskListFooter)
    dfFooter.columns = ["Task1"]
    #logger.tprint(dfFooter)

    # concat to original df and then look at subtasks
    dfFull = pd.concat([df, dfHeader, dfFooter], axis=1)
    logger.tprint(dfFull)

    # check that all tasks matches up (kinda optional)
    # extract cols "Task", "Task1"
    try:
        checkerHeaderDf = dfFull[["Task"]].query("Task != ''").drop_duplicates().reset_index(drop=True)
        checkerFooterDf = dfFull[["Task1"]].query("Task1 != ''").drop_duplicates().reset_index(drop=True)
        #logger.tprint(checkerHeaderDf)
        #logger.tprint(checkerFooterDf)

        if len(checkerHeaderDf) == len(checkerFooterDf):
            for i in range(len(checkerHeaderDf)):
                headerTask = checkerHeaderDf.loc[i, "Task"]
                footerTask = checkerFooterDf.loc[i, "Task1"]
                if headerTask.strip() == footerTask.strip():
                    logger.vprint(f"Task {headerTask} matched")
                else:
                    logger.vprint("May have missing tasks")

    except:
        logger.vprint("WARNING: May have missing tasks")

    mainText = []
    # handle main bodytext
    for text in df["main"]:
        line = text.split("\n")
        textDf = pd.DataFrame(line)
        #logger.tprint(textDf)
        mainText.append(textDf)
    mainTextDf = pd.concat(mainText).reset_index(drop=True)
    #logger.tprint(mainTextDf)

    #logger.vprint()

    #print("mainText")
    #logger.vprint(mainText)
    # extract subtasks
    #for line in mainTextDf[0]:
        #print(f"line = {line}")


    # this has been tested for XWB ONLY!! rmb to test for others
    if engineType == "XWB":
    # xwb has no subprocedure titles, use the first row
        subtaskMarker = dictionaries.subtaskIdentifierDict[engineType]
        matchIndex = [idx for idx, value in mainTextDf.iloc[:, 0].items()
                      if isinstance(value, str) and value.startswith(subtaskMarker)]
        #print(matchIndex)
        subtaskList = []
        i = 0
        for match in matchIndex:
            
            checkSubtask = [match - 1, match, match + 1]
            checkSubtaskText = mainTextDf.iloc[checkSubtask, 0].tolist()
            #print(checkSubtask[1], checkSubtaskText)

            # only accept if it is a 'real' subtask (ie not joined to an instruction)
            if (checkSubtaskText[0] == '') and (checkSubtaskText[2] == ''):
                # start and end of block
                startIdx = match + 1
                endIdx = matchIndex[i+1] if i + 1 < len(matchIndex) else len(mainTextDf)

                subtaskText = mainTextDf.iloc[startIdx:endIdx, 0].tolist()

                subtaskList.append([checkSubtaskText[1], '', subtaskText])  # xwb has no subtask title
            i += 1

        # match subtasks to task
        # remember to remove all non-unique values in dfHeader
        dfHeaderUnique = dfHeader.drop_duplicates().reset_index(drop=True)
        # convert to dict
        dfHeaderDict = dict(zip(dfHeaderUnique.iloc[:, 0], dfHeaderUnique.iloc[:, 1]))  # Task, Task Title

        
        taskList = dfHeaderUnique["Task"].tolist()
        #print("taskList")
        #print(taskList)

        # compare tasks and subtasks
        taskDict = {task: [] for task in taskList}  # init

        for task in taskList:
            # check along the subtasks
            # we just check all (not very efficient) to catch 
            taskNum = task[11:]
            #print(f"taskNum: {taskNum}")
            for subtask in subtaskList:
                subtaskNum = subtask[0][14:]
                #print(f"subtaskNum: {subtaskNum}")

                if taskNum in subtaskNum:
                    if subtask not in taskDict[task]:  # check if value isn't in the list already
                        taskDict[task].append(subtask)

    # this has issues with matching subtasks to tasks, will make alternate.
    # gonna complete the saving thing for xwb first.
    if (engineType == "1000") or (engineType == "7000") or (engineType == "900"):

        # identify tasks and subtasks
        taskDict = {}
        taskMarker = "TASK "
        subtaskMarker = dictionaries.subtaskIdentifierDict[engineType]
        matchTask = [idx for idx, value in mainTextDf.iloc[:, 0].items()
                     if (isinstance(value, str)
                         and value.lower().startswith(taskMarker.lower())
                         and '.' not in value
                         and ',' not in value
                         and 'OP ' not in value)]
        matchSubtask = [idx for idx, value in mainTextDf.iloc[:, 0].items()
                        if (isinstance(value, str)
                            and value.lower().startswith(subtaskMarker.lower())
                            and '.' not in value
                            and ',' not in value)]  # not part of an instruction

        for t in range(len(matchTask)):
            taskStart = matchTask[t]
            taskEnd = matchTask[t + 1] if t + 1 < len(matchTask) else len(mainTextDf)
            
            taskName = mainTextDf.iloc[taskStart, 0]
            #print(taskName)
            #taskDf = mainTextDf.iloc[taskStart+1:taskEnd]  # skip task title itself

            # Get subtasks that fall within this task
            taskSubtaskIndexes = [idx for idx in matchSubtask if taskStart < idx < taskEnd]

            subtaskList = []
            for i, match in enumerate(taskSubtaskIndexes):
                checkSubtask = [match - 1, match, match + 1]
                checkSubtaskText = mainTextDf.iloc[checkSubtask, 0].tolist()

                # find valid tasks
                if (checkSubtaskText[0] == ''):
                    startIdx = match + 1
                    endIdx = taskSubtaskIndexes[i + 1] if i + 1 < len(taskSubtaskIndexes) else taskEnd
                    subtaskText = mainTextDf.iloc[startIdx:endIdx, 0].tolist()

                    # something here must be changed so that subtask titles are recognised
                    # Extract the first non-blank line as the subtask title
                    subtaskTitleLines = []
                    for idx, line in enumerate(subtaskText):
                        if line.strip() != '':
                            # found the first non-blank line
                            start_idx = idx
                            end_idx = idx
                            # scan forward while lines are non-blank
                            for j in range(idx + 1, len(subtaskText)):
                                if subtaskText[j].strip() != '':
                                    end_idx = j
                                else:
                                    break
                            # slice out all consecutive non‑blank lines
                            subtaskTitleLines = subtaskText[start_idx : end_idx + 1]
                            # remove those lines from subtaskText
                            subtaskText = subtaskText[:start_idx] + subtaskText[end_idx + 1 :]
                            break

                    # join them into one title string (you could also keep as list)
                    subtaskTitle = ' '.join(subtaskTitleLines).strip()

                    # title must contain at least one alphabet (not a reference to a part)
                    if any(char.isalpha() for char in subtaskTitle):
                        subtaskList.append([checkSubtaskText[1], subtaskTitle, subtaskText])
                    

            taskDict[taskName[5:]] = subtaskList
        #print(taskDict)

        taskList = []
        for taskIdx in matchTask[:]:
            #print("task title?")
            #print(mainTextDf.iloc[taskIdx])

            # check that they are 'real tasks'
            checkTask = [taskIdx - 1, taskIdx, taskIdx + 1, taskIdx + 2, taskIdx + 3]
            #print(f" line 0: {mainTextDf.iloc[checkTask[0]]}")
            if mainTextDf.iloc[checkTask[0], 0] == '':


            # get full task title
                while ((mainTextDf.iloc[checkTask[-1], 0] != '')
                or mainTextDf.iloc[checkTask[2], 0].startswith("SB")
                or mainTextDf.iloc[checkTask[2], 0].startswith("RevDate")):
                    # the task name must be longer...
                    checkTask.append(checkTask[-1] + 1)
                    #logger.tprint(mainTextDf.iloc[checkTask])

                taskTitle = [mainTextDf.iloc[checkTask[1], 0][5:],
                             ' '.join(mainTextDf.iloc[checkTask[3:-1], 0].astype(str).tolist())]
                # this part needs updating for SB/RevDate tasks ^^^^
                #print(taskTitle)
                taskList.append(taskTitle)
                #taskIdxList.append(checkTask[1])  # index
                #print("iloc checkTask")
                #logger.tprint(mainTextDf.iloc[checkTask])
            #print(f"taskList: {taskList}")
            dfHeaderDict = {task[0]: task[1] for task in taskList}
            #print(f"updated dfHeaderDict: {dfHeaderDict}")

    # remember to remove the empty keys from all dicts
    dfHeaderDict = {k: v for k, v in dfHeaderDict.items() if k != ''}
    taskDict = {k: v for k, v in taskDict.items() if k != ''}

    #logger.vprint(taskDict)

    return dfHeaderDict, taskDict


def tasks(folder, files, output, origFolder, engineType, tables):
    allTasks = []
    # init for detecting engine type
    if engineType == None:
        engineList = []
    else:
        engineTypeSave = engineType  # for passing to file writing

    for file in files:
        fullText = fileHandler.loadPages(os.path.join(folder, file))

        # detect engine type
        if engineType == None:  # not specified
            logger.vprint("Detecting engine type")

            # extract key
            ident = list(dictionaries.identifierDict.keys())

            # find match
            engineIdent = None
            for key in ident:
                if key in fullText:
                    engineIdent = key
                    break

            # get engine type
            if engineIdent:
                engineType = dictionaries.identifierDict[engineIdent]
                #engineList.append(engineType)
                logger.vprint(f"Engine type detected: {engineType}")

                # apply splitting
                dfHeaderDict, taskDict = sectionSplit(fullText, engineType, tables)
                allTasks.append([dfHeaderDict, taskDict])
                engineTypeSave = engineType

                engineType = None  # reset
            else:
                #engineList.append("")
                logger.vprint("ERROR: Failed to identify engine type.")
    
        else:  # rmb to test this
            dfHeaderDict, taskDict = sectionSplit(fullText, engineType, tables)
            allTasks.append([dfHeaderDict, taskDict])
            engineTypeSave = engineType

    fileHandler.exportTasks(allTasks, output, origFolder, files, engineTypeSave)


def splitSteps(df, output, folder, merge):
    logger.vprint(df)
    logger.tprint(df)

    # get engine type
    typeCell = df.loc[0, 'origIdx']
    if isinstance(typeCell, str) and typeCell.startswith('TYPE: '):
        engineType = typeCell[6:]

    # split files into dictionary
    files = {}
    currIdx = None
    buffer = []

    for _, row in df.iloc[1:].iterrows():
        cell = row['origIdx']
        if isinstance(cell, str) and cell.startswith('FILE: '):
            # save previous buffer (if it exists)
            if currIdx is not None:
                files[currIdx] = pd.DataFrame(buffer)
            # start new group
            currIdx = cell
            buffer = []
        else:
            # only accumulate rows after we've seen a FILE:
            if currIdx is not None:
                buffer.append(row)

    # for last file
    if currIdx is not None:
        files[currIdx] = pd.DataFrame(buffer)

    print(f"files dict: {files}")
    print(len(files))

    ignoreEnd = dictionaries.taskEndText.get(engineType)
    #print(ignoreEnd)
    stepsDict = {}
    linePattern = r"[-–—‒―−]"  # for ignoring lines with only dashes

    for file, fileDf in files.items():
        print("file::")
        print(file)
        logger.tprint(fileDf)

        # create output dataframe
        columns = ['origIdx', 'Task', 'Task Title', 'Subtask', 'Subtask Title', 'Step(s)']
        rows = []

        # split into steps
        #for stepsList in fileDf['Steps']:
        fileDf = fileDf.reset_index(drop=True)
        for i, stepsList in enumerate(fileDf['Steps']):
            #assign other columns
            origIdx = fileDf.loc[i, 'origIdx']
            task = fileDf.loc[i, 'Task']
            taskTitle = fileDf.loc[i, 'Task Title']
            subtask = fileDf.loc[i, 'Subtask']
            subtaskTitle = fileDf.loc[i, 'Subtask Title']

            steps = stepsList.split(" | ")
            print(f"steps: {steps}")

            for i, line in enumerate(steps):
                # drop 'end' text
                if (ignoreEnd != '') and (ignoreEnd in line):
                    steps = steps[:i]
                    break

            cleanSteps = []
            buffer = []

            # >> there are issues here with 1000C losing steps! <<

            # cld put this earlier but its probably just an efficiency thing
            for i, line in enumerate(steps):
                line = line.strip()
                
                # if line is blank, save buffer
                if line == '':
                    if buffer:
                        # different joiner for text/number
                        #print(buffer)
                        #stepStr = ''
                        # have to check each first and last character
                        if len(buffer) == 1:
                            stepStr = buffer[0]
                            cleanSteps.append(stepStr)

                        elif len(buffer) > 1:
                            stepStr = buffer[0]
                            j = 0
                            while j < (len(buffer) - 1):  # so we dont get an index error
                                if buffer[j][-1].isalnum() or buffer[j+1][0].isalnum():
                                    stepStr += ' ' + buffer[j+1]
                                else:
                                    stepStr += buffer[j+1]
                                j += 1
                            cleanSteps.append(stepStr)

                        else:  # anything else
                            cleanSteps.append(' '.join(buffer))

                        print(f"stepStr = {stepStr}")
                        #cleanSteps.append(' '.join(buffer))
                        buffer = []
                    i += 1
                    
                    #print(f"buffer = {buffer}")

                # if line is not blank, add to buffer
                else:
                    unDash = re.sub(linePattern, "", line)

                    if unDash == "":
                        # ignore lines which only have '-'
                        # there's some issue with types of dashes, will come back later
                        pass
                    else:
                        buffer.append(line)

                #print(f"buffer = {buffer}")

                # resplit by sentence
                cleanStepsTemp = []
                for chunk in cleanSteps:
                    #print(f"chunk: {chunk}")

                    if any(re.match(pattern, chunk) for pattern in dictionaries.stepIgnoreText.get(engineType, [])):
                        continue

                    sentences = re.findall(r'[^.]+(?:\.|\n|$)', chunk)
                    temp = []

                    for s in sentences:
                        s = s.strip()
                        alphaCount = sum(c.isalpha() for c in s)

                        if ((alphaCount < 4) or (s and s[0].islower())) and temp:
                            temp[-1] += ' ' + s
                        else:
                            temp.append(s)

                    cleanStepsTemp.extend(temp)
                    #cleanStepsTemp.extend([s.strip() for s in sentences])
                # save to cleanSteps
                cleanSteps = cleanStepsTemp

            # retrieve other column info and save to stepsDict
            #print(f"row, other columns: {origIdx}, {task}, {taskTitle}, {subtask}, {subtaskTitle}")
            
            for step in cleanSteps:
                rows.append([origIdx, task, taskTitle, subtask, subtaskTitle, step])
        stepsDf = pd.DataFrame(rows, columns=columns)

        logger.tprint(stepsDf)
        #rows.append([origIdx, task, taskTitle, subtask, subtaskTitle, ])

        # save to stepsDict
        stepsDict[file] = stepsDf
        
    #print(f"stepsDict: {stepsDict}")
    fileHandler.exportSteps(stepsDict, output, folder, merge)














