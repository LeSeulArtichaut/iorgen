#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2018-2019 Sacha Delanoue
"""Check that parsers are the same as before, and parse correctly"""

import argparse
import os
import shutil
import sys

sys.path.insert(0, "..")
# pylint: disable=wrong-import-position
from iorgen import Input, ALL_LANGUAGES, ALL_MARKDOWN, Language, parse_input
from iorgen import input_errors
from iorgen.generator import compare_files, gen_compile_run_and_compare


def gen_is_same_as_sample(input_data: Input, prefix_path: str,
                          language: Language) -> bool:
    """Check that the generated parser is the same as the reference file"""
    filename = prefix_path + language.extension
    generated = language.generate(input_data).splitlines(True)
    return compare_files(generated, filename)


def test_samples() -> None:
    """Test all the samples"""
    try:
        shutil.rmtree("/tmp/iorgen/tests/")
    except FileNotFoundError:
        pass
    languages = {i.extension: i for i in ALL_LANGUAGES}
    parser = argparse.ArgumentParser(description="Tests for Iorgen")
    parser.add_argument('--languages',
                        '-l',
                        action='append',
                        help='languages to check',
                        choices=list(languages.keys()))
    parser.add_argument('--no_compilation',
                        action='store_true',
                        help='skip the compilation (and run) part')
    args = parser.parse_args()
    selected_languages = args.languages or list(languages.keys())
    for name in os.listdir("samples"):
        prefix = "samples/{0}/{0}.".format(name)
        with open(prefix + "yaml", 'r') as stream:
            input_data = parse_input(stream)
        sample_errors = input_errors(input_data, prefix + "sample_input")
        assert not sample_errors, sample_errors

        for language in ALL_LANGUAGES:
            assert gen_is_same_as_sample(input_data, prefix, language)
            if language.extension in selected_languages:
                assert gen_compile_run_and_compare(input_data, name, language,
                                                   "tests",
                                                   [prefix + "sample_input"],
                                                   args.no_compilation)

        for language in ALL_MARKDOWN:
            assert gen_is_same_as_sample(input_data, prefix, language)

        print("OK", name)


if __name__ == "__main__":
    test_samples()
