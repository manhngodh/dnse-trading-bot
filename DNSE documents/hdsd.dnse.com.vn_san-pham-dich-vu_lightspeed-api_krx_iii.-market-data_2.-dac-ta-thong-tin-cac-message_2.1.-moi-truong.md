---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/iii.-market-data/2.-dac-ta-thong-tin-cac-message/2.1.-moi-truong"
title: "2.1. Môi trường | ENTRADE X"
---

Với các topic public không cần authentication:

**Host**

datafeed-lts-krx.dnse.com.vn

**Port**

443

**Path**

/wss

**ClientID**

<dnse-price-json-mqtt-ws-sub>-<username>-<random\_sequence>

**Username**

Lấy từ trường investorId trong phần 2.1.b

**Password**

Lấy từ trường token trong phần 2.1.a

## [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/iii.-market-data/2.-dac-ta-thong-tin-cac-message/2.1.-moi-truong\#a.-dang-nhap)    a. Đăng nhập

URL

METHOD

[https://api.dnse.com.vn/user-service/api/auth](https://api.dnse.com.vn/user-service/api/auth)

POST

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/iii.-market-data/2.-dac-ta-thong-tin-cac-message/2.1.-moi-truong\#resquest-header)    **Resquest Header**

Field

Type

Description

N/A

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/iii.-market-data/2.-dac-ta-thong-tin-cac-message/2.1.-moi-truong\#resquest-body)    **Resquest Body**

Field

Type

Description

username

String

ID đăng nhập: Email hoặc Số điện thoại hoặc Số lưu ký

password

String

Mật khẩu

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/iii.-market-data/2.-dac-ta-thong-tin-cac-message/2.1.-moi-truong\#response-body)    **Response Body**

Field

Type

Description

token

String

JWT token (có hiệu lực trong 8 tiếng

## [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/iii.-market-data/2.-dac-ta-thong-tin-cac-message/2.1.-moi-truong\#b.-thong-tin-tai-khoan)    **b. Thông tin tài khoản**

URL

METHOD

[https://api.dnse.com.vn/user-service/api/me](https://api.dnse.com.vn/user-service/api/me)

GET

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/iii.-market-data/2.-dac-ta-thong-tin-cac-message/2.1.-moi-truong\#request-header)    **Request Header**

Field

Type

Description

Authorization

Bearer Bearer <JWT token>

Bearer <JWT token> -> lấy JWT token từ mục 2.1.a

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/iii.-market-data/2.-dac-ta-thong-tin-cac-message/2.1.-moi-truong\#request-body)    **Request Body**

Field

Type

Description

N/A

OK

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/iii.-market-data/2.-dac-ta-thong-tin-cac-message/2.1.-moi-truong\#response-body-1)    **Response** B **ody**

Field

Type

Description

investorId

String

Mã khách hàng

name

String

Họ và tên

custodyCode

String

Số lưu ký

mobile

String

Số điện thoại

email

String

Email

<others>

[Previous2\. Đặc tả thông tin các message](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/iii.-market-data/2.-dac-ta-thong-tin-cac-message) [Next2.2. KRX Topics](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/iii.-market-data/2.-dac-ta-thong-tin-cac-message/2.2.-krx-topics)

Last updated 28 days ago

Was this helpful?