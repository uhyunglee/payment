package uhyunglee.payment;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.math.BigDecimal;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public record ExchangedRateData(String result, Map<String, BigDecimal> rates) {
    // record 는 수정 불가
}
