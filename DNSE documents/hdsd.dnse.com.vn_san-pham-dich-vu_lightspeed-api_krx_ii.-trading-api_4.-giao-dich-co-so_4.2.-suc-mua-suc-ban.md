---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.2.-suc-mua-suc-ban"
title: "4.2.  Sức mua, sức bán | ENTRADE X"
---

_**Lấy thông tin sức mua sức bán tối đa theo tiểu khoản, mã, giá và gói vay**_

**URL**

**Method**

[https://api.dnse.com.vn/order-service/accounts/<account>/ppse?symbol=<symbol>&price=<price>&loanPackageId=<loanPackageId>](https://services.entrade.com.vn/dnse-order-service/accounts/%3Caccount%3E/ppse?symbol=%3Csymbol%3E&price=%3Cprice%3E&loanPackageId=%3CloanPackageId%3E)

GET

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.2.-suc-mua-suc-ban\#path-param)    **Path param**

**Field**

**Type**

**Description**

**account**

Mã tiểu khoản

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.2.-suc-mua-suc-ban\#query-param)    **Query param**

**Field**

**Type**

**Description**

**loanPackageId**

Mã gói vay (lấy Mã gói vay cần trong danh sách gói vay mục 4.1)

**symbol**

Mã

**price**

Giá (đơn vị đồng)

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.2.-suc-mua-suc-ban\#resquest-header)    **Resquest header**

**Field**

**Type**

**Description**

**Authorization**

Bearer <JWT token>

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.2.-suc-mua-suc-ban\#resquest-body)    **Resquest body**

**Field**

**Type**

**Description**

**N/A**

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.2.-suc-mua-suc-ban\#response-body)    **Response body**

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

**qmax**

Double

Số lượng mua tối đa

**tradeQuantity**

Double

Số lượng bán tối đa

cURL

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.2.-suc-mua-suc-ban#tab-curl)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request GET 'https://api.dnse.com.vn/order-service/accounts/<account>/ppse?symbol=<symbol>&price=<price>&loanPackageId=<loanPackageId>' \
--header 'Content-Type: application/json' \
--header 'authorization: Bearer <jwt_token_from_login_API_response_step_2.1>'
```

[Previous4.1. Danh sách gói vay](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.1.-danh-sach-goi-vay) [Next4.3. Đặt lệnh](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.3.-dat-lenh)

Last updated 28 days ago

Was this helpful?