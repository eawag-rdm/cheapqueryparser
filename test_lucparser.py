# _*_ coding: utf-8 _*_

import sys
import os.path
import json
from lucparser import LucParser

lp = LucParser()

def test_replace_metaescape():
    ts = r'abc\de \\fg\\h\i  j\k\\l\\\m'
    tsres = (r'abc\de _&_METAESC_&_fg_&_METAESC_&_h\i  '
             'j\k_&_METAESC_&_l_&_METAESC_&_\m')
    assert(tsres == lp._replace_metaescape(ts))

def test_replace_esc_quotes():
    ts = 'abcde "fgh\\"ij\\"kl" mn\\"op\\"qr'
    tsres = 'abcde "fgh_&_QUOT_&_ij_&_QUOT_&_kl" mn_&_QUOT_&_op_&_QUOT_&_qr'
    assert(tsres == lp._replace_esc_quotes(ts))

def test_repspaces_in_ranges():
    ts = (' jhas {82327 TO 938489} {kd\}k  TO  s\{ld} '
          '[38748374 TO 982938] \[kshsgh\] [ sdsd \]sdi\[pp p] '
          '"2  ksj  od": jgt oia"kj lk"ca "a:a:a" /a reg(\/ :)e"x/'
          '[2017:12 TO 3:4] {9:1 TO 6}')
    
    tsres = (' jhas {82327_&_SPACE_&_TO_&_SPACE_&_938489} {kd\}k_&_S'
             'PACE_&__&_SPACE_&_TO_&_SPACE_&__&_SPACE_&_s\{ld} [3874'
             '8374_&_SPACE_&_TO_&_SPACE_&_982938] \[kshsgh\] [_&_SPA'
             'CE_&_sdsd_&_SPACE_&_\]sdi\[pp_&_SPACE_&_p] "2_&_SPACE_'
             '&__&_SPACE_&_ksj_&_SPACE_&__&_SPACE_&_od": jgt oia"kj_'
             '&_SPACE_&_lk"ca "a_&_COLON_&_a_&_COLON_&_a" /a_&_SPACE'
             '_&_reg_&_PA_&_\/_&_SPACE_&__&_COLON_&__&_RENS_&_e"x/[2'
             '017_&_COLON_&_12_&_SPACE_&_TO_&_SPACE_&_3_&_COLON_&_4] '
             '{9_&_COLON_&_1_&_SPACE_&_TO_&_SPACE_&_6}')

    # print(' REPSPACES')
    # print('--------------------------------------------------------------')
    # print(ts)
    # print('--------------------------------------------------------------')
    # print(repspaces_in_ranges(ts))
    # print('--------------------------------------------------------------')
    assert(tsres == lp._repspaces_in_ranges(ts))

def test_addparenswhitespace():
    ts = 'aa(bb (c d)e )f'
    tsres = 'aa ( bb  ( c d ) e  ) f'
    assert(tsres == lp._addparenswhitespace(ts))
    
def test_stripspaces():
    ts = ['a   : b', 'a:  b', 'a:b', 'a :b']
    assert(all([lp._stripspaces(s) == 'a:b' for s in ts]))

def test_repspaces_in_subqueries():
    ts = 'field1:( term1 OR (term2 AND term\\)\\(3) term3 field2:term4'
    tsres = ('field1:(_&_SPACE_&_term1_&_SPACE_&_OR_&_SPACE_&_(term2_&'
             '_SPACE_&_AND_&_SPACE_&_term\\)\\(3) term3 field2:term4')
    assert(tsres == lp._repspaces_in_subqueries(ts))
    # print('')
    # print(ts)
    # print(repspaces_in_subqueries(ts))
    
def test__termdicts():
    ts = ['hol:"mir"','AND', 'die:wurst', '!', 'OR', '(', 'sonst', 'NOT',
          'muss:ich', ')', '&&', '+"1 Brot essen!"', '||', '123']
    tsres = [{'field': 'hol', 'term': '"mir"'}, 'AND',
             {'field': 'die', 'term': 'wurst'}, '!', 'OR', '(',
             {'field': None, 'term': 'sonst'}, 'NOT',
             {'field': 'muss', 'term': 'ich'}, ')', '&&',
             {'field': None, 'term': '+"1 Brot essen!"'}, '||',
             {'field': None, 'term': '123'}]
    assert(tsres == lp._termdicts(ts))
    # print('')
    # print ts
    # print(termdicts(ts))
    # assert
        
def test_parse():
    ts = ('term1 "term2" field1 : te\\"rm2 ( [2016 TO 2020:13:2] OR {A to "ABC"}) '
          '"field2"\\:haha: (term3 AND ("term hmm 4" OR field3:term5))')

    tsres = [{'field': None, 'term': 'term1'}, {'field': None, 'term': '"term2"'},
             {'field': 'field1', 'term': 'te\\"rm2'}, '(',
             {'field': None, 'term': '[2016 TO 2020:13:2]'}, 'OR',
             {'field': None, 'term': '{A to "ABC"}'}, ')',
             {'field': '"field2"\\:haha',
              'term': '( term3 AND  ( "term hmm 4" OR field3:term5 )'
             }, ')']

    # print('test_parse')
    # print('------------------------------------------------------------------------------')
    # print(tsres)
    # print('------------------------------------------------------------------------------')
    # print(deparse(ts))
    assert(lp.deparse(ts) == tsres)

def test_assemble():
    ts = ('term1 "term2" AND field1 : te\\"rm2 ( [2016 TO 2020:13:2] OR '
          'q{A to "ABC"}) NOT \}\] "field2"\\:haha: ("term3" AND ("term \\\"hmm'
          '4" OR field3:term5))')
    tsres = ('term1 "term2" AND field1 : te\\"rm2 ( [2016 TO 2020:13:2] OR '
             'q{A to "ABC"} ) NOT \}\] "field2"\:haha : ( "term3" AND  ( "term \\\"hmm'
             '4" OR field3:term5 ) )')
    
    assert(tsres == lp.assemble(lp.deparse(ts)))
    # print('test_assemble')
    # print(tsres)
    # print('------------------------------------------------------------------------------')
    # print(assemble(deparse(ts)))

def test_get_fieldname_indices():
    ts = ['(', 'AND', {'field': 'fn_one', 'term': 'term_one'},
          ')', 'OR', {'field': 'fn_two', 'term': 'term_two'},
          '[','what',  {'field': 'fn_one', 'term': 'term_one_1'},')']

    assert(lp._get_fieldname_indices(ts, 'fn_one') == [2, 8])
    assert(lp._get_fieldname_indices(ts, 'fn_two') == [5])
    assert(lp._get_fieldname_indices(ts, 'fn_not') == [])

def test_add_to_query():
    q = ('field1: (son quatsch) AND field2: pfffrt (haalo OR field1: (ich OR er) '
         ') globalterm field1 : yepp')
         
    res = lp.add_to_query(q, 'OR "ich auch"', fieldname='field1')
    assert(res == 'field1 : (( son quatsch ) OR "ich auch") AND field2 '
           ': pfffrt ( haalo OR field1 : (( ich OR er ) OR "ich auch") ) '
           'globalterm field1 : (yepp OR "ich auch")')
    res = lp.add_to_query(q, 'OR "ich auch"')
    assert(res == '( field1: (son quatsch) AND field2: pfffrt (haalo OR field1'
           ': (ich OR er) ) globalterm field1 : yepp ) OR "ich auch"')
    

