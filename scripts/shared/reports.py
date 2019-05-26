import os
from datetime import datetime

from file_utils import mkdir, dict_to_file, dict_from_file, touch

date_format = '%Y%m%d_%H%M%S'

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
        self.full_name = 'summary_' + datetime.strftime(self.date, date_format) + '_' + comment
        self.results_dir = os.path.join(reports_path, self.full_name)
        self.settings_file = os.path.join(self.results_dir, 'settings.properties')
        self.done_file = os.path.join(self.results_dir, '.done')

    def generate(self):
        if self.is_done():
            copy = Report(self.comparison, date=None, comment=self.comment)
            copy.generate()
            return copy
        else:
            c = self.comparison
            results_dir = self.ensure_dir()
            for p in [50, 90, 99]:
                path = os.path.join(results_dir, 'percentile{}.csv'.format(str(p)))
                c.csv_file(c.percentile(p), path)
            self.mark_done()
            return self

    def mark_done(self):
        touch(self.done_file)

    def is_done(self):
        return os.path.isfile(self.done_file)

    def write_settings(self):
        settings_file = self.settings_file
        kv = self.to_dict()
        dict_to_file(settings_file, kv)

    @classmethod
    def from_full_name(cls, full_name):
        return cls.from_dir(os.path.join(reports_path, full_name))

    @classmethod
    def from_dir(cls, full_path):
        settings_file = os.path.join(full_path, 'settings.properties')
        kv = dict_from_file(settings_file)
        return cls.from_dict(kv)

    def ensure_dir(self):
        results_dir = self.results_dir
        mkdir(results_dir)
        self.write_settings()
        return results_dir

    @classmethod
    def from_dict(cls, kv):
        comment = kv.get('comment')
        raw_date = kv.get('date')
        if raw_date is None:
            date = None
        else:
            date = datetime.strptime(raw_date, date_format)
        from comparison import Comparison
        return cls(Comparison.from_dict(kv), date, comment)

    def to_dict(self):
        kv = self.comparison.to_dict()
        kv['comment'] = self.comment
        kv['date'] = datetime.strftime(self.date, date_format)
        return kv
