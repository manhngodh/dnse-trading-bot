---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.3.-thong-tin-tien"
title: "3.3.  Thông tin tiền | ENTRADE X"
---

_**Lấy thông tin tài sản tiền theo mã tiểu khoản**_

**URL**

**Method**

[https://api.dnse.com.vn/order-service/account-balances/<account>](https://services.entrade.com.vn/dnse-order-service/account-balances/%3Caccount%3E)

GET

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.3.-thong-tin-tien\#path-param)    **Path param**

**Field**

**Type**

**Description**

**account**

Mã tiểu khoản <account> lấy ở bước 3.2

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.3.-thong-tin-tien\#resquest-header)    **Resquest header**

**Field**

**Type**

**Description**

**Authorization**

Bearer <JWT token>

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.3.-thong-tin-tien\#resquest-body)    **Resquest body**

**Field**

**Type**

**Description**

**N/A**

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.3.-thong-tin-tien\#response-body)    **Response body**

**Field**

**Type**

**Description**

**custodyCode**

String

Số lưu ký

**investorAccountId**

String

Mã tiểu khoản, bằng giá trị <account> truyền lên

**totalCash**

Double

Tổng tiền hiện có

**availableCash**

Double

Tiền mặt hiện có đã trừ đi các khoản nợ + phí

**totalDebt**

Double

Tổng nợ

**withdrawableCash**

Double

Số tiền được rút

**depositFeeAmount**

Double

Phí lưu ký

**depositInterest**

Double

Lãi tiền gửi không ký hạn

**marginDebt**

Double

Nợ margin

**stockValue**

Double

Giá trị chứng khoán tính theo giá đầu ngày

**netAssetValue**

Double

Tài sản ròng

**receivingAmount**

Double

Tiền chờ về

**secureAmount**

Double

Tiền mua khớp trong ngày

**withdrawableCash**

Double

Số tiền có thể rút

**cashDividendReceiving**

Double

Tiền cổ tức chờ về

cURL

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.3.-thong-tin-tien#tab-curl)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request GET 'https://api.dnse.com.vn/order-service/account-balances/<account>' \
--header 'Content-Type: application/json' \
--header 'authorization: Bearer <jwt_token_from_login_API_response_step_2.1>'
```

[Previous3.2. Thông tin tiểu khoản](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.2.-thong-tin-tieu-khoan) [Next4\. Giao dịch cơ sở](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so)

Last updated 28 days ago

Was this helpful?