"""

Script to build TSV file for raw input into CrowdFlower

"""

import csv
from typing import List

from base.data_types import Instance


def build_raw_data(fout: str, instances: List[Instance]) -> int:
    """
    Converts a list of instance objects into TSV format suitable for CrowdFlower
    TSV headers are ['paper_id', 'abstract', 'query', 'number_list', 'highlight_display']
    which are defined to match the CrowdFlower task definition files in
    `data_generator/crowdflower/example-task.*`

    Returns number of rows written to help with verification
    """

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
