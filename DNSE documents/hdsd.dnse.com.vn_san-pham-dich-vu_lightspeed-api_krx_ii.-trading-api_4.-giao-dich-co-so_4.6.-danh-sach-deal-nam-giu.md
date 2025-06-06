---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.6.-danh-sach-deal-nam-giu"
title: "4.6.  Danh sách deal nắm giữ | ENTRADE X"
---

**URL**

**Method**

[https://api.dnse.com.vn/deal-service/deals?accountNo=<account>](https://services.entrade.com.vn/dnse-deal-service/deals?accountNo=%3Caccount%3E)

GET

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.6.-danh-sach-deal-nam-giu\#query-param)    **Query param**

**Field**

**Type**

**Description**

**account**

Mã tiểu khoản

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.6.-danh-sach-deal-nam-giu\#resquest-header)    **Resquest header**

**Field**

**Type**

**Description**

**Authorization**

Bearer <JWT token>

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.6.-danh-sach-deal-nam-giu\#resquest-body)    **Resquest body**

**Field**

**Type**

**Description**

**N/A**

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.6.-danh-sach-deal-nam-giu\#response-body)    **Response body**

**Field**

**Type**

**Description**

**deals**

Deal List

Danh sách Deal nắm giữ

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.6.-danh-sach-deal-nam-giu\#deal)    **Deal**

**Fied**

**Type**

**Description**

**id**

long

Id deal

**symbol**

string

Mã chứng khoán

**accountNo**

string

Số tiểu khoản

**orderIds**

\[\]string

danh sách Order Id thuộc deal

**status**

string

Trạng thái của deal, thuộc các giá trị sau:


OPEN: đang mở

CLOSED: đã đóng

**loanPackageId**

string

mã gói vay

**side**

string

Bên mua/bán

NB: mua

NS: bán

**secure**

Double

cọc hiện tại của deal

**accumulateQuantity**

integer

Khối lượng mở tích lũy

**closedQuantity**

integer

khối lượng đã đóng

**t0ReceivingQuantity**

integer

**t1ReceivingQuantity**

integer

**t2ReceivingQuantity**

integer

**costPrice**

double

Giá vốn hiện tại của deal

**averageCostPrice**

double

Giá mở cửa trung bình của deal

**marketPrice**

double

Giá thị trường

**realizedProfit**

double

Lãi lỗ phần đã chốt, chưa bao gồm phí thuế

**realizedTotalTaxAndFee**

double

Phí thuế của phần đã chốt, bao gồm cả mở và đóng

**collectedBuyingFee**

double

Tổng phí mua

**collectedBuyingTax**

doulbe

Tổng thuế mua

**collectedSellingFee**

doulbe

tổng phí bán

**collectedSellingTax**

doulbe

tổng thuế bán

**collectedStockTransferFee**

double

tổng phí chuyển khoản chứng khoán khi bán

**collectedInterestFee**

double

Tổng lãi vay khi dùng margin

**estimateRemainTaxAndFee**

doulbe

phí thuế đóng tạm tính cho phần còn lại của deal, tính theo giá thị trường

**unrealizedProfit**

doulbe

lãi lỗ tạm tính cho phần còn lại của deal, tính theo giá thị trường

**breakEvenPrice**

double

giá hòa vốn

**dividendReceivingQuantity**

integer

**dividendQuantity**

integer

**cashReceiving**

double

**rightReceivingCash**

double

**t0ReceivingCash**

double

**t1RecevingCash**

double

**t2RecevingCash**

double

**createdDate**

string

ISO UTC 8601, format datetime

**modifiedDate**

string

datetime

**currentDebt**

double

nợ của phần đang mở

**currentInterest**

double

lãi của phần đang mở

**unrealizedOpenTaxAndFee**

double

phí thuế mua của phần đang mở

**currentDebtExcludeToCollect**

double

nợ chưa trả của deal

**accumulateSecure**

double

**accumulateDebt**

double

**averageClosePrice**

double

**currentInterestExcludeToCollect**

double

lãi chưa trả của deal

cURL

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.6.-danh-sach-deal-nam-giu#tab-curl)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request GET 'https://api.dnse.com.vn/deal-service/deals?accountNo=<account>' \
--header 'content-type: application/json' \
--header 'authorization: Bearer <jwt_token_from_login_API_response_step_2.1>'
```

[Previous4.5. Huỷ lệnh](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.5.-huy-lenh) [Next5\. Giao dịch phái sinh](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh)

Last updated 28 days ago

Was this helpful?