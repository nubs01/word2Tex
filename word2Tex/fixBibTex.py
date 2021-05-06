import argparse
from collections import Counter
import bibtexparser as btp
from copy import deepcopy
import os
import sys


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
    out = []
    for x in a_list:
        out.append(x.split(',')[0])

    return out


def fix_entry_id(entry, inplace=False):
    """repalces the BibTex database entry ID with [First Author Last Name][Year]
    :param entry: Bibtex Database Entry
    :type entry: dict
    :param inplace: whether to edit the entry in place or to make a copy and
        return the editted version
    :type inplace: bool
    :return: correct entry
    :rtype: dict
    """
    if inplace:
        out = entry
    else:
        out = entry.copy()

    authors = parse_authors(entry['author'])
    out['ID'] = authors[0] + entry['year']

    if inplace:
        return

    return out


def resolve_ID_matches(db, index='journal'):
    """Goes through Bibtex Database and fixes any entries with matching IDs by
    appending the journal initials or digits, if journal initials aren't unique

    :param db: parsed Bibtex Database
    :type db: btp.bibdatabase
    :param index: {'journal', 'digit'}, specifies whether to resolve matches
        with journal initialsi or digits
    :type index: str
    :return: fixed database
    :rtype: btp.bibdatabase
    """
    assert index in ['journal', 'digit'], ('unsupported indexing type. '
                                           'Must be "journal" or "digit"')
    IDs = [x['ID'] for x in db.entries]
    counts = Counter(IDs)
    if all([y==1 for y in counts.values()]):
        return db

    out = deepcopy(db)
    tofix = []
    for k, v in counts.items():
        if v > 1:
            tofix.append(k)

    indices = {}
    for x in out.entries:
        if x['ID'] in tofix:
            if index == 'journal':
                ji = ''.join([y[0] for y in x['journal'].split(' ')])
                new_id = '%s-%s' % (x['ID'], ji)
            elif index == 'digit':
                ld = indices[x['ID']]
                dig = ld + 1 if ld else 0
                indices[x['ID']] = dig
                new_id = '%s-%i' % (x['ID'], dig)

            x['ID'] = new_id

    IDs = [x['ID'] for x in out.entries]
    counts = Counter(IDs)
    if all([y==1 for y in counts.values()]):
        return out
    else:
        return resolve_ID_matches(out, index='digit')


def fix_bibtexDB(fn, save_file=None):
    """fixes all citation IDs
    :param fn: file to fix
    :type fn: str
    :param save_file: output file (optional), default appends '-fixed' to filename
    :type save_file: str
    """
    with open(fn) as f:
        db = btp.load(f)

    for x in db.entries:
        fix_entry_id(x, inplace=True)

    db = resolve_ID_matches(db)
    name, ext = os.path.splitext(fn)
    if not save_file:
        save_file = name + '-fixed' + ext

    with open(save_file, 'w') as f:
        btp.dump(db, f)


def main():
    parser = argparse.ArgumentParser(prog='fixBibTex',
                                     description='Fixes IDs in bibtex file '
                                     'to be AuthorYear for easy citation '
                                     'in LaTeX.')
    parser.add_argument('file', help='.txt or .bib file to fix')
    parser.add_argument('-o', '--output', help='output file (optional)')
    args = parser.parse_args()

    fix_bibtexDB(args.file, save_file=args.output)


if __name__ == "__main__":
    main()

