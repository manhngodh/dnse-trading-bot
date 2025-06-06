---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.1.-thong-tin-tai-khoan"
title: "3.1.\t Thông tin tài khoản | ENTRADE X"
---

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.1.-thong-tin-tai-khoan\#resquest-header)    **Resquest header**

**Field**

**Type**

**Description**

**Authorization**

Bearer <JWT token>

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.1.-thong-tin-tai-khoan\#resquest-body)    **Resquest body**

**Field**

**Type**

**Description**

**N/A**

OK

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.1.-thong-tin-tai-khoan\#response-body)    **Response body**

**Field**

**Type**

**Description**

**investorId**

String

Mã khách hàng

**name**

String

Họ và tên

**custodyCode**

String

Số lưu ký

**mobile**

String

Số điện thoại

**email**

String

Email

**<others>**

cURL

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.1.-thong-tin-tai-khoan#tab-curl)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request GET 'https://api.dnse.com.vn/user-service/api/me' \
--header 'Content-Type: application/json' \
--header 'authorization: Bearer <jwt_token_from_login_API_response_step_2.1>'
```

[Previous3\. Thông tin tài khoản và tiền tài khoản](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan) [Next3.2. Thông tin tiểu khoản](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan/3.2.-thong-tin-tieu-khoan)

Last updated 1 month ago

Was this helpful?