# 실행 결과
이 문서는 로컬 실행 재현 결과를 기록하기 위한 문서입니다.

결과값은 `result/`에 저장되어 있습니다. [결과값 보러가기](result/)

아래 예시는 sample_01.json의 결과 값입니다.

## 1) JSON 결과 예시 

```json
{
  "source_file": "data/sample_01.json",
  "stage1": {
    "measured_date": "2026-02-02",
    "vehicle_no": "8713",
    "issuer_name": "",
    "customer_name": "곰욕환경폐기물",
    "item_name": "",
    "io_type": "",
    "ticket_id": "",
    "measure_count": "",
    "issuer_address": "",
    "issuer_tel": "",
    "issuer_fax": "",
    "gross_kg": "",
    "gross_time": "",
    "tare_kg": "",
    "tare_time": "",
    "net_kg": 5010,
    "net_time": "",
    "gps_lat": "",
    "gps_lon": "",
    "warnings": []
  },
  "stage2": {
    "measured_date": "2026-02-02",
    "vehicle_no": "8713",
    "issuer_name": "동우바이오(주)",
    "customer_name": "곰욕환경폐기물",
    "item_name": "",
    "io_type": "",
    "ticket_id": "",
    "measure_count": "",
    "issuer_address": "",
    "issuer_tel": "",
    "issuer_fax": "",
    "gross_kg": 12480,
    "gross_time": "05:26:18",
    "tare_kg": 7470,
    "tare_time": "05:36:01",
    "net_kg": 5010,
    "net_time": "",
    "gps_lat": 37.105317,
    "gps_lon": 127.375673,
    "warnings": [
      "ISSUER_FROM_SCORE:COMPANY_CANDIDATE_SMELL",
      "COMPANY_CANDIDATE_COUNT:2",
      "COMPANY_TOP_ISSUER:COMPANY_CANDIDATE_SMELL:5",
      "COMPANY_TOP_COUNTERPARTY:COMPANY_CANDIDATE_LABEL:5"
    ]
  }
}
```

## 2) CSV 결과 예시
sample_01_parsed.csv
``` csv
field,stage1_value,stage2_value
measured_date,2026-02-02,2026-02-02
vehicle_no,8713,8713
issuer_name,,동우바이오(주)
customer_name,곰욕환경폐기물,곰욕환경폐기물
item_name,,
io_type,,
ticket_id,,
measure_count,,
issuer_address,,
issuer_tel,,
issuer_fax,,
gross_kg,,12480
gross_time,,05:26:18
tare_kg,,7470
tare_time,,05:36:01
net_kg,5010,5010
net_time,,
gps_lat,,37.105317
gps_lon,,127.375673
warnings,[],"['ISSUER_FROM_SCORE:COMPANY_CANDIDATE_SMELL', 'COMPANY_CANDIDATE_COUNT:2', 'COMPANY_TOP_ISSUER:COMPANY_CANDIDATE_SMELL:5', 'COMPANY_TOP_COUNTERPARTY:COMPANY_CANDIDATE_LABEL:5']"
```

## 3) 터미널 실행 결과
``` plaintext
== data/sample_01.json ==
[📌 원본]
계 량 증 명 서
계량일자: 2026-02-02 0016
차량번호: 8713
거 래 처: 곰욕환경폐기물
품종명랑 05:26:18 12,480 kg
명:
중 량:
05:36:01 7,470 kg
실 중 량: 5,010 kg
* 위와 같이 계량하였음을 확인함.
동우바이오(주)
2026-02-02 05:37:55
37.105317, 127.375673
[파싱-1단계]
measured_date: 2026-02-02
vehicle_no: 8713
issuer_name: 
customer_name: 곰욕환경폐기물
item_name: 
io_type: 
ticket_id: 
measure_count: 
issuer_address: 
issuer_tel: 
issuer_fax: 
gross_kg: 
gross_time: 
tare_kg: 
tare_time: 
net_kg: 5010
net_time: 
gps_lat: 
gps_lon: 
warnings: []
[파싱-2단계]
measured_date: 2026-02-02
vehicle_no: 8713
issuer_name: 동우바이오(주) [2단계 보강]
customer_name: 곰욕환경폐기물
item_name: 
io_type: 
ticket_id: 
measure_count: 
issuer_address: 
issuer_tel: 
issuer_fax: 
gross_kg: 12480 [2단계 보강]
gross_time: 05:26:18 [2단계 보강]
tare_kg: 7470 [2단계 보강]
tare_time: 05:36:01 [2단계 보강]
net_kg: 5010
net_time: 
gps_lat: 37.105317 [2단계 보강]
gps_lon: 127.375673 [2단계 보강]
warnings: ['ISSUER_FROM_SCORE:COMPANY_CANDIDATE_SMELL', 'COMPANY_CANDIDATE_COUNT:2', 'COMPANY_TOP_ISSUER:COMPANY_CANDIDATE_SMELL:5', 'COMPANY_TOP_COUNTERPARTY:COMPANY_CANDIDATE_LABEL:5']
[결과파일]
json: result/sample_01_parsed.json
csv: result/sample_01_parsed.csv