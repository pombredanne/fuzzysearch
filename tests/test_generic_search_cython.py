from tests.compat import unittest
from tests.utils import skip_if_arguments_are_unicode
from tests.test_levenshtein import TestFindNearMatchesLevenshteinBase
from fuzzysearch.common import Match, get_best_match_in_group, group_matches
from tests.test_substitutions_only import TestSubstitionsOnlyBase
from tests.test_generic_search import TestGenericSearchBase

from six import b


try:
    from fuzzysearch._generic_search import \
        c_find_near_matches_generic_linear_programming as c_fnm_generic_lp, \
        c_find_near_matches_generic_ngrams as c_fnm_generic_ngrams
except ImportError:
    pass
else:
    class TestGenericSearchLpAsLevenshtein(TestFindNearMatchesLevenshteinBase,
                                           unittest.TestCase):
        @skip_if_arguments_are_unicode
        def search(self, subsequence, sequence, max_l_dist):
            return [
                get_best_match_in_group(group)
                for group in group_matches(
                    c_fnm_generic_lp(subsequence,
                                     sequence,
                                     max_l_dist, max_l_dist,
                                     max_l_dist, max_l_dist)
                )
            ]

    class TestGenericSearchNgramsAsLevenshtein(
        TestFindNearMatchesLevenshteinBase, unittest.TestCase):
        @skip_if_arguments_are_unicode
        def search(self, subsequence, sequence, max_l_dist):
            return [
                get_best_match_in_group(group)
                for group in group_matches(
                    c_fnm_generic_ngrams(subsequence,
                                         sequence,
                                         max_l_dist, max_l_dist,
                                         max_l_dist, max_l_dist)
                )
            ]


    class TestGenericSearchLpAsSubstitutionsOnly(TestSubstitionsOnlyBase,
                                                 unittest.TestCase):
        @skip_if_arguments_are_unicode
        def search(self, subsequence, sequence, max_subs):
            return list(
                c_fnm_generic_lp(subsequence,
                                 sequence,
                                 max_subs, 0, 0, max_subs)
            )

        def expectedOutcomes(self, search_results, expected_outcomes,
                             *args, **kw):
            return self.assertEqual(search_results, expected_outcomes,
                                    *args, **kw)


    class TestGenericSearchNgramsAsSubstitutionsOnly(TestSubstitionsOnlyBase,
                                                     unittest.TestCase):
        @skip_if_arguments_are_unicode
        def search(self, subsequence, sequence, max_subs):
            return [
                get_best_match_in_group(group)
                for group in group_matches(
                    c_fnm_generic_ngrams(subsequence,
                                         sequence,
                                         max_subs, 0, 0, max_subs)
                )
        ]

        def expectedOutcomes(self, search_results, expected_outcomes,
                             *args, **kw):
            best_from_grouped_results = [
                get_best_match_in_group(group)
                for group in group_matches(search_results)
            ]
            best_from_grouped_exepected_outcomes = [
                get_best_match_in_group(group)
                for group in group_matches(expected_outcomes)
            ]
            return self.assertEqual(best_from_grouped_results,
                                    best_from_grouped_exepected_outcomes,
                                    *args, **kw)


    class TestGenericSearchLp(TestGenericSearchBase, unittest.TestCase):
        @skip_if_arguments_are_unicode
        def search(self, pattern, sequence, max_subs, max_ins, max_dels,
                   max_l_dist=None):
            return list(c_fnm_generic_lp(pattern,
                                         sequence,
                                         max_subs, max_ins,
                                         max_dels, max_l_dist))

        def expectedOutcomes(self, search_result, expected_outcomes,
                             *args, **kw):
            self.assertEqual(search_result, expected_outcomes, *args, **kw)

        def test_double_first_item_two_results(self):
            self.assertEqual(
                self.search(b('def'), b('abcddefg'), 0, 1, 0),
                [Match(start=3, end=7, dist=1), Match(start=4, end=7, dist=0)],
            )

        def test_missing_second_item_complex(self):
            self.assertEqual(
                self.search(b('bde'), b('abcdefg'), 1, 1, 1, 1),
                [Match(start=1, end=5, dist=1),
                 Match(start=2, end=5, dist=1),
                 Match(start=3, end=5, dist=1)],
            )

            self.assertTrue(
                set([
                    Match(start=1, end=5, dist=1),
                    Match(start=2, end=5, dist=1),
                    Match(start=3, end=5, dist=1),
                    Match(start=2, end=5, dist=3),
                ]).issubset(set(
                    self.search(b('bde'), b('abcdefg'), 1, 1, 1, 3),
                ))
            )

    class TestGenericSearchNgrams(TestGenericSearchBase, unittest.TestCase):
        @skip_if_arguments_are_unicode
        def search(self, pattern, sequence, max_subs, max_ins, max_dels,
                   max_l_dist=None):
            return [
                get_best_match_in_group(group)
                for group in group_matches(
                    c_fnm_generic_ngrams(pattern,
                                         sequence,
                                         max_subs, max_ins,
                                         max_dels, max_l_dist)
                )
            ]

        def expectedOutcomes(self, search_result, expected_outcomes,
                             *args, **kw):
            best_from_groups = [
                get_best_match_in_group(group)
                for group in group_matches(search_result)
            ]
            self.assertEqual(search_result, best_from_groups, *args, **kw)

        def test_missing_second_item_complex(self):
            self.assertTrue(
                set(self.search(b('bde'), b('abcdefg'), 1, 1, 1, 1)).issubset([
                    Match(start=1, end=5, dist=1),
                    Match(start=2, end=5, dist=1),
                    Match(start=3, end=5, dist=1),
                ])
            )
