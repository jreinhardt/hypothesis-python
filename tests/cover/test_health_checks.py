# coding=utf-8
#
# This file is part of Hypothesis (https://github.com/DRMacIver/hypothesis)
#
# Most of this work is copyright (C) 2013-2015 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# https://github.com/DRMacIver/hypothesis/blob/master/CONTRIBUTING.rst for a
# full list of people who may hold copyright, and consult the git log if you
# need to determine who owns an individual contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
#
# END HEADER

from __future__ import division, print_function, absolute_import

import time

from pytest import raises

import hypothesis.strategies as st
from hypothesis import given
from hypothesis.errors import FailedHealthCheck


def test_slow_generation_fails_a_health_check():
    @given(st.integers().map(lambda x: time.sleep(0.2)))
    def test(x):
        pass

    with raises(FailedHealthCheck):
        test()


def test_global_random_in_strategy_fails_a_health_check():
    import random

    @given(st.lists(st.integers(), min_size=1).map(random.choice))
    def test(x):
        pass

    with raises(FailedHealthCheck):
        test()


def test_global_random_in_test_fails_a_health_check():
    import random

    @given(st.lists(st.integers(), min_size=1))
    def test(x):
        random.choice(x)

    with raises(FailedHealthCheck):
        test()


def test_error_in_strategy_produces_health_check_error():
    def boom(x):
        raise ValueError()

    @given(st.integers().map(boom))
    def test(x):
        pass

    with raises(FailedHealthCheck) as e:
        test()
    assert 'executor' not in e.value.args[0]


def test_error_in_strategy_with_custom_executor():
    def boom(x):
        raise ValueError()

    class Foo(object):

        def execute_example(self, f):
            return f()

        @given(st.integers().map(boom))
        def test(x):
            pass

    with raises(FailedHealthCheck) as e:
        Foo().test()
    assert 'executor' in e.value.args[0]