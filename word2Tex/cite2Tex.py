import re
import os
import sys
import pandas as pd
import bibtexparser as btp
import argparse


PATTERN = "(?:(?P<name1>[^0-9\s\(\),]+)|(?P<name2>[^0-9\s\(\)]+)(?:\set\sal[.]*)|(?P<name3>[^0-9\s\(\)]+)(?:\s&\s[^\s\(\)]+))\s(?P<year>\d{4})"

def find_matches(text, pattern=PATTERN, bib=None):
    """Finds citations in text (e.g. Varela et al 2014, Sigurdsson & Duvarci
    2015, Vertes 2006, Venables et al. 2008) and converts them to LaTeX
    citation (e.g. \cite{Varela2014}). If a bibtex .bib file is provided or a
    btp.bibdatabase then it will attempt to lookup the citation in the
    bibliography and use the correct citation ID. If a bib is provided and a
    citation is not found in it then it will marked as missing from the
    bibliography. This returns a pandas dataframe detailing the found
    citations, the new citation text as well as the start and end locations in
    the text and, if bib is provided, whether or not the citation appears in
    the bib. Prompts user if multiple possible citation matches in bibliography.
    :param text: text to look for citations in
    :type text: str
    :param pattern: regex pattern to search for citations. Default pattern can
        detect citations of the style in the description.
    :type pattern: str
    :param bib: bibtex bib file or btp.bibdatabase object
    :type bib: str or btp.bibdatabase
    :return: DataFrame with columns: original, cite_key, tex (the new citation text), start, end, in_bib
    :rtype: pd.DataFrame
    """
    if bib and isinstance(bib, str) and os.path.isfile(bib):
        with open(bib) as f:
            tmp = btp.load(f)
        bib = tmp

    if bib:
        bib_keys = bib.entries_dict.keys()
    else:
        bib_keys = None

    out = []
    for match in re.finditer(pattern, text):
        si = match.start()
        ei = match.end()
        orig = text[si:ei]
        if bib:
            new = citation_lookup(orig, bib)
            if len(new) == 1:
                new = new[0]
            elif len(new) > 1:
                choice = ''
                while not choice.isnumeric():
                    print(f'Multiple matches found for citation {orig}\n Please '
                          'select from the list below:')
                    for i, j in enumerate(new):
                        print(f'{i}) {j}')

                    choice = input('Select One >> ')

                new = new[int(choice)]
            else:
                new = ''.join([x for x in match.groups() if x])

        else:
            new = ''.join([x for x in match.groups() if x])

        tmp = {'original': orig, 'cite_key': new, 'tex': f'\cite{{{new}}}', 'start':si, 'end':ei}
        if bib_keys:
            if new in bib_keys:
                tmp['in_bib'] = True
            else:
                tmp['in_bib'] = False

        out.append(tmp)

    return pd.DataFrame(out)


def parse_authors(auth_str):
    """returns list of all author last names from a string with `last_name,
    first_initial and last_name, first_inital and etc`
    :param auth_str: string containing all author names as exported by
        EndNoteX9 default BibTex export
    :type auth_str: str
    :return: list of author last names
    :rtype: list of str
    """
    a_list = auth_str.split(' and ')
    out = [decode_Tex_accents(x.split(' ')[-1]) for x in a_list]
    return out

def decode_Tex_accents(in_str):
    """Converts a string containing LaTex accents (i.e. "{\\`{O}}") to ASCII
    (i.e. "O"). Useful for correcting author names when bib entries were
    queried from web via doi

    :param in_str: input str to decode
    :type in_str: str
    :return: corrected string
    :rtype: str
    """
    # replaces latex accents with ascii letter (no accent)
    pat = "\{\\\\'\{(\w)\}\}"
    out = in_str
    for x in re.finditer(pat, in_str):
        out = out.replace(x.group(), x.groups()[0])

    # replace latex {\textsinglequote} with underscore
    out = out.replace('{\\textquotesingle}', "_")

    # replace actual single quotes with underscore for bibtex compatibility
    out = out.replace("'", '_')

    return out


def citation_lookup(citation, bib):
    """Looks up an in-text citation in the bibliography file/database and
    returns all possible citation IDs that match the year and authors in the
    citation.
    :param citation: citation to look up (e.g. Ito et al 2015)
    :type citation: str
    :param bib: bibtex bibliography file or database
    :type bib: str or btp.bibdatabase
    :return: list of citation keys
    :type: list of str
    """
    citation = citation.replace('\n', ' ')
    if isinstance(bib, str) and os.path.isfile(bib):
        with open(bib) as f:
            tmp = btp.load(f)
        bib = tmp

    year = re.match('(?:.*)(?P<year>\d{4})', citation)['year']
    if '&' in citation:
        authors = list(re.match('(\S*)(?:\s&\s)(\S*)', citation).groups())
        num_auth = 2
    elif 'et al' in citation:
        authors = [citation.split(' ')[0]]
        num_auth = 3
    else:
        authors = [citation.split(' ')[0]]
        num_auth = 1

    authors = [decode_Tex_accents(x) for x in authors]
    matches = []
    for entry in bib.entries:
        if year != entry['year']:
            continue

        bib_auths = parse_authors(entry['author'])
        if num_auth == 3 and len(bib_auths) < 3:
            continue
        elif num_auth < 3 and len(bib_auths) != num_auth:
            continue

        if all([x in bib_auths for x in authors]):
            matches.append(entry['ID'])

    return matches


def citations2Tex(fn, bib=None, save_file=None):
    """Finds all citations in a text document and converts them to LaTex
    citations (e.g.Viena et al 2018 --> Viena2018). If bib is provided then the
    citations will be looked up in the bibtex file and the proper citation key
    will be used, and if the citation cannot be matched to a bibliography entry
    then you will be notified and the citation will be left unchanged.
    :param fn: file to convert
    :type fn: str
    :param bib: bibtex bibliography file or database
    :type bib: str or btp.bibdatabase
    :param save_file: file to save edited text to, default appends '-fixed' to
        the input filename
    :type save_file: str
    """
    with open(fn) as f:
        text = f.read()

    matches = find_matches(text, bib=bib)
    if matches.empty:
        print('No citations found to edit. Done!')
        return

    new_text = text
    no_change = []
    if 'in_bib' in matches.columns:
        matches = matches[['original', 'cite_key', 'tex', 'in_bib']]
    else:
        matches = matches[['original', 'cite_key', 'tex']]

    matches = matches.drop_duplicates()
    fixed_n = 0
    same_n = 0

    for i, row in matches.iterrows():
        if 'in_bib' in row and not row['in_bib']:
            print(row['cite_key'] + ' not found bib. Skipping citation ' + row['original'])
            no_change.append(row)
            same_n += 1
            continue

        new_text = new_text.replace(row['original'], row['tex'])
        fixed_n += 1

    if save_file is None:
        name, ext = os.path.splitext(fn)
        save_file = name + '-fixed' + ext

    with open(save_file, 'w') as f:
        print(new_text, file=f)

    print('Done. %i citations fixed. %i citations unchanged' % (fixed_n, same_n))


def main():
    parser = argparse.ArgumentParser(prog='cite2Tex',
                                     description='Converts citations from '
                                     'Author Year, Author et al Year, Author '
                                     '& Author2 Year to LaTeX citations2Tex')
    parser.add_argument('file', help='text file to fix')
    parser.add_argument('-b', '--bib', help='bibtex file (optional)')
    parser.add_argument('-o', '--output', help='output file (optional)')
    args = parser.parse_args()

    citations2Tex(args.file, bib=args.bib, save_file=args.output)


if __name__ == '__main__':
    main()

