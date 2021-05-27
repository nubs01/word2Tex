import os
import requests
import argparse
import bibtexparser as btp
from word2Tex.fixBibTex import resolve_ID_matches
from word2Tex.cite2Tex import decode_Tex_accents, parse_authors

def doi_lookup(doi):
    """queries for article data based on given doi

    :param doi: DOI to lookup
    :type doi: str
    :return: reference information
    :rtype: dict
    """
    url = "https://dx.doi.org/" + doi
    headers = {"accept": "application/x-bibtex"}
    r = requests.get(url, headers = headers)
    bp = btp.bparser.BibTexParser(interpolate_strings=False)
    db = bp.parse(r.text)
    if len(db.entries) == 0:
        print(f'No reference found for DOI: {doi}')
        return
    else:
        print(f'Found reference for DOI: {doi}')
        print(r.text)
        return db.entries[0]


def fix_queried_ref(ref):
    """Fixes the ID for references to deal with author names with accents.
    Leaves author names intact in author field.
    :param ref: reference to fix, output from doi_lookup
    :type ref: dict
    :return: fixed reference
    :rtype: dict
    """
    authors = parse_authors(ref['author'])
    ref['ID'] = '%s_%s' % (authors[0], ref['year'])
    return ref


def add_to_bibtex(bib_fn, doi):
    """Lookup a doi and add the reference to a bibtex file
    :param bib_fn: path to bibtex file
    :type bib_fn: str
    :param doi: doi reference
    :type doi: str
    """
    ref = doi_lookup(doi)
    if ref is None:
        print('No reference added to bibtex database')
        return

    if os.path.isfile(bib_fn):
        with open(bib_fn) as f:
            db = btp.load(f)
    else:
        db = btp.bibdatabase.BibDatabase()

    db.entries.append(ref)
    db = resolve_ID_matches(db)
    with open(bib_fn, 'w') as f:
        btp.dump(db, f)

    ID = ref['ID']
    print(f'Added new reference ({ID}) to bibtex db')

def main():
    parser = argparse.ArgumentParser(prog='doi2bib',
                                     description='Adds new reference to '
                                     'bibtex library using the doi.')
    parser.add_argument('file', help='.txt or .bib file to add to')
    parser.add_argument('doi', help='DOI of reference to add')
    args = parser.parse_args()
    add_to_bibtex(args.file, args.doi)

if __name__ == "__main__":
    main()
