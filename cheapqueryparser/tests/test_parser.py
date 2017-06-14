# _*_ coding: utf-8 _*_

import sys
import os.path
import json
curpath = os.path.dirname(os.path.realpath(__file__))
mainpath = os.path.abspath(os.path.join(curpath, '../..'))
sys.path.insert(0, mainpath)
from cheapqueryparser.lucparser import *

# def test_parse():
#     ts = ['"lecker \\" quot"', 'fi\{el\}d: \[bodat\]',
#           'field2\(spacy\):', '/reg*\/ex[^/]/', 'fi\\\\{el\\\\}d']
#     tsres = ['"lecker _&_QUOT_&_ quot"',
#              'fi_&_CURL_&_el_&_CURR_&_d: _&_BRA_&_bodat_&_KET_&_',
#              'field2_&_PA_&_spacy_&_REN_&_:',             
#              '/reg*_&_REGEX_&_ex[^/]/',
#              'fi_&_METAESC_&_{el_&_METAESC_&_}d']             
 
#     for s, sres in zip(ts, tsres):
#         assert(unquote(s) == sres)

def test_replace_metaescape():
    ts = r'abc\de \\fg\\h\i  j\k\\l\\\m'
    tsres = (r'abc\de _&_METAESC_&_fg_&_METAESC_&_h\i  '
             'j\k_&_METAESC_&_l_&_METAESC_&_\m')
    assert(tsres == replace_metaescape(ts))

def test_replace_esc_quotes():
    ts = 'abcde "fgh\\"ij\\"kl" mn\\"op\\"qr'
    tsres = 'abcde "fgh_&_QUOT_&_ij_&_QUOT_&_kl" mn_&_QUOT_&_op_&_QUOT_&_qr'
    assert(tsres == replace_esc_quotes(ts))

def test_repspaces_in_ranges():
    ts = (' jhas {82327 TO 938489} {kd\}k  TO  s\{ld} '
          '[38748374 TO 982938] \[kshsgh\] [ sdsd \]sdi\[pp p] '
          '"2  ksj  od": jgt oia"kj lk"ca "a:a:a"'
          '[2017:12 TO 3:4] {9:1 TO 6}')
    tsres = (' jhas {82327_&_SPACE_&_TO_&_SPACE_&_938489} '
             '{kd\}k_&_SPACE_&_TO_&_SPACE_&_s\{ld} [38748374_&_SPACE'
             '_&_TO_&_SPACE_&_982938] \[kshsgh\] [_&_SPACE_&_sdsd_&_SPACE_&_\]'
             'sdi\[pp_&_SPACE_&_p] "2_&_SPACE_&_ksj_&_SPACE_&_od": jgt oia"kj_'
             '&_SPACE_&_lk"ca "a_&_COLON_&_a_&_COLON_&_a"'
             '[2017_&_COLON_&_12_&_SPACE_&_TO_&_SPACE_&_3_&_COLON_&_4] '
             '{9_&_COLON_&_1_&_SPACE_&_TO_&_SPACE_&_6}')
    assert(tsres == repspaces_in_ranges(ts))

def test_addparenswhitespace():
    ts = 'aa(bb (c d)e )f'
    tsres = 'aa ( bb  ( c d ) e  ) f'
    assert(tsres == addparenswhitespace(ts))
    
def test_stripspaces():
    ts = ['a   : b', 'a:  b', 'a:b', 'a :b']
    assert(all([stripspaces(s) == 'a:b' for s in ts]))

def test_repspaces_in_subqueries():
    ts = 'field1:( term1 OR (term2 AND term\\)\\(3) term3 field2:term4'
    tsres = ('field1:(_&_SPACE_&_term1_&_SPACE_&_OR_&_SPACE_&_(term2_&'
             '_SPACE_&_AND_&_SPACE_&_term\\)\\(3) term3 field2:term4')
    assert(tsres == repspaces_in_subqueries(ts))
    # print('')
    # print(ts)
    # print(repspaces_in_subqueries(ts))

   
def test_parse():
    ts = ('term1 "term2" field1 : te\\"rm2 ( [2016 TO 2020:13:2] OR {A to "ABC"}) '
          '"field2"\\:haha: (term3 AND ("term hmm 4" OR field3:term5))')  
    print('')
    print(ts)
    print(parse(ts))



           


    
