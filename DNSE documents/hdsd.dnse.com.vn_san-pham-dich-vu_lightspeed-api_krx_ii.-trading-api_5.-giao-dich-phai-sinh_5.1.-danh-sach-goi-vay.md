---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.1.-danh-sach-goi-vay"
title: "5.1.\t Danh sách gói vay | ENTRADE X"
---

**URL**

**Method**

[https://api.dnse.com.vn/order-service/accounts/<account>/derivative-loan-packages](https://services.entrade.com.vn/dnse-order-service/accounts/%3Caccount%3E/derivative-loan-packages)

GET

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.1.-danh-sach-goi-vay\#path-param)    **Path param**

**Field**

**Type**

**Description**

**account**

Mã tiểu khoản

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.1.-danh-sach-goi-vay\#resquest-header)    **Resquest header**

Field

Type

Description

Authorization

Bearer <JWT token>

**Resquest body**

**Field**

**Type**

**Description**

**N/A**

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.1.-danh-sach-goi-vay\#response-body)    **Response body**

**Field**

**Type**

**Description**

**loanPackages**

Loan Package List

Danh sách các gói vay

**Loan Package**

**Field**

**Type**

**Description**

**id**

Double

Mã gói vay

**name**

String

Tên gói vay

**source**

String

Nguồn gói vay

**initialRate**

Double

Tỷ lệ ký quỹ ban đầu

**maintenanceRate**

Double

Tỷ lệ duy trì (call margin)

**liquidRate**

Double

Tỷ lệ xử lý (bán xử lý)

**tradingFee**

Trading fee

Thông tin phí giao dịch

**symbolTypes**

String array

Các mã áp dụng gói vay

cURL

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.1.-danh-sach-goi-vay#tab-curl)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request GET 'https://api.dnse.com.vn/order-service/accounts/<account>/derivative-loan-packages' \
--header 'Content-Type: application/json' \
--header 'authorization: Bearer <jwt_token_from_login_API_response_step_2.1>'
```

[Previous5\. Giao dịch phái sinh](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh) [Next5.2. Sức mua, sức bán](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.2.-suc-mua-suc-ban)

Last updated 28 days ago

Was this helpful?