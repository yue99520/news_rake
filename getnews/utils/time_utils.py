from datetime import datetime, timezone


class TimeUtils:
    @staticmethod
    def convert_datetime_to_iso8601(date_str, date_format):
        date_obj = datetime.strptime(date_str, date_format)
        date_obj = date_obj.astimezone(timezone.utc)
        iso_date_str = date_obj.isoformat(timespec='milliseconds')
        if iso_date_str.endswith('+00:00'):
            iso_date_str = iso_date_str[:-6]
        return f"{iso_date_str}Z"


if __name__ == '__main__':
    iso_date = TimeUtils.convert_datetime_to_iso8601('2024-08-15 14:45 -04:00', "%Y-%m-%d %H:%M %z")
    print(iso_date)
