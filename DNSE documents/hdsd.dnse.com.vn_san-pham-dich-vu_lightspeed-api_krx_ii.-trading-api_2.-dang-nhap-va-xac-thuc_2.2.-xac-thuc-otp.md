---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc/2.2.-xac-thuc-otp"
title: "2.2.  Xác thực OTP | ENTRADE X"
---

DNSE cung cấp 2 phương thức để xác thực OTP cho giao dịch qua API, có thể sử dụng một trong 2 phương thức này để xác thực:

- Xác thực bằng smart OTP

- Xác thực bằng email OTP


## [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc/2.2.-xac-thuc-otp\#i.-xac-thuc-bang-smart-otp)    i. Xác thực bằng smart OTP

Để sử dụng tính năng xác thực OTP, tài khoản cần đăng ký sử dụng Smart OTP trên ứng dụng DNSE. [Hướng dẫn cài đặt Smart OTP](https://hdsd.dnse.com.vn/giao-dien/man-hinh-menu/kich-hoat-smart-otp)

- Sau khi xác thực OTP thành công, hệ thống sẽ cấp trading-token

- Trading token sẽ được sử dụng trong các API chỉnh sửa dữ liệu: đặt lệnh, huỷ lệnh

- Trading token sẽ có hiệu lực trong vòng 8h, khi hết hiệu lực cần dùng API này để xác thực và lấy lại trading-token mới.


**URL**

**Method**

[https://api.dnse.com.vn/order-service/trading-token](https://api.dnse.com.vn/order-service/trading-token)

POST

**Resquest header**

**Field**

**Type**

**Description**

**Authorization**

Bearer <JWT token>

**smart-otp**

String

Mã smart otp lấy từ ứng dụng Entrade X

**Resquest body**

**Field**

**Type**

**Description**

**N/A**

**Response body**

**Field**

**Type**

**Description**

**tradingToken**

String

Trading token (có hiệu lực trong 8 tiếng)

cURL

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc/2.2.-xac-thuc-otp#tab-curl)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request POST 'https://services.entrade.com.vn/dnse-order-service/trading-token' \
--header 'Authorization: Bearer <jwt_token_from_login_API_response_step_2.1>' \
--header 'Content-Type: application/json' \
--header 'smart-otp: <smart_otp_from_EntradeX_mobile_app>' \
--data ''
```

## [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc/2.2.-xac-thuc-otp\#xac_thuc_bang)    ii. Xác thực bằng email OTP

Để sử dụng tính năng xác thực bằng email OTP, cần thực hiện 3 bước như sau:

**Bước 1: Đăng ký**

Khách hàng có thể thực hiện đăng ký online trực tiếp trên trang Web EntradeX hoặc liên hệ DNSE theo hướng dẫn: [Hướng dẫn đăng ký](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api/i.-huong-dan-dang-ky).

**Bước 2: Lấy OTP bằng email**

Sau khi đăng ký thành công, Khách hàng có thể sử dụng API lấy OTP bằng email.

- Khi dùng API Email OTP thì mã OTP sẽ được gửi tới địa chỉ email đăng ký khi tạo tại khoản trên Entrade X. [Hướng dẫn xem email hiện tại](https://hdsd.dnse.com.vn/giao-dien/man-hinh-menu/thong-tin-tai-khoan) (Lưu ý: Email cần được xác thực trước khi dùng API)

- Mã OTP sẽ có hiệu lực trong vòng 2 phút và chỉ dùng được 1 lần, khi dùng xong hoặc hết hiệu lực thì cần dùng API này để lấy mã mới


**URL**

**Method**

[https://api.dnse.com.vn/auth-service/api/email-otp](https://api.dnse.com.vn/auth-service/api/email-otp)

GET

**Resquest header**

**Field**

**Type**

**Description**

**Authorization**

Bearer <JWT token>

**Resquest body**

**Field**

**Type**

**Description**

**N/A**

**Response body**

**Field**

**Type**

**Description**

**N/A**

cURL

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc/2.2.-xac-thuc-otp#tab-curl-1)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request GET 'https://services.entrade.com.vn/dnse-auth-service/api/email-otp' \
--header 'Authorization: Bearer <jwt_token_from_login_API_response_step_2.1>' \
--header 'Content-Type: application/json'
```

**Bước 3: Xác thực OTP**

Sau khi tài khoản lấy được mã OTP bằng email thì có thể xác thực OTP để hệ thống cấp trading-token.

- Trading token sẽ được sử dụng trong các API chỉnh sửa dữ liệu: đặt lệnh, huỷ lệnh

- Trading token sẽ có hiệu lực trong vòng 8h, khi hết hiệu lực cần dùng API này để xác thực và lấy lại trading-token mới


**URL**

**Method**

[https://api.dnse.com.vn/order-service/trading-token](https://api.dnse.com.vn/order-service/trading-token)

POST

**Resquest header**

**Field**

**Type**

**Description**

**Authorization**

Bearer <JWT token>

**otp**

String

Mã otp lấy từ API Email OTP (Bước 2)

**Resquest body**

**Field**

**Type**

**Description**

**N/A**

**Response body**

**Field**

**Type**

**Description**

**tradingToken**

String

Trading token (có hiệu lực trong 8 tiếng)

cURL

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc/2.2.-xac-thuc-otp#tab-curl-2)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request POST 'https://services.entrade.com.vn/dnse-order-service/trading-token' \
--header 'Authorization: Bearer <jwt_token_from_login_API_response_step_2.1>' \
--header 'Content-Type: application/json' \
--header 'otp: <otp_from_email>' \
--data ''
```

[Previous2.1. Đăng nhập](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc/2.1.-dang-nhap) [Next3\. Thông tin tài khoản và tiền tài khoản](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/3.-thong-tin-tai-khoan-va-tien-tai-khoan)

Last updated 28 days ago

Was this helpful?