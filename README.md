# extract-from-em

## Setting Up the Environment

To set up the Conda environment, run:

```sh
conda env create -f environment.yml
conda activate myenv
```

## Setting Up Folders

Place all EM files downloaded in a folder. See the arrangement of `example-files-xxxx` for example. Use the name of this folder to access all the files inside.

## Run Example

After setting up the environment, try example command:

```sh
python main.py example-files-1000C -rt
```

## Info About Arguments

- `folder`: Specify input folder name.
- `-o, --output`: Specify output file/folder name. Default: `output`

### Printing
- `-q, --quiet`: Disable verbose output
- `--tables`: Shows dataframes generated. Usually for debugging.

### rawText and related mode(s)
- `-rt, --rawText`: rawText mode. Just coverts the `.pdf` file to `.txt`. Has 1 separate optional sub-mode, `-c` (see below).
- `-c, --combine`: Combined mode. If combined mode is ON, only 1 output file will be written. If combined mode is OFF, a folder will be created and outputs for each input file will be written in the new folder. Default: OFF.

### tasks and related mode(s)
- `-t, --tasks`: Tasks mode. Extracts task, task number, subtask, subtask number, and body text. Has 1 separate optional sub-mode, `-f` (see below).
-  `-e, --engineType`: Specify engine type (optional): ['1000', '7000', '900', 'XWB']. If it is not specified, the type will be detected automatically. Use this only when the layout of the pdf has been changed.

### File Handling Modes
- `-st, --splitThreshold`: Specify the threshold for number of pages in a file which will consider the file large. If the file is large, a temporary folder will be created to split all large files into smaller chunks for extraction to reduce data loss in case the program crashes. The temporary folder will be deleted if the program completes properly. Default: 200.
- `-keep, --keepTemp`: Keep temporary files generated during the script. Use this if the program keeps crashing.

Note: Arguments like `-rt, --rawText` and `-t, --tasks` can be called at the same time, but the files will be read again for each argument.