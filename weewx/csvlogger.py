# WeeWX CSV archive logger for WeeWX 5.x
# Writes one CSV row for each NEW_ARCHIVE_RECORD event.
# Values are expected to already be in METRICWX because StdConvert is set to METRICWX.

import csv
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import weewx
import weewx.engine
import logging


class CSVLogger(weewx.engine.StdService):
    """Append WeeWX archive records to monthly CSV files."""

    log = logging.getLogger("user.csvlogger")

    fields = (
        "dateTime",
        "dateTimeISO",
        "interval",
        "usUnits",
        "outTemp",
        "outHumidity",
        "dewpoint",
        "heatindex",
        "windchill",
        "windSpeed",
        "windGust",
        "windDir",
        "windGustDir",
        "windrun",
        "rain",
        "rainRate",
        "radiation",
        "UV",
    )

    headers = (
        "dateTime",
        "dateTimeISO",
        "interval",
        "units",
        "outTemp_C",
        "outHumidity_pct",
        "dewpoint_C",
        "heatindex_C",
        "windchill_C",
        "windSpeed_m_per_s",
        "windGust_m_per_s",
        "windDir_deg",
        "windGustDir_deg",
        "windrun_km",
        "rain_mm",
        "rainRate_mm_per_h",
        "radiation_W_per_m2",
        "UV_index",
    )

    def __init__(self, engine, config_dict):
        super().__init__(engine, config_dict)

        cfg = config_dict.get("CSVLogger", {})
        self.template = cfg.get(
            "filename", "/var/lib/weewx/csv/weather-{year}-{month}.csv"
        )
        self.timezone_name = cfg.get("timezone", "Europe/London")
        self.timezone = ZoneInfo(self.timezone_name)
        self.decimals = int(cfg.get("decimals", 3))

        self.file = None
        self.writer = None
        self.current_filename = None

        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        self.bind(weewx.SHUTDOWN, self.shut_down)

        # Open the current month's file when the service starts.
        now = datetime.now(self.timezone)
        self._open_for_month(now.year, now.month)

    def _filename_for(self, year, month):
        return self.template.format(year=year, month=f"{month:02d}")

    def _open_for_month(self, year, month):
        filename = self._filename_for(year, month)

        if filename == self.current_filename and self.file is not None:
            return

        self._close_file()

        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        exists_and_nonempty = os.path.exists(filename) and os.path.getsize(filename) > 0

        self.file = open(filename, "a", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file)

        if not exists_and_nonempty:
            self.writer.writerow(self.headers)
            self.file.flush()

        self.current_filename = filename
        self.log.info("writing archive records to %s", filename)

    def _close_file(self):
        if self.file is not None:
            try:
                self.file.flush()
            finally:
                self.file.close()

        self.file = None
        self.writer = None
        self.current_filename = None

    def _format_value(self, field, value):
        if value is None:
            return ""

        if field in ("dateTime", "dateTimeISO", "usUnits"):
            return value

        if field == "interval":
            try:
                return int(round(float(value)))
            except (TypeError, ValueError):
                return ""

        try:
            return round(float(value), self.decimals)
        except (TypeError, ValueError):
            return ""

    def new_archive_record(self, event):
        record = event.record
        timestamp = record.get("dateTime")
        if timestamp is None:
            return

        dt = datetime.fromtimestamp(float(timestamp), tz=self.timezone)
        self._open_for_month(dt.year, dt.month)

        row = []
        for field in self.fields:
            if field == "dateTimeISO":
                row.append(dt.isoformat(timespec="seconds"))
            else:
                row.append(self._format_value(field, record.get(field)))

        self.writer.writerow(row)
        self.file.flush()

    def shut_down(self, event):
        self._close_file()
