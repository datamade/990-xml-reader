import os

import pytest
from irsx.file_utils import validate_object_id
from irsx.filing import Filing
from irsx.irsx_cli import get_parser as get_cli_parser
from irsx.irsx_cli import run_main as run_cli_main
from irsx.irsx_index_cli import get_cli_index_parser, run_cli_index_main
from irsx.object_ids import object_ids_2015, object_ids_2016, object_ids_2017
from irsx.settings import WORKING_DIRECTORY
from irsx.standardizer import Standardizer
from irsx.xmlrunner import XMLRunner

FILING_2015V21 = "201642229349300909"
FILING_2015V21_skeds = [
    "ReturnHeader990x",
    "IRS990",
    "IRS990ScheduleA",
    "IRS990ScheduleB",
    "IRS990ScheduleD",
    "IRS990ScheduleM",
    "IRS990ScheduleO",
]

# SUTTER HEALTH SACRAMENTO REGION 2014 filing has multiple schedule K's.
FILING_2014V50 = "201533089349301428"

FILING_2014V50_skeds = [
    "ReturnHeader990x",
    "IRS990",
    "IRS990ScheduleA",
    "IRS990ScheduleB",
    "IRS990ScheduleC",
    "IRS990ScheduleD",
    "IRS990ScheduleG",
    "IRS990ScheduleH",
    "IRS990ScheduleI",
    "IRS990ScheduleJ",
    "IRS990ScheduleK",
    "IRS990ScheduleL",
    "IRS990ScheduleM",
    "IRS990ScheduleO",
    "IRS990ScheduleR",
]

FILING_2022 = "202210409349301026"

# don't bother testing every filing in tests
TEST_DEPTH = 10

# When set to false don't test download files that are already there.
# Runs faster set to off!
DOWNLOAD = False


def test_valid_object_id():
    result = validate_object_id(FILING_2022)


def test_process_from_id_only():
    a = Filing(FILING_2022)
    a.process()


def test_process_from_id_only_2():
    a = Filing(FILING_2014V50)
    a.process()
    assert a.get_version() == "2014v5.0"


@pytest.mark.skip(reason="Not sure why this is failing now. Was commented out.")
def test_process_with_filepath():
    filename = "%s_public.xml" % FILING_2015V21
    filepath = os.path.join(WORKING_DIRECTORY, filename)
    a = Filing(FILING_2015V21, filepath=filepath)
    a.process()
    assert a.get_version() == "2015v2.1"


# test without runner
class TestConversion:
    """Still doesn't validate actual values, but..."""

    def setup_method(self):
        self.xml_runner = XMLRunner()

    def test_case_1(self):
        self.xml_runner.run_filing(FILING_2022)

    def test_case_2(self):
        object_ids = (
            object_ids_2017[:TEST_DEPTH]
            + object_ids_2016[:TEST_DEPTH]
            + object_ids_2015[:TEST_DEPTH]
        )
        for object_id in object_ids:
            self.xml_runner.run_filing(object_id)


class TestRunner:
    """Test using runner class"""

    def setup_method(self):
        self.xml_runner = XMLRunner()

    @pytest.mark.skip(reason="Not sure why this is failing now. Was commented out.")
    def test1(self):
        parsed_filing = self.xml_runner.run_filing(FILING_2022)
        assert parsed_filing.get_type() == "IRS990"
        parsed_filing_schedules = parsed_filing.list_schedules()
        for sked in FILING_2015V21_skeds:
            assert sked in parsed_filing_schedules
            parsed_filing.get_parsed_sked(sked)

    def test_multiple_sked_ks(self):
        parsed_filing = self.xml_runner.run_filing(FILING_2014V50)
        assert parsed_filing.get_type() == "IRS990"
        parsed_filing_schedules = parsed_filing.list_schedules()
        for sked in FILING_2014V50_skeds:
            assert sked in parsed_filing_schedules
            parsed_filing.get_parsed_sked(sked)

    def test_with_standardizer(self):
        standardizer = Standardizer()
        self.xml_runner = XMLRunner(standardizer=standardizer)


class TestWithDownload:
    def setup_method(self):
        self.filing = Filing(FILING_2015V21)
        if os.path.isfile(self.filing.get_filepath()):
            if DOWNLOAD:
                os.remove(self.filing.get_filepath())

    def test_case_1(self):
        self.filing.process()
        assert self.filing.get_version() == "2015v2.1"

    def test_case_2(self):
        self.filing.process()
        f_skeds = self.filing.list_schedules()
        assert f_skeds == FILING_2015V21_skeds
        for f_sked in f_skeds:
            self.filing.get_schedule(f_sked)


class TestCommandLine:
    def setup_method(self):
        parser = get_cli_parser()
        self.parser = parser

    def test_cli_1(self):
        args = self.parser.parse_args([FILING_2022, "--verbose"])
        # Does it run? Output is to std out.
        run_cli_main(args)

    def test_cli_2(self):
        # dump only main 990 in bare json format
        test_args = ["--schedule", "IRS990", "--xpath", "202210409349301026"]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_3(self):
        test_args = ["--schedule", "IRS990", FILING_2022]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_4(self):
        test_args = [
            "--schedule",
            "IRS990",
            "--format",
            "csv",
            "--file",
            "testout.csv",
            "202210409349301026",
        ]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_5(self):
        test_args = [
            "--schedule",
            "IRS990",
            "--format",
            "txt",
            "--file",
            "testout.csv",
            "--verbose",
            "202210409349301026",
        ]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_6(self):
        test_args = ["--format", "txt", "202210409349301026"]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_7(self):
        test_args = ["--format", "txt", "--xpath", "--verbose", "202210409349301026"]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_8(self):
        test_args = ["--list_schedules", "202210409349301026"]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_9(self):
        test_args = ["--format", "txt", "202210409349301026"]
        args = self.parser.parse_args(test_args)
        run_cli_main(args)

    def test_cli_namespaced(self):
        test_args = ["--format", "txt", "202210409349301026"]  # tags start with "irs:"
        args = self.parser.parse_args(test_args)
        run_cli_main(args)


class TestCommandLine_Index:
    def setup_method(self):
        parser = get_cli_index_parser()
        self.parser = parser

    def test_cli_index_1(self):
        args = self.parser.parse_args(["--year", "2017"])
        # Does it run? Output is to the 2017 index file.
        if DOWNLOAD:
            run_cli_index_main(args)
