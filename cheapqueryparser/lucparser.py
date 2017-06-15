# _*_ coding: utf-8 _*_

# Based on
# https://lucene.apache.org/core/6_6_0/queryparser/org/apache/lucene/queryparser/classic/package-summary.html#package.description

import re

replacepairs = {
    'metaesc': ('\\\\\\\\', '_&_METAESC_&_'),
    'quot': ('\\\\"', '_&_QUOT_&_'),
    'space': ('\s', '_&_SPACE_&_'),
    'colon': (':', '_&_COLON_&_'),
    'pa': ('\\(', '_&_PA_&_'),
    'rens': ('\\)', '_&_RENS_&_'),
    }

revpairs = {
    'metaesc': ('_&_METAESC_&_', '\\\\'),
    'quot': ('_&_QUOT_&_','\\"'),
    'space': ('_&_SPACE_&_', ' '),
    'colon': ('_&_COLON_&_', ':'),
    'pa': ('_&_PA_&_', '('),
    'rens': ('_&_RENS_&_',')'),
    }
    
def replace_metaescape(qstring):
    "replaces escaped escapechar"
    fro, to = replacepairs['metaesc']
    qstring = re.sub(fro, to, qstring)
    return qstring

def replace_esc_quotes(qstring):
    "Replaces escaped quotation marks"
    fro, to = replacepairs['quot']
    qstring = re.sub(fro, to, qstring)
    return qstring

def _replace_in_range(qstring, rangepats, repair):
    '''Replaces according to replacepair in certain intervals
    of qstring, which are characterized by a list of patterns (rangepats).

    '''
    for pat in rangepats:
        matches = re.findall(pat, qstring)
        replacements = [re.sub(repair[0], repair[1], s) for s in matches]
        for m, rep in zip(matches, replacements):
            qstring = qstring.replace(m, rep)
    return qstring
 
def repspaces_in_ranges(qstring):
    '''Replace spaces inside range terms and inside quotes.
    Replace colons in range terms and inside quotes.
    Replace parenthesies in range terms and inside quotes.
    
    '''
    rangeex =  re.compile('(?<!\\\\)\{.*?(?<!\\\\)\}')
    rangeinc = re.compile('(?<!\\\\)\[.*?(?<!\\\\)\]')
    regex =    re.compile('(?<!\\\\)\/.*?(?<!\\\\)\/')
    quoted =   re.compile('".*?"')
    ranges = [rangeex, rangeinc, regex, quoted]
    re_pairs = [replacepairs['space'], replacepairs['colon'],
                replacepairs['pa'], replacepairs['rens']]
    for repair in re_pairs:
        qstring = _replace_in_range(qstring, ranges, repair)
        
    return qstring

def addparenswhitespace(qstring):
    reparens = {'(': ' ( ', ')': ' ) '}
    'Add space around "(" and ")" for separation from terms'
    qstring = re.sub('[\\(\\)]', lambda x: reparens[x.group()], qstring)
    return qstring
    
def stripspaces(qstring):
    'Removes spaces surrounding ":".'
    return re.sub(r'\s*(?<!\\\\):\s*', ':', qstring)

def repspaces_in_subqueries(qstring):
    '''Replace all spaces in field specific subqueries. That is is
    necessary so that the associaten with the subquery can be maintained.
    For example 'field:(+term1 -term2)'.
    Replace also all colons in field specific subqueries, necessary to prevent
    incorrect splitting.

    '''
    re_pairs = [replacepairs['space'], ('(?<!^):', '_&_COLON_&_')]
    rangepats = [':\\(.*?(?<!\\\\)\\)']
    for repair in re_pairs:
        qstring = _replace_in_range(qstring, rangepats, repair)
    return qstring

def termdicts(qsplitted):
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
    
def parse(qstring):
    qstring = replace_metaescape(qstring) # replace \\
    qstring = replace_esc_quotes(qstring) # replace \"
    qstring = repspaces_in_ranges(qstring)# replace \s and : in ranges and quotes
    qstring = addparenswhitespace(qstring) # add whitespace aound parenthesies
    qstring = stripspaces(qstring) # remove whitespace around :
    qstring = repspaces_in_subqueries(qstring) # make subqueries one item
    return termdicts(qstring.split())

def unreplace(termdicts):
    '''Reverses all replacements'''
    for termdict in termdicts:
        if not isinstance(termdict, dict):
            continue
        for key in termdict.keys():
            if termdict.get(key):
                for fro, to in revpairs.values():
                    termdict[key] = re.sub(fro, to, termdict[key])
    return termdicts

def deparse(qstring):
    '''Returns the final list of query-tokens, where terms ore replaced with
    dictionaries {'field': fieldname|None, 'term': 'the term'}

    '''
    return unreplace(parse(qstring))

def assemble(termdicts):
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


## take that as starting point
        
# IPackageController
    # Modify the search query to include the datasets from
    # the children organizations in the result list
    # HvW: Do this always
    def before_search(self, search_params):
        

        ''' If include children selected the query string is modified '''

        def _tokenize_search(queryfield):
            def repspace(st):
                # deal with escaped brackets
                # issue if st tarts with ( ? 
                pat = re.compile(r'(\([^)]*\))+')
                brackets = re.finditer(pat, st)
                splitted = re.split(pat, st)
                repstrings = []
                for b in brackets:
                    repstrings.append(re.sub(r' +', '__SPACE__',b.group()))
                for k, i in enumerate(range(1,len(splitted),2)):
                    splitted[i] = repstrings[k] 
                return ''.join(splitted)

            def splitspaces(st):
                st = re.sub(": +", ":", st)
                ## split querystring at spaces if space doesn't occur in quotes
                ## http://stackoverflow.com/a/2787064
                # deal with escaped quotqtion marks
                # implement this: https://stackoverflow.com/a/2787979/6930916
                pat = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
                splitspaces = pat.split(st)[1::2]
                splitspaces = [el.replace('__SPACE__',' ') for el in splitspaces]
                return splitspaces

            splitquery = splitspaces(repspace(search_params.get(queryfield, '')))
            querylist = [e.split(':', 1) for e in splitquery]
            return querylist
        
        def _assemble_query(q_list):
            print q_list
            q_string = ' '.join([':'.join(el) for el in q_list])
            return q_string
            
        # q_list = _tokenize_search('q')
        # search_params['q'] = _assemble_query(q_list)
        # fq_list = _tokenize_search('fq')
        # search_params['fq'] = _assemble_query(fq_list)
        # print('------------------------------------------------------------')
        # print(search_params)
        # print('------------------------------------------------------------')
        # return search_params

