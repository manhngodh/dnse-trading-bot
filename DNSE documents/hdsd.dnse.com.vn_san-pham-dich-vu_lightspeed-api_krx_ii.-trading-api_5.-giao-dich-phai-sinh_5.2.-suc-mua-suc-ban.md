---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.2.-suc-mua-suc-ban"
title: "5.2.  Sức mua, sức bán | ENTRADE X"
---

_**Lấy thông tin sức mua sức bán tối đa theo tiểu khoản, mã, giá và gói vay**_

**URL**

**Method**

[https://api.dnse.com.vn/order-service/accounts/<account>/derivative-ppse?symbol=<symbol>&price=<price>&loanPackageId=<loanPackageId>](https://services.entrade.com.vn/dnse-order-service/accounts/%3Caccount%3E/derivative-ppse?symbol=%3Csymbol%3E&price=%3Cprice%3E&loanPackageId=%3CloanPackageId%3E)

GET

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.2.-suc-mua-suc-ban\#path-param)    **Path param**

**Field**

**Type**

**Description**

**account**

Mã tiểu khoản

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.2.-suc-mua-suc-ban\#query-param)    **Query param**

**Field**

**Type**

**Description**

**loanPackageId**

Mã gói vay (lấy Mã gói vay cần trong danh sách gói vay mục 5.1)

**symbol**

Mã, ví dụ: VN30F2306

**price**

Giá

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.2.-suc-mua-suc-ban\#resquest-header)    **Resquest header**

**Field**

**Type**

**Description**

**Authorization**

Bearer <JWT token>

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.2.-suc-mua-suc-ban\#resquest-body)    **Resquest body**

**Field**

**Type**

**Description**

**N/A**

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.2.-suc-mua-suc-ban\#response-body)    **Response body**

**Field**

**Type**

**Description**

**investorAccountId**

String

Mã tiểu khoản

**ppse**

Double

Sức mua

**price**

Double

Giá tính sức mua

**qmaxLong**

Double

Số lượng mua tối đa (LONG)

**qmaxShort**

Double

Số lượng bán tối đa (SHORT)

cURL

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.2.-suc-mua-suc-ban#tab-curl)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request GET 'https://api.dnse.com.vn/order-service/accounts/<account>/derivative-ppse?symbol=<symbol>&price=<price>&loanPackageId=<loanPackageId>' \
--header 'Content-Type: application/json' \
--header 'authorization: Bearer <jwt_token_from_login_API_response_step_2.1>'
```

[Previous5.1. Danh sách gói vay](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.1.-danh-sach-goi-vay) [Next5.3. Đặt lệnh](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.3.-dat-lenh)

Last updated 28 days ago

Was this helpful?