# backupFiles
Takes a list of files and directoried to backup and copy them with folder structure in destination folder

## usage
```
usage: backupFiles.py [-h] [-v] [-l LOG_FILE] input_file dest_folder

positional arguments:
  input_file            Input file containing folders/files to backup
  dest_folder           Destination folder where to save the backup files

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -l LOG_FILE, --log_file LOG_FILE
                        Log file to store processed and ignored files lists
```
### input file example
The input file must contains absolute path to files and directories to backup. One file/directory per line. Here is an example file:
```
/home/yann/.vimrc
/home/yann/.bash_aliases
/home/yann/.gitconfig
```
