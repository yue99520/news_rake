from datetime import datetime, timezone


class TimeUtils:
    @staticmethod
    def convert_datetime_to_iso8601(date_str, date_format):
        date_obj = datetime.strptime(date_str, date_format)
        date_obj.astimezone(timezone.utc)
        iso_date_str = date_obj.isoformat(timespec='milliseconds')
        return iso_date_str + 'Z'


if __name__ == '__main__':
    date_str = "2024-08-26 15:00:00"
    date_format = "%Y-%m-%d %H:%M:%S"
    iso_date = TimeUtils.convert_datetime_to_iso8601(date_str, date_format)
    print(iso_date)