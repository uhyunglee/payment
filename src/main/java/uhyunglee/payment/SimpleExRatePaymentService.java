package uhyunglee.payment;

import java.io.IOException;
import java.math.BigDecimal;

public class SimpleExRatePaymentService extends PaymentService{
    @Override
    BigDecimal getExchangeRate(String currency) throws IOException {
        if(currency.equals("USD")) return BigDecimal.valueOf(1000);

        throw new IllegalArgumentException("Not provided");
    }
}
