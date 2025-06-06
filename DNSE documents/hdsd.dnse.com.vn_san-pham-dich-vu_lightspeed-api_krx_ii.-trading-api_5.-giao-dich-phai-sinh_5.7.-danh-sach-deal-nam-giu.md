---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.7.-danh-sach-deal-nam-giu"
title: "5.7.  Danh sách deal nắm giữ | ENTRADE X"
---

**URL**

**Method**

[https://api.dnse.com.vn/derivative-core/deals?accountNo=](https://services.entrade.com.vn/dnse-derivative-core/deals?accountNo=0001008710){accountNo}

GET

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.7.-danh-sach-deal-nam-giu\#query-param)    **Query param**

**Field**

**Type**

**Description**

**account**

Mã tiểu khoản

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.7.-danh-sach-deal-nam-giu\#resquest-header)    **Resquest header**

**Field**

**Type**

**Description**

**Authorization**

Bearer <JWT token>

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.7.-danh-sach-deal-nam-giu\#resquest-body)    **Resquest body**

**Field**

**Type**

**Description**

**N/A**

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.7.-danh-sach-deal-nam-giu\#response-body)    **Response body**

**Field**

**Type**

**Description**

**data**

Deal List

Danh sách Deal nắm giữ

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.7.-danh-sach-deal-nam-giu\#deal)    **Deal**

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

**openQuantity**

integer

Khối lương mở

**closedQuantity**

integer

Khối lượng đóng

**overNightQuantity**

integer

Khối lượng giữ qua đêm

**breakEvenPrice**

Double

Giá hoà vốn

**costPrice**

Double

Giá vốn toàn bộ open quantity

**costPriceVM**

Double

Giá vốn VM (theo gía hàng ngày)

**averageCostPrice**

Double

Giá mở trung bình

**averageClosePrice**

Double

Giá đóng trung bình

**totalUnrealizedProfit**

Double

Lãi mở (chưa bao gồm phí thuế)

**totalUnrealizedTaxAndFee**

Double

Phí thuế phần mổ

**totalRealizedProfit**

Double

Lãi đã đóng (chưa bao gồm phí thuế)

**totalRealizedTaxAndFee**

Double

Phí thuế phần đã đóng

**estimateRemainFee**

Double

Phí ước tính còn lại

**estimateRemainTax**

Double

Thuế ước tính còn lại

**totalRealizedPositionFee**

Double

Phí vị thế phần đã đóng

**totalUnrealizedPositionFee**

Double

Phí vị thế phần mở

**maturityFee**

Double

Phí đáo hạn

**createdDate**

Date

Giờ tạo

**modifiedDate**

Date

Giờ cập nhật

First Tab

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.7.-danh-sach-deal-nam-giu#tab-first-tab)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request GET 'https://api.dnse.com.vn/derivative-core/deals?accountNo=<account>' \
--header 'content-type: application/json' \
--header 'authorization: Bearer <jwt_token_from_login_API_response_step_2.1>'
```

[Previous5.6. Huỷ lệnh](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.6.-huy-lenh) [Next5.8 Cài chốt lời cắt lỗ theo Deal](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.8-cai-chot-loi-cat-lo-theo-deal)

Last updated 28 days ago

Was this helpful?