from datetime import datetime, timezone


class TimeUtils:
    @staticmethod
    def convert_datetime_to_iso8601(date_str, date_format):
        date_obj = datetime.strptime(date_str, date_format)
        date_obj.astimezone(timezone.utc)
        iso_date_str = date_obj.isoformat()
        return iso_date_str
