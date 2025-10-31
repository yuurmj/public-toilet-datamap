# 남구 공중화장실 데이터 사전 (Data Dictionary)

- **프로젝트**: PUBLIC-TOILET-DATAMAP  
- **문서 위치**: `docs/data_dictionary.md`  
- **스키마 파일**: `schema/dong_schema.json`  
- **마지막 갱신일**: 2025-10-29  
- **버전**: 1.0.0  
- **담당**: 정유림 (데이터 정의/전처리), 서희원 (QA/Export), 정아란 (집계/리포트)

---

## 1) 데이터셋 개요

본 프로젝트는 부산광역시 **남구**의 공중화장실 데이터를 수집·정제하여 **행정동 단위**로 표준화/집계합니다.  
데이터는 3단계로 관리됩니다.

- `data/raw/` : 원본 수준 데이터 (예: `toilets_namgu_cleaned.csv`)
- `data/processed/` : 전처리/정규화/집계 결과 (예: `toilets_namgu_normalized.csv`, `by_dong.csv`)
- `data/ref/` : 참고 데이터 (인구·면적 등)

---

## 2) 파일 목록

| 파일 | 설명 | 주요 키 |
|---|---|---|
| `data/raw/toilets_namgu_cleaned.csv` | 시설(레코드) 단위 원천 데이터(정리본) | `toilet_id` |
| `data/processed/toilets_namgu_normalized.csv` | 동명 정규화, 행정동 코드 부여 등 전처리 결과 | `toilet_id` |
| `data/processed/by_dong.csv` | **행정동 단위 집계 데이터** (대시보드/ML 입력) | `admin_dong` |

---

## 3) 공통 용어

- **법정동(legal_dong)**: 대연동·용호동·문현동·감만동·우암동·용당동 (6개)  
- **행정동(admin_dong)**:  
  대연1·3·4·5·6동, 용호1·2·3·4동, 문현1·2·3·4동, 감만1·2동, 우암동, 용당동 (총 17개)  
- **행정동 내부코드(admin_dong_code)**: 예) `NG-DY4` (남구-대연4동)

---

## 4) 원본(정리본) 컬럼 정의 — `toilets_namgu_cleaned.csv`

| 컬럼 | 타입 | 설명 | 예시 |
|---|---|---|---|
| `toilet_id` | string | 시설 식별자(프로젝트 내부) | `NMG-0123` |
| `name` | string | 시설명 | `부산문화회관 대극장` |
| `addr` | string | 지번/도로명 주소 | `유엔평화로 76번길 1` |
| `lat` | float | 위도 | `35.129561` |
| `lon` | float | 경도 | `129.094086` |
| `male_wc` | int | 남자 대·소변기 합계(원천 표기 기준) | `9` |
| `female_wc` | int | 여자 변기 수 | `6` |
| `male_wc_disabled` | int | 장애인용 남자 변기 수 | `2` |
| `female_wc_disabled` | int | 장애인용 여자 변기 수 | `1` |
| `accessible` | bool | 장애인 화장실 유무 | `True/False` |
| `district` | string | 구/군 | `남구` |
| `dong` | string | **원천 동 표기(비표준 가능)** | `대연동` |
| `disabled_ratio` | float | 장애인 화장실 비율(원자료 기준) | `0.143` |

---

## 5) 전처리 결과 컬럼 — `toilets_namgu_normalized.csv`

| 컬럼 | 타입 | 설명 |
|---|---|---|
| (원본 컬럼들…) |  | 원자료 컬럼 유지 |
| `city` | string | `부산광역시` 고정 |
| `district` | string | 공백/누락 시 `남구`로 보정 |
| `legal_dong` | string | **법정동 표준화** (6개 enum) |
| `admin_dong` | string | **행정동 표준화** (17개 enum) — 주소/이름에서 추출, 단일동(우암/용당)은 fallback |
| `admin_dong_code` | string | 내부 코드 (예: `NG-DY4`) |
| `disabled_wc_total` | int | `male_wc_disabled + female_wc_disabled` |
| `geo_valid_flag` *(선택)* | bool | 부산 근사 범위 좌표 여부(간단 검증) |

---

## 6) 집계 결과 컬럼 — `by_dong.csv`  (**JSON 스키마: `schema/dong_schema.json`**)

