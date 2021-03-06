# -*- coding: utf-8 -*-
import os
from datetime import datetime
import math
import logging

import pandas as pd
import pytest
import numpy as np

from cwmspy import CWMS


@pytest.fixture(params=[["cms", "UTC"], ["cfs", "US/Pacific"]])
def cwms_data(request):

    cwms = CWMS(verbose=True)
    cwms.connect()
    units, tz = ["cms", "UTC"]
    units, tz = request.param

    alter_session_sql = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'"
    cur = cwms.conn.cursor()
    cur.execute(alter_session_sql)
    cur.close()

    try:
        cwms.delete_location("CWMSPY", "DELETE TS DATA")
        cwms.delete_location("CWMSPY", "DELETE TS ID")
        cwms.delete_location("CWMSPY")
    except:
        pass
    cwms.store_location("CWMSPY")
    p_cwms_ts_id = "CWMSPY.Flow.Inst.0.0.REV"
    p_units = units
    times = [
        x.strftime("%Y/%m/%d")
        for x in pd.date_range(datetime(2016, 12, 31), periods=400)
    ]
    values = [math.sin(x) for x in range(len(times))]

    try:
        cwms.store_ts(
            p_cwms_ts_id=p_cwms_ts_id,
            p_units=p_units,
            times=times,
            values=values,
            qualities=None,
            p_override_prot="T",
            timezone=tz,
        )
    except Exception as e:
        try:
            cwms.delete_location("CWMSPY", "DELETE TS DATA")
            cwms.delete_location("CWMSPY", "DELETE TS ID")
            cwms.delete_location("CWMSPY")
        except:
            pass
        c = cwms.close()
        raise e
    yield cwms, times, values, p_cwms_ts_id, units, tz
    cwms.delete_location("CWMSPY", "DELETE TS DATA")
    cwms.delete_location("CWMSPY", "DELETE TS ID")
    cwms.delete_location("CWMSPY")
    c = cwms.close()


@pytest.fixture()
def cwms():

    cwms = CWMS(verbose=True)
    cwms.connect()

    try:
        cwms.delete_location("CWMSPY", "DELETE TS DATA")
        cwms.delete_location("CWMSPY", "DELETE TS ID")
        cwms.delete_location("CWMSPY")
    except:
        pass
    alter_session_sql = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'"
    cur = cwms.conn.cursor()
    cur.execute(alter_session_sql)
    cur.close()
    cwms.store_location("CWMSPY")
    yield cwms
    # test
    try:
        cwms.delete_location("CWMSPY", "DELETE TS DATA")
        cwms.delete_location("CWMSPY", "DELETE TS ID")
        cwms.delete_location("CWMSPY")
    except:
        pass
    c = cwms.close()


