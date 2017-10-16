from tests.compat import unittest, mock
from tests.test_common import TestSearchExactBase
from tests.test_substitutions_only import TestSubstitionsOnlyBase
from tests.test_levenshtein import TestFindNearMatchesLevenshteinBase

from fuzzysearch import find_near_matches, Match


class MockFunctionFailsUnlessDefined(object):
    UNDEFINED = object()

    def __init__(self):
        self.return_value = self.UNDEFINED
        self.call_count = 0
        self.call_args = None

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        self.call_args = (args, kwargs)

        if self.return_value is self.UNDEFINED:
            raise Exception('Undefined mock function called!')
        else:
            return self.return_value


class TestFindNearMatches(unittest.TestCase):
    def patch_concrete_search_methods(self):
        self.mock_search_exact = MockFunctionFailsUnlessDefined()
        self.mock_find_near_matches_levenshtein = \
            MockFunctionFailsUnlessDefined()
        self.mock_find_near_matches_substitutions = \
            MockFunctionFailsUnlessDefined()
        self.mock_find_near_matches_generic = \
            MockFunctionFailsUnlessDefined()

        patcher = mock.patch.multiple(
            'fuzzysearch',
            search_exact=self.mock_search_exact,
            find_near_matches_levenshtein=
                self.mock_find_near_matches_levenshtein,
            find_near_matches_substitutions=
                self.mock_find_near_matches_substitutions,
            find_near_matches_generic=
                self.mock_find_near_matches_generic,
        )
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_no_limitations(self):
        with self.assertRaises(Exception):
            find_near_matches('a', 'a')

    def test_unlimited_parameter(self):
        with self.assertRaises(Exception):
            find_near_matches('a', 'a', max_substitutions=1)

        with self.assertRaises(Exception):
            find_near_matches('a', 'a', max_insertions=1)

        with self.assertRaises(Exception):
            find_near_matches('a', 'a', max_deletions=1)

        with self.assertRaises(Exception):
            find_near_matches('a', 'a', max_substitutions=1, max_insertions=1)

        with self.assertRaises(Exception):
            find_near_matches('a', 'a', max_substitutions=1, max_deletions=1)

        with self.assertRaises(Exception):
            find_near_matches('a', 'a', max_insertions=1, max_deletions=1)

    def test_all_zero(self):
        self.patch_concrete_search_methods()
        self.mock_search_exact.return_value = [42]
        self.assertEqual(
            find_near_matches('a', 'a', 0, 0, 0, 0),
            [Match(42, 43, 0)],
        )
        self.assertEqual(self.mock_search_exact.call_count, 1)

    def test_zero_max_l_dist(self):
        self.patch_concrete_search_methods()
        self.mock_search_exact.return_value = [42]

        call_count = 0
        for (max_subs, max_ins, max_dels) in [
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (1, 1, 0),
            (1, 0, 1),
            (0, 1, 1),
            (1, 1, 1),
        ]:
            with self.subTest('max_l_dist=0, max_subs={0}, max_ins={1}, max_dels={2}'.format(
                    max_subs, max_ins, max_dels)):
                self.assertEqual(
                    find_near_matches('a', 'a', max_subs, max_ins, max_dels, 0),
                    [Match(42, 43, 0)],
                )
                call_count += 1
                self.assertEqual(self.mock_search_exact.call_count, call_count)

    def test_all_zero_except_max_l_dist(self):
        self.patch_concrete_search_methods()
        self.mock_search_exact.return_value = [42]

        self.assertEqual(
            find_near_matches('a', 'a', 0, 0, 0, 1),
            [Match(42, 43, 0)],
        )
        self.assertEqual(self.mock_search_exact.call_count, 1)

    def test_all_none_except_max_l_dist(self):
        self.patch_concrete_search_methods()
        self.mock_find_near_matches_levenshtein.return_value = [42]

        self.assertEqual(
            find_near_matches('a', 'a', max_l_dist=1),
            [42],
        )
        self.assertEqual(self.mock_find_near_matches_levenshtein.call_count, 1)

    def test_levenshtein(self):
        """test cases where 0 < max_l_dist <= max(others)"""
        # in these cases, find_near_matches should call
        # find_near_matches_levenshtein
        self.patch_concrete_search_methods()
        self.mock_find_near_matches_levenshtein.return_value = \
            [mock.sentinel.SENTINEL]

        self.assertEqual(
            find_near_matches('a', 'a', 1, 1, 1, 1),
            [mock.sentinel.SENTINEL],
        )
        self.assertEqual(self.mock_find_near_matches_levenshtein.call_count, 1)

        self.assertEqual(
            find_near_matches('a', 'a', 2, 2, 2, 2),
            [mock.sentinel.SENTINEL],
        )
        self.assertEqual(self.mock_find_near_matches_levenshtein.call_count, 2)

        self.assertEqual(
            find_near_matches('a', 'a', 5, 3, 7, 2),
            [mock.sentinel.SENTINEL],
        )
        self.assertEqual(self.mock_find_near_matches_levenshtein.call_count, 3)

    def test_only_substitutions(self):
        self.patch_concrete_search_methods()
        self.mock_find_near_matches_substitutions.return_value = [42]

        self.assertEqual(
            find_near_matches('a', 'a', 1, 0, 0),
            [42],
        )
        self.assertEqual(
            self.mock_find_near_matches_substitutions.call_count,
            1,
        )

        self.assertEqual(
            find_near_matches('a', 'a', 1, 0, 0, 1),
            [42],
        )
        self.assertEqual(
            self.mock_find_near_matches_substitutions.call_count,
            2,
        )

    def test_generic(self):
        self.patch_concrete_search_methods()
        self.mock_find_near_matches_generic.return_value = [42]

        self.assertEqual(
            find_near_matches('a', 'a', 1, 1, 1),
            [42],
        )
        self.assertEqual(
            self.mock_find_near_matches_generic.call_count,
            1,
        )

        self.assertEqual(
            find_near_matches('a', 'a', 1, 1, 1, 2),
            [42],
        )
        self.assertEqual(
            self.mock_find_near_matches_generic.call_count,
            2,
        )


