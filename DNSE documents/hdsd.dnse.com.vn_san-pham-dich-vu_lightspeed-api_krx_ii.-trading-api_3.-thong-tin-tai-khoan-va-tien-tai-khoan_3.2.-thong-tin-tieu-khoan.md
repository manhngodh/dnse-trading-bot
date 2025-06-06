---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.2.-thong-tin-tieu-khoan"
title: "3.2.  Thông tin tiểu khoản | ENTRADE X"
---

_**Lấy danh sách tiểu khoản giao dịch**_

**URL**

**Method**

[https://api.dnse.com.vn/order-service/accounts](https://api.dnse.com.vn/order-service/accounts)

GET

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.2.-thong-tin-tieu-khoan\#resquest-header)    **Resquest header**

**Field**

**Type**

**Description**

**Authorization**

Bearer <JWT token>

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.2.-thong-tin-tieu-khoan\#resquest-body)    **Resquest body**

**Field**

**Type**

**Description**

**N/A**

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.2.-thong-tin-tieu-khoan\#response-body)    **Response body**

**Field**

**Type**

**Description**

**accounts**

Account list

Danh sách các tiểu khoản

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.2.-thong-tin-tieu-khoan\#account)    **Account**

**Field**

**Type**

**Description**

**id**

String

Mã tiểu khoản

**custodyCode**

String

Số lưu ký

**investorId**

String

Mã khách hàng

**accountTypeName**

String

Tên tiểu khoản

**derivativeAccount**

Bolean

Đã đăng ký giao dịch phái sinh chưa?

**<others>**

cURL

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.2.-thong-tin-tieu-khoan#tab-curl)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request GET 'https://api.dnse.com.vn/order-service/accounts' \
--header 'Content-Type: application/json' \
--header 'authorization: Bearer <jwt_token_from_login_API_response_step_2.1>'
```

[Previous3.1. Thông tin tài khoản](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.1.-thong-tin-tai-khoan) [Next3.3. Thông tin tiền](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.3.-thong-tin-tien)

Last updated 28 days ago

Was this helpful?