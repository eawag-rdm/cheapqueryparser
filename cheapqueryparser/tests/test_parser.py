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
 
    for s, sres in zip(ts, tsres):
        assert(unquote(s) == sres)

def test_stripspaces():
    ts = ['a   : b', 'a:  b', 'a:b', 'a :b']
    assert(all([stripspaces(s) == 'a:b' for s in ts])) 

def test_repspaces():
    ts = ' jhas {82327 TO 938489} {kd\}k  TO  s\{ld} [38748374 TO 982938] \[kshsgh\] [ sdsd \]sdi\[pp p]'
    tsres = ' jhas {82327_&_SPACE_&_TO_&_SPACE_&_938489} {kd\}k_&_SPACE_&_TO_&_SPACE_&_s\{ld} [38748374_&_SPACE_&_TO_&_SPACE_&_982938] \[kshsgh\] [_&_SPACE_&_sdsd_&_SPACE_&_\]sdi\[pp_&_SPACE_&_p]'
    assert(tsres == repspaces(ts))

def test_replace_esc_quotes():
    ts = 'abcde "fgh\\"ij\\"kl" mn\\"op\\"qr'
    tsres = 'abcde "fgh_&_QUOT_&_ij_&_QUOT_&_kl" mn_&_QUOT_&_op_&_QUOT_&_qr'
    assert(tsres == replace_esc_quotes(ts))


           


    
