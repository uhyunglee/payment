# 요구사항
- 해외직구를 위한 원화 결제 준비 기능 개발
- 주문번호, 외국 통화 종류, 외국 통화 기준 결제 금액을 전달 받아서 다음의 정보를 더해 Payment를 생성한다.
  - 적용 환율
  - 원화 환산 금액
  - 원화 환산 금액 유효시간
- PaymentService.prepare() 메서드로 개발
  - Payment 오브젝트 리턴

# 환율 가져오기
- https://open.er-api.com/v6/latest/{기준통화} 이용
- JSON 포맷으로 리턴되는 값을 분석해서 원화(KRW) 환율 값을 가져온다.
- JSON을 자바 오브젝트로 변환
  - Jackson 프로젝트의 ObjectMapper 사용
