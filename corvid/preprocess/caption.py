"""

Class used to represent a table caption:

"""

import re
import warnings

from typing import List
from bs4 import Tag, BeautifulSoup
from data_types import Table

class Caption(object):
    def __init__(self):
        pass
    

    def _searchforcaption(self, candidates: List, current_idx, caption_texts: List, caption_search_window):
        """
        Search for the caption text in a window of size 'caption_search_window'. 
        Return when forst match is found
        """
        non_caption_candidates = []

        for window_idx in range( 1, caption_search_window+1 ):
            caption_candidate = " ".join([text.getText() for text in candidates[current_idx-window_idx].find_all('text')])
            if caption_candidate.lower().strip().startswith('table',0,5):
                caption_texts.append(caption_candidate)
                non_caption_candidates.append('nil')
                return (caption_texts, non_caption_candidates)
            else:
                non_caption_candidates.append(caption_candidate)
                try:                    
                    caption_candidate = " ".join([text.getText() for text in candidates[current_idx+window_idx].find_all('text')])

                    if caption_candidate.lower().strip().startswith('table',0,5):
                        caption_texts.append(caption_candidate)
                        return (caption_texts, non_caption_candidates)
                    else:
                        non_caption_candidates.append(caption_candidate)
                except:
                    pass

        caption_texts.append('nil')
        return (caption_texts, non_caption_candidates)
            


    def find_caption(self, xml: BeautifulSoup, caption_search_window = 3):
        """
        Find `Caption` by inferring from tetml xml para tags 
        that appear in the vicinity of Table element 
        """
        candidates_raw      = xml.find_all(['para', 'table'])
        candidates          = []
        
        caption_texts       = []
        non_caption_texts   = []
        table_child_paras   = []
        tables              = []

        # value of n will have a window of length 3 
        # from <table> element +n to <table> element -n

        # Filters para elements from candidates that occur as children of the table element
        for element in candidates_raw:
            if element.name == 'table':
                table_child_paras = []
                candidates.append(element)
                for child in element.findChildren():
                    table_child_paras.append(child.getText())
            if element.name == 'para':
                if element.getText() not in table_child_paras:
                    candidates.append(element)
        
        for i,element in enumerate(candidates):
            if element.name == 'table':
                #TODO create normalised tables and return in addition to tetml tables
                #table = Table.from_bs4_tag(element)
                tables.append(element.find_all('text'))
                
                (caption_texts, non_caption_candidates) = self._searchforcaption(   candidates,
                                                                                    i, 
                                                                                    caption_texts, 
                                                                                    caption_search_window
                                                                                )

                non_caption_texts.append(non_caption_candidates)

        return (tables, caption_texts, non_caption_texts)