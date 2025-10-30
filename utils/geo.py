import re

def is_valid_coordinate(lat, lon):
    # 위도/경도가 유효 범위 내에 있는지 검사
    try:
        lat, lon = float(lat), float(lon)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except ValueError:
        return False