class TestFindNearMatchesAsLevenshtein(TestFindNearMatchesLevenshteinBase,
                                       unittest.TestCase):
    def search(self, subsequence, sequence, max_l_dist):
        return find_near_matches(subsequence, sequence, max_l_dist=max_l_dist)


class TestFindNearMatchesAsSearchExact(TestSearchExactBase,
                                       unittest.TestCase):
    def search(self, subsequence, sequence, start_index=0, end_index=None):
        if end_index is None:
            end_index = len(sequence)
        sequence = sequence[start_index:end_index]
        return [
            start_index + match.start
            for match in find_near_matches(subsequence, sequence, max_l_dist=0)
        ]

    @classmethod
    def get_supported_sequence_types(cls):
        from tests.test_common import TestSearchExact
        return TestSearchExact.get_supported_sequence_types()


class TestFindNearMatchesAsSubstitutionsOnly(TestSubstitionsOnlyBase,
                                             unittest.TestCase):
    def search(self, subsequence, sequence, max_subs):
        return find_near_matches(subsequence, sequence,
                                 max_insertions=0, max_deletions=0,
                                 max_substitutions=max_subs)

    def expectedOutcomes(self, search_results, expected_outcomes, *args, **kwargs):
        return self.assertEqual(search_results, expected_outcomes, *args, **kwargs)


from tests.test_generic_search import TestGenericSearch
class TestFindNearMatchesAsGeneric(TestGenericSearch,
                                   unittest.TestCase):
    def search(self, pattern, sequence, max_subs, max_ins, max_dels,
               max_l_dist=None):
        return find_near_matches(pattern, sequence,
                                 max_subs, max_ins, max_dels, max_l_dist)
del TestGenericSearch
