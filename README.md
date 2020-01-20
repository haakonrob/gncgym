# gncgym

## Installation

To install gncgym and all of its dependencies, clone the repository and navigate to the folder, 
and then use pip install.
```bash
git clone https://github.com/haakonrob/gncgym
cd gncgym
pip install -e .
```

This installs gncgym as an "editable" library using links. If you don't need to 
edit the files, and just want to use the library, just use the following instead
of the last line. 

```bash
pip install .
```

This will also create a startup script that allows you to the 
library from the command line.


## Usage

After installation, type the following in a terminal to start an example 
scenario where you can control the vessel using the arrow keys.

```bash
gncgym play
```