# _*_ coding: utf-8 _*_

# Based on
# https://lucene.apache.org/core/6_6_0/queryparser/org/apache/lucene/queryparser/classic/package-summary.html#package.description

import re


def parse(qstring):
    '''Parses qstring.

    '''
    pass

def unquote(qstring):
    '''Replaces quoted characters that are relevant for the parsing.

    '''
    def repstr(c):
        return '_&_{}_&_'.format(c)

    escchars = {'(': 'PA', ')': 'REN',
               '{': 'CURL', '}':'CURR',
               '[': 'BRA', ']': 'KET',
                '/': 'REGEX', '"': 'QUOT'}

    esc = '\\'
    metaesc = ('\\\\', 'METAESC')
    # replace escaped escapes
    qstring = qstring.replace(metaesc[0], repstr(metaesc[1]))
    # replace escapes
    for c, rep in escchars.iteritems():
        qstring = qstring.replace(esc + c, repstr(rep))
    return qstring

                                  
    
                              


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

