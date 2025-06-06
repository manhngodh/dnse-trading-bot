---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.1.-danh-sach-goi-vay"
title: "4.1.\t Danh sách gói vay | ENTRADE X"
---

- _**Lấy thông tin gói vay, gói vay sẽ được dùng để đặt lệnh**_

- _**Gói vay là khái niệm của DNSE định nghĩa để hỗ trợ phân biệt các tỷ lệ ký quỹ khi đặt lệnh (margin, không margin)**_


**URL**

**Method**

[https://api.dnse.com.vn/order-service/accounts/<account>/loan-packages](https://services.entrade.com.vn/dnse-order-service/accounts/%3Caccount%3E/loan-packages)

GET

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.1.-danh-sach-goi-vay\#path-param)    **Path param**

**Field**

**Type**

**Description**

**account**

Mã tiểu khoản

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.1.-danh-sach-goi-vay\#resquest-header)    **Resquest header**

**Field**

**Type**

**Description**

**Authorization**

Bearer <JWT token>

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.1.-danh-sach-goi-vay\#resquest-body)    **Resquest body**

**Field**

**Type**

**Description**

**N/A**

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.1.-danh-sach-goi-vay\#response-body)    **Response body**

**Field**

**Type**

**Description**

**loanPackages**

Loan Package List

Danh sách các gói vay

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.1.-danh-sach-goi-vay\#loan-package)    **Loan Package**

**Field**

**Type**

**Description**

**id**

Double

Mã gói vay

**name**

String

Tên gói vay

**type**

String

Loại gói vay. M: Margin, N: không vay

**initialRate**

Double

Tỷ lệ ký quỹ ban đầu

**maintenanceRate**

Double

Tỷ lệ duy trì (call margin)

**liquidRate**

Double

Tỷ lệ xử lý (bán xử lý)

**interestRate**

Double

Lãi suất margin (%/năm)

**preferentialPeriod**

Double

Thời gian ưu đãi lãi suất margin

**preferentialInterestRate**

Double

Lãi suất margin trong thời gian ưu đãi

**term**

Double

Kỳ hạn vay margin

**allowExtendLoanTerm**

Boolean

Cho phép gia hạn nợ

**allowEarlyPayment**

Boolean

Cho phép trả nợ trước hạn

**brokerFirmBuyingFeeRate**

Double

Phí mua DNSE thu

**brokerFirmSellingFeeRate**

Double

Phí bán DNSE thu

**transferFee**

Double

Phí chuyển chứng khoán do sở thu

**description**

Double

Mô tả

**symbols**

Double

Danh sách mã áp dụng gói vay, nếu trống có nghĩa áp dụng cho tất cả các mã

cURL

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.1.-danh-sach-goi-vay#tab-curl)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request GET 'https://api.dnse.com.vn/order-service/accounts/<account>/loan-packages' \
--header 'Content-Type: application/json' \
--header 'authorization: Bearer <jwt_token_from_login_API_response_step_2.1>'
```

[Previous4\. Giao dịch cơ sở](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so) [Next4.2. Sức mua, sức bán](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.2.-suc-mua-suc-ban)

Last updated 28 days ago

Was this helpful?