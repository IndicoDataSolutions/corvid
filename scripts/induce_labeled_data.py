import re
import json

import argparse
import spacy
from spacy.lang.en import English

class AutoLabelPapers:
    '''
    Use rules to label tokens in paper abstracts as RESULTS or O.
    '''

    def __init__(self):
        self.nlp = English()
        self.tokenizer = English().Defaults.create_tokenizer(self.nlp)
        self.venue_regex = re.compile('ACL|EACL|TACL|EMNLP|IJCNLP')
        self.result_regex = re.compile('(?P<before_metric>f1 |uas |las |bleu |meteor |accuracy |precision |recall |performance |errors? )?(?P<before_qualifier>reduced by |of |more than |less than |above |over |improvements? |up to )*(?P<number>(\d+\.\d+|(\d+\.)?\d+%))\W+(?P<after_qualifier>improvements? in | reductions? in )?(?P<after_metric>relative |absolute |average |perplexity |f1 |uas |las |bleu |meteor |accuracy |precision |recall )*(?P<end_qualifier>improvements? |reductions? )?', re.I)
        self.number_regex = re.compile('\d+')

    def _is_paper_relevant(self, paper_record):
        '''
        Return true for a predefined list of relevant venues. Otherwise, return False.
        '''
        target_venue = self.venue_regex.search(paper_record['venue'])
        return target_venue
    
    def get_token_label_pairs(self, paper_record):
        '''
        Use regular expressions + tokenizer to identify numerical result tokens 
        in the paper abstract.
        '''
        abstract = paper_record['paperAbstract']
        tokens = self.tokenizer(abstract)
        token_label_pairs = []
        has_number = self.number_regex.search(abstract)
        has_result = self.result_regex.search(abstract)
        if has_result:
            number_begin_index, number_end_index = has_result.start('number'), has_result.end('number')
        for token in tokens:
            token_str = token.string.strip()
            if not token_str: continue
            if has_result and (has_result.group('after_metric') or has_result.group('before_metric')) and \
               (token.idx >= number_begin_index and token.idx + token.__len__() <= number_end_index):
                label = 'RESULT'
            else:
                label = 'O'
            token_label_pairs.append( (token_str, label) )
        return token_label_pairs

    def convert_s2_file_to_allennlp_labels(self, in_filename, out_filename):
        '''
        Reads paper abstracts in in_filename, label them with regexes, 
        and write the output to out_filename.
        in_filename: each line is a json object representing a paper, 
                     e.g., http://labs.semanticscholar.org/corpus/
        out_filename: a file suitable for consumption by the allennlp sequence_tagging data reader.
                      See https://allenai.github.io/allennlp-docs/api/allennlp.data.dataset_readers.sequence_tagging.html for details.
        '''
        count_all, count_with_results, count_without_results, count_ignored = 0, 0, 0, 0
        with open(in_filename, mode='rt', encoding='utf8') as in_file, open(out_filename, mode='wt', encoding='utf8') as out_file:
            for line in in_file:
                count_all += 1
                if count_all % 100 == 1:
                    print('all: {}, with results: {}, without results: {}, ignored: {}'.format(count_all, count_with_results, count_without_results, count_ignored))
                line = line.strip()
                if not line: continue
                paper_record = json.loads(line.strip())
        
                # skip papers we don't care about.
                if not self._is_paper_relevant(paper_record):
                    count_ignored += 1
                    continue
        
                # induce the token-label sequence.
                token_label_pairs = self.get_token_label_pairs(paper_record)
        
                # skip papers with no results.
                if not any([label == 'RESULT' for token, label in token_label_pairs]):
                    count_without_results += 1
                    continue
                else:
                    count_with_results += 1
                    
                # write to output file.
                out_file.write('{}\n'.format('\t'.join(['{}###{}'.format(token,label) for token, label in token_label_pairs])))
    
def main():
    parser = argparse.ArgumentParser(description='Automatically label numerical results in paper abstracts.')
    parser.add_argument('--in_filename', default = 'data/papers-2017-10-30.json',
                        help = 'An s2 file with one json paper object per line, e.g., http://labs.semanticscholar.org/corpus/')
    parser.add_argument('--out_filename', default = 'data/papers-2017-10-30.induced_labels',
                        help = 'An allennlp-compatible sequence tagging labels file, e.g., https://allenai.github.io/allennlp-docs/api/allennlp.data.dataset_readers.sequence_tagging.html')
    argparse_args = parser.parse_args()
    
    Labeler = AutoLabelPapers()
    Labeler.convert_s2_file_to_allennlp_labels(argparse_args.in_filename, argparse_args.out_filename)
    
if __name__ == "__main__":
    main()
