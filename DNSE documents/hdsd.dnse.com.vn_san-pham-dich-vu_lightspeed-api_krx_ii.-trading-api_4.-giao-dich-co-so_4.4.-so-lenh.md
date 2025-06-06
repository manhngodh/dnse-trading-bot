---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.4.-so-lenh"
title: "4.4.  Sổ lệnh | ENTRADE X"
---

**URL**

**Method**

[https://api.dnse.com.vn/order-service/v2/orders?accountNo=<account>](https://services.entrade.com.vn/dnse-order-service/v2/orders?accountNo=%3Caccount%3E)

GET

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.4.-so-lenh\#query-param)    **Query param**

**Field**

**Type**

**Description**

**account**

Mã tiểu khoản

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.4.-so-lenh\#resquest-header)    **Resquest header**

**Field**

**Type**

**Description**

**Authorization**

Bearer <JWT token>

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.4.-so-lenh\#response-body)    **Response body**

**Field**

**Type**

**Description**

**orders**

Order list

Danh sách order

### [Direct link to heading](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.4.-so-lenh\#order)    **Order**

**Field**

**Type**

**Description**

**id**

integer

Số hiệu lệnh

**side**

string

Lệnh Mua/Bán thuộc các giá trị sau:

\- NB: Mua

\- NS: Bán

**accountNo**

string

Số tiểu khoản

**investorId**

string

Mã Khách hàng

**symbol**

string

Mã chứng khoán

**price**

number

Giá đặt

**quantity**

integer

Khối lượng đặt

**orderType**

string

Loại lệnh, thuộc các giá trị sau:

\- LO: lệnh giới hạn

\- MP/MTL: lệnh thị trường

\- ATC/ATO: lệnh khớp phiên định kỳ đóng cửa/mở cửa

\- PLO: lệnh khớp lệnh sau giờ

**orderStatus**

string

Trạng thái lệnh, thuộc các giá trị sau đây:

\- pending: chờ gửi

\- pendingNew: chờ gửi

\- new: chờ khớp

\- partiallyFilled: khớp một phần

\- filled: khớp toàn bộ

\- rejected: bị từ chối

\- expired: bị hết hạn trong phiên

\- doneForDay: lệnh hết hiệu lực khi hết phiên

**fillQuantity**

integer

Khối lượng đã khớp

**lastQuantity**

integer

Khối lượng của lần khớp gần nhất của lệnh

**lastPrice**

number

Giá khớp của lần khớp gần nhất của lệnh

**averagePrice**

double

Giá khớp trung bình của lệnh

**transDate**

string

Ngày giao dịch, theo định dạng ISO UTC 8601 format date

Ví dụ: 2022-07-15

**createdDate**

string

Thời điểm (ngày giờ) đặt lệnh, theo định dạng ISO UTC 8601 format datetime

Ví dụ: 2022-07-15T10:00:00.111+07:00

**modifiedDate**

string

Thời điểm (ngày giờ) thay đổi cuối cùng của lệnh

**taxRate**

double

Tỷ lệ thuế lệnh chịu

**feeRate**

double

Tỷ lệ phí lệnh chịu

**leaveQuantity**

integer

Khối lượng chưa khớp của lệnh

**canceledQuantity**

integer

Khối lượng đã huỷ của lệnh

**priceSecure**

double

Giá cọc cho lệnh

**custody**

string

Số lưu ký của tiểu khoản đặt lệnh

**channel**

string

Kênh đặt lệnh

**loanPackageId**

integer

Id gói vay

**initialRate**

number

Tỷ lệ ký quỹ theo gói vay tương ứng với lệnh

**error**

string

Mã lỗi với trạng thái expired

0: Lệnh MP không có lệnh đối ứng

Mã lỗi đối với trạng thái lệnh rejected (bị từ chối) bao gồm các mã lỗi:

QMAX\_EXCEED: Vượt quá KL có thể mua/bán

INVALID\_QUANTITY\_LOT: KL đặt không hợp lệ

PRICE\_MUST\_GREATER\_THAN\_OR\_EQUAL\_TO\_FLOOR\_PRICE: Giá đặt không hợp lệ

PRICE\_MUST\_LESS\_THAN\_OR\_EQUAL\_TO\_CEILING\_PRICE: Giá đặt không hợp lệ

INVALID\_PRICE\_LOT: Giá đặt không hợp lệ

SYMBOL\_IS\_NOT\_IN\_MARGIN\_BASKET: Mã không nằm trong rổ margin

cURL

[Direct link to tab](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.4.-so-lenh#tab-curl)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line] print:whitespace-pre-wrap
curl --location --request GET 'https://api.dnse.com.vn/order-service/v2/orders?accountNo=<account>' \
--header 'content-type: application/json' \
--header 'authorization: Bearer <jwt_token_from_login_API_response_step_2.1>'
```

[Previous4.3. Đặt lệnh](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.3.-dat-lenh) [Next4.4. Chi tiết lệnh](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/4.-giao-dich-co-so/4.4.-chi-tiet-lenh)

Last updated 28 days ago

Was this helpful?