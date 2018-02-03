"""

Class used to represent a table caption:

"""

import re
import warnings
from collections import namedtuple
from typing import List, Dict, Tuple

from bs4 import Tag, BeautifulSoup


class Caption(object):
    def __init__(self,):
        pass
    
    def _find_caption(self, xml: BeautifulSoup):
        """Create `Caption` by inferring from tetml xml para tags 
        that appear before a Table tag 
        """
        candidates_raw = xml.find_all(['para', 'table'])
        candidates = []
        
        caption_para = []
        caption_texts = []
        table_child_paras = []
        tables = []

        # Filters para tags from candidates that occur as children of the table tag
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
                    tables.append(element)
                    caption_text = []
                    caption_text.append(" ".join([text.getText() for text in candidates[i+1].find_all('text')]))
                    caption_text.append(" ".join([text.getText() for text in candidates[i-1].find_all('text')]))
                    caption_texts.append(caption_text)
                    caption_para.append(candidates[i+1])
                    caption_para.append(candidates[i-1])
        return (tables,caption_texts)