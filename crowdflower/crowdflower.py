"""

Script to build TSV file for raw input into CrowdFlower

"""

from typing import List

import csv

from python.instance import Instance


class CrowdFlower(object):
    def build_raw_data(self, fout: str, instances: List[Instance]) -> int:
        with open(fout, 'w') as tsvfile:
            writer = csv.writer(tsvfile, delimiter='\t')
            writer.writerow(['paper_id', 'abstract', 'query', 'number_list',
                             'highlight_display'])
            i = 0
            for instance in instances:
                row = [instance.paper.id, instance.paper.abstract,
                       ', '.join([w.title() for w in instance.query.keywords]),
                       ','.join([str(m.as_num) for m
                                 in instance.paper.mentions]),
                       ','.join([m.as_str for m in instance.paper.mentions])]
                writer.writerow(row)
                i += 1
        print('Wrote {} rows to {}'.format(i, fout))
        return i

