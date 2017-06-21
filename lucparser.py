# _*_ coding: utf-8 _*_

'''This module parses a Lucene query string into a list of tokens,
where each "term" is represented by a dictionary of the form

_{'field': fieldname, 'term': termvalue}

If a search term is general (doesn't relate to a specific field, fieldname=None.

The module provides a class `LucParser` with two functions:

LucParser.deparse(querystring):

Takes the querystring an returns a list of tokens, where "terms" are
replaced with dictionaries {'field': fieldname, 'term': termvalue}.

LucParser.assemble(termlist):

Takes a list of the form returned by deparse. Returns a querystring.

The implementation of this module is informed by the
lucene query-parser documentation:
https://lucene.apache.org/core/6_6_0/queryparser/org/apache/lucene/
queryparser/classic/package-summary.html#package.description

Example:
from lucparser import LucParser
lp = LucParser()

qlist = lp.deparse('author: Meier tags:(water OR fire) "open access"')
print(qlist)

> [{'field': 'author', 'term': 'Meier'},
>  {'field': 'tags', 'term': '( water OR fire )'},
>  {'field': None, 'term': '"open access"'}]


qlist[0]['term'] = '{}{} OR Mueller -Donald{}'.format('(', qlist[0]['term'], ')')
print(qlist)

> [{'field': 'author', 'term': '(Meier OR Mueller -Donald)'},
>  {'field': 'tags', 'term': '( water OR fire )'},
>  {'field': None, 'term': '"open access"'}]

lp.assemble(qlist)

> 'author : (Meier OR Mueller -Donald) tags : ( water OR fire ) "open access"'


'''

import re

__version__ = '1.0.0'

class LucParser(object):
    def __init__(self):
        self.replacepairs = {
            'metaesc': ('\\\\\\\\', '_&_METAESC_&_'),
            'quot': ('\\\\"', '_&_QUOT_&_'),
            'space': ('\s', '_&_SPACE_&_'),
            'colon': (':', '_&_COLON_&_'),
            'pa': ('\\(', '_&_PA_&_'),
            'rens': ('\\)', '_&_RENS_&_'),
        }

        self.revpairs = {
            'metaesc': ('_&_METAESC_&_', '\\\\'),
            'quot': ('_&_QUOT_&_','\\"'),
            'space': ('_&_SPACE_&_', ' '),
            'colon': ('_&_COLON_&_', ':'),
            'pa': ('_&_PA_&_', '('),
            'rens': ('_&_RENS_&_',')'),
        }
 
    def _replace_metaescape(self, qstring):
        "replaces escaped escapechar"
        fro, to = self.replacepairs['metaesc']
        qstring = re.sub(fro, to, qstring)
        return qstring

    def _replace_esc_quotes(self, qstring):
        "Replaces escaped quotation marks"
        fro, to = self.replacepairs['quot']
        qstring = re.sub(fro, to, qstring)
        return qstring

    def _replace_in_range(self, qstring, rangepats, repair):
        '''Replaces according to replacepair in certain intervals
        of qstring, which are characterized by a list of patterns (rangepats).

        '''
        for pat in rangepats:
            matches = re.findall(pat, qstring)
            replacements = [re.sub(repair[0], repair[1], s) for s in matches]
            for m, rep in zip(matches, replacements):
                qstring = qstring.replace(m, rep)
        return qstring

    def _repspaces_in_ranges(self, qstring):
        '''Replace spaces inside range terms and inside quotes.
        Replace colons in range terms and inside quotes.
        Replace parenthesies in range terms and inside quotes.

        '''
        rangeex =  re.compile('(?<!\\\\)\{.*?(?<!\\\\)\}')
        rangeinc = re.compile('(?<!\\\\)\[.*?(?<!\\\\)\]')
        regex =    re.compile('(?<!\\\\)\/.*?(?<!\\\\)\/')
        quoted =   re.compile('".*?"')
        ranges = [rangeex, rangeinc, regex, quoted]
        re_pairs = [self.replacepairs['space'], self.replacepairs['colon'],
                    self.replacepairs['pa'], self.replacepairs['rens']]
        for repair in re_pairs:
            qstring = self._replace_in_range(qstring, ranges, repair)

        return qstring

    def _addparenswhitespace(self, qstring):
        reparens = {'(': ' ( ', ')': ' ) '}
        'Add space around "(" and ")" for separation from terms'
        qstring = re.sub('[\\(\\)]', lambda x: reparens[x.group()], qstring)
        return qstring

    def _stripspaces(self, qstring):
        'Removes spaces surrounding ":".'
        return re.sub(r'\s*(?<!\\\\):\s*', ':', qstring)

    def _repspaces_in_subqueries(self, qstring):
        '''Replace all spaces in field specific subqueries. That is is
        necessary so that the associaten with the subquery can be maintained.
        For example 'field:(+term1 -term2)'.
        Replace also all colons in field specific subqueries, necessary to prevent
        incorrect splitting.

        '''
        re_pairs = [self.replacepairs['space'], ('(?<!^):', '_&_COLON_&_')]
        rangepats = [':\\(.*?(?<!\\\\)\\)']
        for repair in re_pairs:
            qstring = self._replace_in_range(qstring, rangepats, repair)
        return qstring

    def _termdicts(self, qsplitted):
        '''Replaces term-token in splitted query by dictionaries of the form
        {'field': fieldname, 'term': term}. In the case of global terms,
        fieldname is None.

        '''
        nonterms = 'AND|OR|NOT|!|&&|\\|\\||\\(|\\)'
        termidx = [i for i, t in enumerate(qsplitted) if not re.match(nonterms, t)]
        terms = [qsplitted[i] for i in termidx]
        for i, t in zip(termidx, terms):
            parts = re.split('(?<!\\\\):', t)
            if len(parts) == 1:
                qsplitted[i] = {'field': None, 'term': parts[0]}
            else:
                qsplitted[i] = {'field': parts[0], 'term': parts[1]}
        return qsplitted

    def _parse(self, qstring):
        qstring = self._replace_metaescape(qstring) # replace \\
        qstring =self. _replace_esc_quotes(qstring) # replace \"
        qstring = self._repspaces_in_ranges(qstring)# replace \s and : in ranges and quotes
        qstring = self._addparenswhitespace(qstring) # add whitespace aound parenthesies
        qstring = self._stripspaces(qstring) # remove whitespace around :
        qstring = self._repspaces_in_subqueries(qstring) # make subqueries one item
        return self._termdicts(qstring.split())

    def _unreplace(self, termdicts):
        '''Reverses all replacements'''
        for termdict in termdicts:
            if not isinstance(termdict, dict):
                continue
            for key in termdict.keys():
                if termdict.get(key):
                    for fro, to in self.revpairs.values():
                        termdict[key] = re.sub(fro, to, termdict[key])
        return termdicts

    def deparse(self, qstring):
        '''Returns the final list of query-tokens, where terms ore replaced with
        dictionaries {'field': fieldname|None, 'term': 'the term'}

        '''
        return self._unreplace(self._parse(qstring))

    def assemble(self, termdicts):
        "Assembles the list of tokens and term-dicts back to a querastring"
        querylist = []
        for termdict in termdicts:
            if isinstance(termdict, dict):
                tstring = termdict.get('field')
                tstring = tstring + ' : ' if tstring else ''
                tstring += termdict.get('term')
                querylist.append(tstring)
            else:
                querylist.append(termdict)
        query = ' '.join(querylist)
        return query
