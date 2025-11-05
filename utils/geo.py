import re

# 위도/경도가 유효 범위 내에 있는지 검사
def is_valid_coordinate(lat, lon):
    try:
        lat, lon = float(lat), float(lon)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except ValueError:
        return False
    
    
# 좌표 문자열에서 공백이나 특수문자 제거
def clean_coordinate_format(coord):
    return re.sub(r"[^\d\.\-]", "", coord)