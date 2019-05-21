import os
from datetime import datetime, time
from file_utils import mkdir

reports_path = 'reports'


class Report:
    def __init__(self, comparison, date=None, comment=None):
        self.comparison = comparison
        if comment is None:
            comment = '_vs_'.join(map(lambda c: c.full_name, comparison.configurations)).replace(os.sep, "_")
        self.comment = comment
        if date is None:
            date = datetime.now()
        self.date = date
        self.full_name = 'summary_' + time.strftime(self.date, '%Y%m%d_%H%M%S') + '_' + comment
        self.results_dir = os.path.join(reports_path, self.full_name)

    def generate(self):
        c = self.comparison
        results_dir = self.ensure_results_dir()
        for p in [50,90,99]:
            path = os.path.join(results_dir, 'percentile{}.csv'.format(str(p)))
            c.csv_file(c.percentile(p), path)

    def ensure_results_dir(self):
        results_dir = self.results_dir
        mkdir(results_dir)
        return results_dir