"""


"""

import unittest

from corvid.types.table import Token, Cell, Table
from corvid.evaluation.compute_metrics import compute_metrics


class TestComputeMetrcis(unittest.TestCase):
    def setUp(self):
        self.gold_cells = [ Cell(tokens=[Token(text='Model')], rowspan=1, colspan=1), 
                      Cell( tokens=[Token(text='EM')], rowspan=1, colspan=1), 
                      Cell( tokens=[Token(text='F1')], rowspan=1, colspan=1),
                      Cell( tokens=[Token(text='CNN')], rowspan=1, colspan=1),
                      Cell( tokens=[Token(text='35')], rowspan=1, colspan=1),
                      Cell( tokens=[Token(text='15')], rowspan=1, colspan=1),
                      Cell( tokens=[Token(text='RNN')], rowspan=1, colspan=1),
                      Cell( tokens=[Token(text='75')], rowspan=1, colspan=1),
                      Cell( tokens=[Token(text='50')], rowspan=1, colspan=1)
                   ]

        self.agg_cells = [ Cell( tokens=[Token(text='Model')], rowspan=1, colspan=1), 
                      Cell( tokens=[Token(text='EM')], rowspan=1, colspan=1), 
                      Cell( tokens=[Token(text='F1')], rowspan=1, colspan=1), 
                      Cell( tokens=[Token(text='CNN')], rowspan=1, colspan=1),
                      Cell( tokens=[Token(text='35')], rowspan=1, colspan=1),
                      Cell( tokens=[Token(text='15')], rowspan=1, colspan=1),
                      Cell( tokens=[Token(text='RNN')], rowspan=1, colspan=1),
                      Cell( tokens=[Token(text='75')], rowspan=1, colspan=1),
                      Cell( tokens=[Token(text='50')], rowspan=1, colspan=1)
            ]

        self.gold_table = Table(self.gold_cells,3,3,'example_gold_paper_id',1,'example_caption')
        self.aggregate_table = Table(self.agg_cells,3,3,'example_agg_paper_id',1,'example_caption')

        self.metric_scores = {'schema_match_accuracy': 100, 'table_match_ccuracy_exact': 100, 'table_match_ccuracy_inexact':100}


    def test_compute_metrics(self):
        self.assertDictEqual(compute_metrics(self.gold_table,self.aggregate_table),self.metric_scores)


       
      