class TestClass(object):
    cwd = os.path.dirname(os.path.realpath(__file__))

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        # https://stackoverflow.com/a/50375022/4296857
        self._caplog = caplog

    def test_successful_get_ts_code(self, cwms_data):
        """
        get_ts_code: Testing successful ts code
        """
        cwms, times, values, p_cwms_ts_id, units, tz = cwms_data
        ts_code_sql = f"""select ts_code 
                        from cwms_20.at_cwms_ts_id
                        where cwms_ts_id = '{p_cwms_ts_id}'"""
        cur = cwms.conn.cursor()
        cur.execute(ts_code_sql)
        ts_code = cur.fetchall()[0][0]
        cur.close()
        cwms_ts_code = cwms.get_ts_code(p_cwms_ts_id)

        assert cwms_ts_code == str(ts_code)

    def test_get_ts_max_date(self, cwms_data):
        cwms, times, values, p_cwms_ts_id, units, tz = cwms_data
        max_date = cwms.get_ts_max_date(
            p_cwms_ts_id="CWMSPY.Flow.Inst.0.0.REV",
            p_time_zone=tz,
            version_date="1111/11/11",
            p_office_id=None,
        )

        assert max_date == datetime.strptime(times[-1], "%Y/%m/%d")

    def test_get_ts_min_date(self, cwms_data):
        cwms, times, values, p_cwms_ts_id, units, tz = cwms_data
        min_date = cwms.get_ts_min_date(
            p_cwms_ts_id, p_time_zone=tz, version_date="1111/11/11", p_office_id=None
        )
        assert min_date == datetime.strptime(times[0], "%Y/%m/%d")

    def test_retrieve_time_series(self, cwms_data):
        cwms, times, values, p_cwms_ts_id, units, tz = cwms_data
        df = cwms.retrieve_time_series(
            [p_cwms_ts_id],
            units=[units],
            p_datums=None,
            p_start="2015-12-01",
            p_end="2020-01-02",
            p_timezone=tz,
            p_office_id=None,
            as_json=False,
        )
        # assert times == list(df["date_time"].values)
        # assert len(list(df["value"].values)) == len(values)
        # assert list(df["value"].values) == values
        assert [x.strftime("%Y/%m/%d") for x in df["date_time"]] == times
        assert [np.round(float(x)) for x in list(df["value"].values)] == [
            np.round(float(x)) for x in values
        ]

    def test_retrieve_ts(self, cwms_data):
        cwms, times, values, p_cwms_ts_id, units, tz = cwms_data
        df = cwms.retrieve_ts(
            p_cwms_ts_id,
            p_units=units,
            start_time="2015-12-01",
            end_time="2020/01/02",
            p_timezone=tz,
            p_office_id=None,
        )
        # assert times == list(df["date_time"].values)
        # assert len(list(df["value"].values)) == len(values)
        # assert list(df["value"].values) == values
        assert [x.strftime("%Y/%m/%d") for x in df["date_time"]] == times
        assert [np.round(float(x)) for x in list(df["value"].values)] == [
            np.round(float(x)) for x in values
        ]

    def test_store_by_df(self, cwms):
        df = pd.read_json("test/data/data.json")
        # units are not in the same order as above and I need them to get the data
        # again for the actual test
        firsts = df.groupby("ts_id").first()["units"]
        units = list(firsts.values)
        paths = list(firsts.index)
        df["date_time"] = pd.to_datetime(df["date_time"])
        p_start = df["date_time"].min().strftime(format="%Y-%m-%d")
        p_end = df["date_time"].max().strftime(format="%Y-%m-%d")
        cwms.store_by_df(df, timezone="UTC")
        new_df = cwms.retrieve_time_series(
            paths,
            units=units,
            p_start=p_start,
            p_end=p_end,
            p_timezone="UTC",
            p_office_id=None,
        )
        grp = new_df.groupby("ts_id")
        for g, v in grp:
            df[df["ts_id"] == g].equals(v)

    def test_store_by_df_no_new_data(self, cwms):
        df = pd.read_json("test/data/data.json")
        cwms.store_by_df(df)
        with self._caplog.at_level(logging.INFO):
            cwms.store_by_df(df)
            assert "No new data to load for" in self._caplog.records[-1].message

    def test_store_by_df_no_new_data_diff_timezone(self, cwms):
        df = pd.read_json("test/data/data.json")
        cwms.store_by_df(df, timezone="UTC")
        df.set_index("date_time", inplace=True)
        df.index = df.index.tz_localize(tz="UTC")
        df.index = df.index.tz_convert(tz="US/Pacific")
        df.reset_index(inplace=True, drop=False)
        df["time_zone"] = "US/Pacific"
        with self._caplog.at_level(logging.INFO):
            cwms.store_by_df(df)
            assert "No new data to load for" in self._caplog.records[-1].message

    def test_store_by_df_protected_data(self, cwms):

        # loading the protected data
        df = pd.read_json("test/data/data.json")
        grp = df.groupby("ts_id")
        df = grp.get_group(df["ts_id"][0]).reset_index(drop=True)
        df["quality_code"] = 2 ** 31 + 5
        cwms.store_by_df(df)

        # changing the data, making it non protected then loading
        # again
        new_df = df.copy()
        new_df["value"] = new_df["value"] + 5
        new_df["quality_code"] = 0
        cwms.store_by_df(new_df)

        # retrieving the data from the database to make sure it
        # is still the original protected data
        ts_id = df["ts_id"][0]
        units = df["units"][0]
        tz = df["time_zone"][0]
        start_time = df[["date_time"]].min()[0]
        end_time = df[["date_time"]].max()[0]
        retrieved_df = cwms.retrieve_ts(
            ts_id,
            p_units=units,
            start_time=start_time,
            end_time=end_time,
            p_timezone=tz,
            p_office_id=None,
        )

        assert (
            retrieved_df.sort_values("date_time")[["value"]]
            .dropna()
            .reset_index(drop=True)
            .equals(
                df.sort_values("date_time")[["value"]].dropna().reset_index(drop=True)
            )
        )

    def test_delete_by_df(self, cwms):
        df = pd.read_json("test/data/data.json")
        df = df.head(n=100).copy()
        cwms.store_by_df(df)
        ts_id = df["ts_id"].values[0]
        start = df["date_time"].min()
        end = df["date_time"].max()
        units = df["units"].values[0]
        cwms.delete_by_df(df.iloc[[1, 5, 10], :])
        dropped_df = df.drop([1, 5, 10]).copy().reset_index(drop=True).dropna()
        retrieved_df = (
            cwms.retrieve_time_series([ts_id], units=[units], p_start=start, p_end=end)
            .dropna()
            .reset_index(drop=True)
        )
        assert dropped_df[["value"]].equals(retrieved_df[["value"]])

