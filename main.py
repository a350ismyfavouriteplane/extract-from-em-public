import re
import os
import sys
import shutil
import openpyxl
import time
import argparse
import logging
import pandas as pd
from pdfminer.high_level import extract_text
from pypdf import PdfReader
from pathlib import Path

# remember to redo the yml when this is done

import logger
import fileHandler
import extract

# Disable all existing loggers except __main__
# (idk why pypdf can't be suppressed properly)
for name in logging.root.manager.loggerDict:
    if not name.startswith("__main__"):
        logging.getLogger(name).setLevel(logging.CRITICAL + 1)

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('folder',
                        action='store',
                        type=str,
                        help='Folder with downloaded files')
    parser.add_argument('-o', '--output',
                        type=str,
                        default='output',
                        help='Output file name (default: "output")')
    
    # rawtext and related modes
    parser.add_argument('-rt', '--rawText',
                        action='store_true',
                        help='Save raw text')
    parser.add_argument('-c', '--combine',
                        action='store_true',
                        help='Combine outputs into a single file')

    # tasks and related modes
    parser.add_argument('-t', '--tasks',
                        action='store_true',
                        help='Extract tasks and subtasks')
    parser.add_argument('-e', '--engineType',
                        choices=['1000', '7000', '900', 'XWB'],
                        help='Specify engine type (optional). If not specified, will guess')
    parser.add_argument('-s', '--steps',
                        action='store_true',
                        help='Create separate cells for each step')

    # file handling modes
    parser.add_argument('-st', '--splitThreshold',
                        type=int,
                        default=200,
                        help='Set page number threshold for large files to be split (default: 200)')
    parser.add_argument('-keep', '--keepTemp',
                        action='store_true',
                        help='Keep temporary files')

    # print variants
    parser.add_argument('-q', '--quiet',
                        action='store_false',
                        dest='verbose',
                        help='Disable verbose output')
    parser.add_argument('--tables',
                        action='store_true',
                        dest='tables',
                        help='Show nice tables')

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    # setup verbose mode
    logger.setup(args.verbose, args.tables)
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s"
    )
    
    logger.vprint(f"Getting folder: {args.folder}")
    logger.vprint(f"Output files will start with: '{args.output}_'")

    files = fileHandler.getFileList(args.folder)
    #for file in files:  # debug
        #logger.vprint(f"FILE: {repr(file)} | length={len(file)}")

    if files:
        logger.vprint("Files in the folder:")
        for file in files:
            logger.vprint(file)
    else:  # folder is empty :(
        logging.error("ERROR: No files found or invalid folder.")
        sys.exit(1)  # to tell other scripts that ERROR occurred

    filenameThreshold = 100  # default
    longNames = fileHandler.detectLongNames(files, filenameThreshold)

    if longNames:
        tempFolder_LN = "temp_LN"
        logger.vprint("Names may get too long, shortening names")
        logger.vprint(f"Temp folder will be created: {tempFolder_LN}")

        fileHandler.shortenNames(args.folder, tempFolder_LN, filenameThreshold)
        #files = fileHandler.getFileList(tempFolder_LN)

        # specify folder to extract from
        extractFolder = tempFolder_LN
        files = fileHandler.getFileList(extractFolder)  # retrieve all files again
        logger.vprint(f"Working folder: {extractFolder}")

    else:  # no long names
        logger.vprint(f"No potential issues with name length, extracting from folder: {args.folder}")
        extractFolder = args.folder
        logger.vprint(f"Working folder: {extractFolder}")

    largeFiles = fileHandler.detectLargeFiles(extractFolder, files, args.splitThreshold)

    if largeFiles:
        tempFolder_LF = "temp_LF"
        logger.vprint(f"Large files detected: {largeFiles}")
        logger.vprint(f"Temp folder will be created: {tempFolder_LF}")

        fileHandler.largeFileSplitter(extractFolder, tempFolder_LF, largeFiles, args.splitThreshold)
        # change this when done       ^^^^^^^^^^^

        # specify folder to extract from
        extractFolder = tempFolder_LF
        files = fileHandler.getFileList(extractFolder)  # retrieve all files again
        logger.vprint(f"Working folder: {extractFolder}")

    else:
        if longNames:
            extractFolder = tempFolder_LN
        else:
            extractFolder = args.folder

        logger.vprint(f"No potential issues with number of pages, extracting from folder: {extractFolder}")
        #extractFolder = args.folder
        logger.vprint(f"Working folder: {extractFolder}")

    if args.rawText:
        extract.rawText(extractFolder, files, args.combine, args.output, args.folder)

    if args.tasks:
        #print(args.engineType)
        extract.tasks(extractFolder, files, args.output, args.folder, args.engineType, args.tables)

        if args.steps:
            filename = f"{args.output}_tasks_{args.folder}.csv"
            if filename in os.listdir():
                df = pd.read_csv(filename)  # not sure why reading it gives 2 columns but it helps
                #logger.tprint(df)
                extract.splitSteps(df)


            else:
                print("Task file cannot be found")


    if not args.keepTemp:  # delete temp files generated
        for item in Path('.').iterdir():
            if item.is_dir() and item.name.startswith('temp'):
                logger.vprint(f'Deleting: {item}')
                shutil.rmtree(item)

    logger.vprint("Script finished successfully")
    sys.exit(0)
