# word2Tex: Citation handling and fixing application
The modules included in this package are cite2Tex and fixBibTex which help with
citations when migrating a manuscript into LaTeX.

## Installation
```bash
pip install word2Tex
```

## cite2Tex
This module can be used as a command-line tool or in python. It goes through a
text file and converts citations into LaTeX format (e.g. Viena et al. 2018 -->
\cite{Viena2018}). If a bibtex bibliography file is provided then citations
will be looked up by author and year and the correct citation key will be used.
Additionally, if a bib is provided, citations not found in the bib will be left
alone and you will be notified which citations are missing from the bib.

### Usage
To use in the command line:
```bash
cite2Tex path_to_file.txt -b path_to_bib.bib -o path_to_output_file.txt
```
the `-b` and `-o` flags are optional. 

To use in python:
```python
from word2Tex import cite2Tex as c2t
fn = 'path_to_file.txt'
bib_fn = 'path_to_bib.bib' # optional
save_file = 'path_to_save_edited_text.txt' # optional, regardless will always write to a new file

# This will allow you to view all citations in the document and see what they will become
with open(fn) as f:
    matches = c2t.find_matches(f.read(), bib=bib_fn)
#This creates the dataframe matches which you cna view and check

# To convert a file
w2t.citations2Tex(fn, bib=bib, save_file=save_file)
```

## fixBibTex
This module allows correction of citation ID in bibtex files when exported from applications such as EndNote. Citation IDs will be set to AuthorYear using the first authors last name. If there are duplicates with this method then the article's journal initials will be tacked onto the end or an index number to ensure unique IDs.

### Usage
To use from command-line:
```bash
fixBibTex path_to_bib_file.bib -o output_file.bib
```
The output file is optional. Regardless this will always save to a new file to avoid dataloss.

In python:
```python
from word2Tex import fixBibTex as fbt
fn = 'path_to_bib_file.bib'
out_fn = 'out_file_path.bib' # optional
fbt.fix_bibtexDB(fn, save_file=out_fn)
```
