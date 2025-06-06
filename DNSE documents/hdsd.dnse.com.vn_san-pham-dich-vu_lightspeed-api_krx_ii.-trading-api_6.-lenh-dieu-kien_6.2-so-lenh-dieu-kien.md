---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/6.-lenh-dieu-kien/6.2-so-lenh-dieu-kien"
title: "6.2 Sổ lệnh điều kiện | ENTRADE X"
---

**url**

[https://api.dnse.com.vn/conditional-order-api/v1/orders](https://api.dnse.com.vn/conditional-order-api/v1/orders)

**method**

GET

**header**

Authorization: Bearer <token>

**param**

accountNo:(String) Mã tiểu khoản
daily: (Boolean) Lấy lệnh trong ngày(true/false) - default là false
from: (String) ngày bắt đầu yyyy-MM-dd
to: (String) ngày kết thúc yyyy-MM-dd
page (Integer): số thứ tự trang
size (Interger): số lượng item trong trang
status (Array): trạng thái của lệnh (NEW/ACTIVATED/REJECTED/CANCELLED/EXPIRED/FAILED/CANCELLED\_BY\_RIGHTS\_EVENT)
symbol (String): Mã
marketId: UNDERLYING (nếu lấy sổ lệnh điều kiện cơ sở) hoặc DERIVATIVES (phái sinh)

**request body**

**success response body**

`{
    "content": [\
        {\
            "accountNo": "0001000006",\
            "category": "STOP",\
            "condition": "price >= 26650",\
            "createdAt": "2024-10-23T04:19:53.94801Z",\
            "createdBy": "064C000006",\
            "id": "csc7iqa45sbpqutqm81g",\
            "investorId": "0001000006",\
            "metadata": { `\
\
`                 "errorMessage": "",\
                 "externalOrderId": 112,\
                 "status": "OK"\
            },\
            "props": {\
                 "marketId": "UNDERLYING",\
                 "stopPrice": 26650,\
                 "trailingAmount": 0,\
                 "trailingPercent": 0\
            },\
            "status": "ACTIVATED",\
            "symbol": "HPG",\
            "targetOrder": {\
                "loanPackageId": 1531,                  `\
\
`                "orderType": "LO",\
                "price": 26600,\
                "quantity": 100,\
                "side": "NB"\
             },\
             "timeInForce": {\
             "expireTime": "2024-10-23T07:30:00Z",\
             "kind": "GTD"\
             },\
             "updatedAt": "2024-10-23T04:19:59.299943Z",\
             "updatedBy": "064C000006"\
         },\
         {\
             "accountNo": "0001000006",\
             "category": "STOP",\
             "condition": "price \u003c= 26650",\
             "createdAt": "2024-10-23T04:18:18.971188Z",\
             "createdBy": "064C000006",\
             "id": "csc7i2i45sbpqutqm80g",\
             "investorId": "0001000006",\
             "metadata": {\
                  "errorMessage": "",\
                  "externalOrderId": 102,\
                  "status": "OK"\
         },\
         "props": {\
             "marketId": "UNDERLYING",\
             "stopPrice": 26650,\
             "trailingAmount": 0,\
             "trailingPercent": 0\
         },\
         "status": "ACTIVATED", `\
\
`         "symbol": "HPG",\
         "targetOrder": {\
            "loanPackageId": 1531,\
            "orderType": "LO",\
            "price": 26600,\
            "quantity": 100,\
            "side": "NB"\
         },\
         "timeInForce": {\
             "expireTime": "2024-10-23T07:30:00Z",\
             "kind": "GTD"\
         }, `\
\
`        "updatedAt": "2024-10-23T04:18:26.831862Z", `\
\
`        "updatedBy": "064C000006"\
      }\
],
"page": 1,
"size": 10000,
"numberOfElements": 2,
"totalElements": 2,
"totalPages": 1
}`

**error response body**

`{`

`  "message": "Invalid signature" `

`}`

**Response body**

Field

Type

Description

createdAt

String

Thời gian tạo lệnh

createdBy

String

Người tạo lệnh

id

String

id của lệnh

updatedAt

String

Thời gian cập nhật lệnh

updatedBy

String

Người cập nhật lệnh

status

String

Trạng thái của lệnh

condition

String

Điều kiện đặt
price >= stopPrice
price <= stopPrice

targetOrder

Object

targetOrder.quantity

Double

Khối lượng đặt

targetOrder.side

String

Lệnh mua: NB, Lệnh bán:NS

targetOrder.price

Doble

Giá đặt, đơn vị đồng

targetOrder.loanPackageId

Integer

Mã gói vay, lấy gói vay muốn đặt từ api danh sách gói vay

targetOrder.orderType

String

Loại lệnh, thuộc các giá trị sau:

- LO: lệnh giới hạn

- MP/MTL: lệnh thị trường


symbol

String

Mã

props

Object

props.stopPrice

Double

Giá trigger lệnh điều kiện

props.marketId

String

lệnh cơ sở: UNDERLYING
Lệnh phái sinh: DERIVATIVES

accountNo

String

Mã tiểu khoản

category

String

STOP

timeInForce

Object

timeInForce.expireTime

String

Thời gian hết hạn lệnh

timeInForce.kind

String

Loại : GTD

page

Integer

Trang đã yêu cầu

size

Integer

Số lượng bản ghi trong trang đã yêu cầu

numberOfElements

Integer

Số lượng lệnh trong trang

totalElements

Integer

Tổng số lượng lệnh có trong hệ thống

totalPages

Integer

Tổng số lượng trang có trong hệ thống

[Previous6.1. Đặt lệnh điều kiện](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/6.-lenh-dieu-kien/6.1.-dat-lenh-dieu-kien) [Next6.3 Chi tiết 1 lệnh điều kiện](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/6.-lenh-dieu-kien/6.3-chi-tiet-1-lenh-dieu-kien)

Last updated 28 days ago

Was this helpful?