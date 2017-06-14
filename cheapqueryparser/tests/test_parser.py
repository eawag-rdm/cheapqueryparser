# _*_ coding: utf-8 _*_

import sys
import os.path
import json
curpath = os.path.dirname(os.path.realpath(__file__))
mainpath = os.path.abspath(os.path.join(curpath, '../..'))
sys.path.insert(0, mainpath)
from cheapqueryparser.lucparser import *

def test_parse():
    ts = ['"lecker \\" quot"', 'fi\{el\}d: \[bodat\]',
          'field2\(spacy\):', '/reg*\/ex[^/]/', 'fi\\\\{el\\\\}d']
    tsres = ['"lecker _&_QUOT_&_ quot"',
             'fi_&_CURL_&_el_&_CURR_&_d: _&_BRA_&_bodat_&_KET_&_',
             'field2_&_PA_&_spacy_&_REN_&_:',             
             '/reg*_&_REGEX_&_ex[^/]/',
             'fi_&_METAESC_&_{el_&_METAESC_&_}d']             
    # print  
    for s, sres in zip(ts, tsres):
        assert(unquote(s) == sres)
        # print(s)
        # print(unquote(s))
        # print
