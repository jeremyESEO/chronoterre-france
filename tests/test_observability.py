import unittest
from datetime import datetime, timezone

from national.observability import acquisition_freshness


class FreshnessTests(unittest.TestCase):
    def test_one_recent_page_does_not_mask_an_old_batch(self):
        files = {
            'page_0': {'source': 'pbdb', 'fetched_at': '2026-09-25T13:30:00+00:00'},
            'page_1': {'source': 'pbdb', 'fetched_at': '2026-11-06T13:30:00+00:00'},
        }
        now = datetime(2026, 11, 7, 18, tzinfo=timezone.utc)
        result = acquisition_freshness(files, {'pbdb': {'review_after_days': 30}}, now)['pbdb']
        self.assertEqual(result['status'], 'REVIEW_DUE')
        self.assertEqual(result['max_acquisition_age_days'], 43)
        self.assertEqual(result['raw_files'], 2)

    def test_missing_timestamp_cannot_be_presented_as_fresh(self):
        now = datetime(2026, 11, 7, 18, tzinfo=timezone.utc)
        result = acquisition_freshness({'file': {'source': 'gpu'}}, {'gpu': {'review_after_days': 30}}, now)['gpu']
        self.assertEqual(result['status'], 'INVALID_TIMESTAMP')
        self.assertIsNone(result['max_acquisition_age_days'])
        self.assertEqual(result['invalid_raw_timestamps'], ['file'])
