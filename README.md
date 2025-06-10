# extract-from-em

## Setting Up the Environment

To set up the Conda environment, run:

```sh
conda env create -f environment.yml
conda activate myenv
```

## Setting Up Folders

Place all EM files downloaded in a folder, even if there is only one file to be extracted. Use the name of this folder to access all the files inside.

## Useful examples

After setting up environment, try:

### Common uses
1. For raw text `.txt` file:
   - `python main.py <folder name> -rt`
   - `python main.py <folder name> --rawText`
2. For tasks and subtasks in `.csv` file:
   - `python main.py <folder name> -t`
   - `python main.py <folder name> --tasks`
3. For tasks and subtasks with associated steps in `.xlsx` file:
   - `python main.py <folder name> -t -s`
   - `python main.py <folder name> --tasks --steps`

### Less common variants:
4. For the whole folder to be extracted into one single raw text `.txt` file:
   - `python main.py <folder name> -rt -c`
   - `python main.py <folder name> --rawText --combine`
5. For tasks and subtasks with associated steps, but with task / task title and subtask / subtask title merged for readability (bad for copy-pasting):
   - `python main.py <folder name> -t -s -m`
   - `python main.py <folder name> --tasks --steps --merge`

### For debugging:
6. For intermediate dataframes to be printed (e.g. while extracting tasks and steps):
   - `python main.py <folder name> -t -s --tables`
   - `python main.py <folder name> --tasks --steps --tables`
7. For retaining intermediate temporary files generated when large files are split or files are renamed:
   - `python main.py <folder name> -rt -keep`
   - `python main.py <folder name> -rawText --keepTemp`

This has also been tested on non-EM files such as CIR.

## Info About Arguments

- `folder`: Specify input folder name.
- `-o, --output`: Specify output file/folder name. Default: `output`

### Printing
- `-q, --quiet`: Disable verbose output
- `--tables`: Shows dataframes generated. Usually for debugging.

### rawText and related mode(s)
- `-rt, --rawText`: rawText mode. Just coverts the `.pdf` file to `.txt`.
- `-c, --combine`: Combined mode. If combined mode is ON, only 1 output file will be written. If combined mode is OFF, a folder will be created and outputs for each input file will be written in the new folder. Default: OFF.

### tasks and related mode(s)
- `-t, --tasks`: Tasks mode. Extracts task, task number, subtask, subtask number, and body text.
- `-s, --steps`: Steps mode. Prints each step in a subtask on a different line. Must be used after `-t, --tasks`.
- `-m, --merge`: Merges cells unedr the same task / task title / subtask / subtask title. Default: OFF.
-  `-e, --engineType`: Specify engine type (optional): ['1000', '7000', '900', 'XWB']. If it is not specified, the type will be detected automatically. Use this only when the layout of the pdf has been changed, but most of the time this is not necessary to be specified at all.

### File Handling Modes
- `-st, --splitThreshold`: Specify the threshold for number of pages in a file which will consider the file large. If the file is large, a temporary folder will be created to split all large files into smaller chunks for extraction to reduce data loss in case the program crashes. The temporary folder will be deleted if the program completes properly. Default: 200.
- `-keep, --keepTemp`: Keep temporary files generated during the script. Use this if the program keeps crashing.

Note: `-rt, --rawText` and `-t, --tasks` can be called at the same time, but the files will be read again for each argument.

Note: `-s, --steps` will read the file created from tasks as an intermediate step. Modifying the file will affect if the file can be read or may have errors.
