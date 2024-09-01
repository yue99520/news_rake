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
    
    @staticmethod
    def convert_unixtime_to_iso8601(unix_timestamp):
        # 將 Unix timestamp 轉換為 datetime 物件
        date_obj = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
        
        # 格式化為 ISO 8601 並處理時區
        iso_date_str = date_obj.isoformat(timespec='milliseconds')
        if iso_date_str.endswith('+00:00'):
            iso_date_str = iso_date_str[:-6]
        
        return f"{iso_date_str}Z"


if __name__ == '__main__':
    iso_date = TimeUtils.convert_datetime_to_iso8601('2024-08-30 11:18 -04:00', "%Y-%m-%d %H:%M %z")
    iso_date_a = TimeUtils.convert_datetime_to_iso8601('2024-08-16 04:49 -04:00', "%Y-%m-%d %H:%M %z")
    iso_date_b = TimeUtils.convert_unixtime_to_iso8601(1725212557)
    print(iso_date)
    print(iso_date_a)
    print(iso_date_b)
    print(datetime.fromisoformat(iso_date) >= datetime.fromisoformat(iso_date_a))