| 필드 | 타입 | 필수 | 설명 | 예시 |
|---|---:|:---:|---|---|
| `city` | string | ✅ | 광역시/도(고정) | 부산광역시 |
| `district` | string | ✅ | 구/군(고정) | 남구 |
| `legal_dong` | string | ✅ | 법정동(6개) | 대연동 |
| `admin_dong` | string | ✅ | 행정동(17개) | 대연4동 |
| `admin_dong_code` | string |  | 내부코드 | NG-DY4 |
| `centroid_lat` | number | ✅ | 동 중심 위도 | 35.1312 |
| `centroid_lng` | number | ✅ | 동 중심 경도 | 129.1015 |
| `area_km2` | number | ✅ | 면적(km²) — `ref`에서 취득 | 1.82 |
| `population` | integer | ✅ | 인구(명) — `ref`에서 취득 | 18450 |
| `floating_population` | integer/null |  | 유동인구(선택) | null |
| `toilets_total` | integer | ✅ | 시설 개수 | 12 |
| `toilets_accessible` | integer | ✅ | 장애인 화장실 보유 시설 수 | 7 |
| `male_urinals_total` | integer | ✅ | 남자 소변기 총합 | 38 |
| `male_toilets_total` | integer | ✅ | 남자 대변기 총합 | 24 |
| `female_toilets_total` | integer | ✅ | 여자 변기 총합 | 32 |
| `open_24h_count` | integer |  | 24시간 개방 개소 | 2 |
| `baby_table_count` | integer |  | 기저귀 교환대 비치 개소 | 3 |
| `toilets_per_10k` | number | ✅ | 인구 1만 명당 화장실 수 | 6.5 |
| `toilets_density_per_km2` | number | ✅ | 면적 1km²당 화장실 수 | 6.59 |
| `accessible_ratio` | number(0~1) | ✅ | `toilets_accessible / toilets_total` | 0.58 |
| `gap_score` | number/null |  | 부족도 지표(선택) | -0.41 |
| `updated_at` | string(date) | ✅ | 갱신일(YYYY-MM-DD) | 2025-10-29 |
| `source` | string |  | 데이터 출처 | data.go.kr |
| `version` | string(semver) | ✅ | 스키마/데이터 버전 | 1.0.0 |
| `notes` | string |  | 비고(최대 500자) | 초기 산출값 |

---

## 7) 허용 값 목록 (Enums)

- **법정동(`legal_dong`)**:  
  `대연동`, `용호동`, `문현동`, `감만동`, `우암동`, `용당동`

- **행정동(`admin_dong`)**:  
  `대연1동`, `대연3동`, `대연4동`, `대연5동`, `대연6동`,  
  `용호1동`, `용호2동`, `용호3동`, `용호4동`,  
  `문현1동`, `문현2동`, `문현3동`, `문현4동`,  
  `감만1동`, `감만2동`, `우암동`, `용당동`

---

## 8) 품질 관리(QA) 체크리스트

- 좌표 범위: 34.0 ≤ `lat` ≤ 36.5, 127.0 ≤ `lon` ≤ 131.0  
- 동 매핑: `legal_dong`/`admin_dong`이 공란이면 미매핑 리포트 기록  
- 타입 검증: `schema/dong_schema.json`으로 `by_dong.csv` 검증  
- 중복 제거: `toilet_id` 중복 불가  
- 결측치 처리: 카운트형 필드는 0 이상, 비율형은 0~1 범위

---

## 9) 파이프라인 연결

1. **정규화**: `scripts/normalize_dong_names.py`  
2. **검증/중복/좌표**: `scripts/validate_coordinates.py`, `scripts/dedupe_records.py`  
3. **참고데이터 결합**: `scripts/join_population_area.py`  
4. **집계**: `scripts/aggregate_by_dong.py` → `data/processed/by_dong.csv`  
5. **Export**: `scripts/export_for_app.py` (대시보드/ML 입력 포맷)

---

## 10) 예시 레코드

```json
{
  "city": "부산광역시",
  "district": "남구",
  "legal_dong": "대연동",
  "admin_dong": "대연4동",
  "admin_dong_code": "NG-DY4",
  "centroid_lat": 35.1312,
  "centroid_lng": 129.1015,
  "area_km2": 1.82,
  "population": 18450,
  "toilets_total": 12,
  "toilets_accessible": 7,
  "toilets_per_10k": 6.5,
  "toilets_density_per_km2": 6.59,
  "accessible_ratio": 0.58,
  "updated_at": "2025-10-29",
  "version": "1.0.0"
}