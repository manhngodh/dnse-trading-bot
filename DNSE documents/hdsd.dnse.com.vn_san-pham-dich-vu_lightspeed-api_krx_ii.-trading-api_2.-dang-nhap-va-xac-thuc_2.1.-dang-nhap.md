---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc/2.1.-dang-nhap"
title: "2.1.  Đăng nhập | ENTRADE X"
---

**URL**

**Method**

[https://api.dnse.com.vn/auth-service/login](https://api.dnse.com.vn/auth-service/login)

POST

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc/2.1.-dang-nhap\#resquest-header)    Resquest header

**Field**

**Type**

**Description**

**N/A**

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc/2.1.-dang-nhap\#resquest-body)    **Resquest body**

**Field**

**Type**

**Description**

**username**

String

ID đăng nhập: email hoặc số điện thoại hoặc số lưu ký

**password**

String

Mật khẩu

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc/2.1.-dang-nhap\#response-body)    Response body

**Field**

**Type**

**Description**

**token**

String

JWT token (có hiệu lực trong 8 tiếng)

cURL

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc/2.1.-dang-nhap#tab-curl)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request POST 'https://services.entrade.com.vn/dnse-auth-service/login' \
--header 'Content-Type: application/json' \
--data '{"username":"<your_email OR your_mobile OR your_custody_code>","password":"<your_password>"}'
```

[Previous2\. Đăng nhập và xác thực](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc) [Next2.2. Xác thực OTP](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc/2.2.-xac-thuc-otp)

Last updated 28 days ago

Was this helpful?