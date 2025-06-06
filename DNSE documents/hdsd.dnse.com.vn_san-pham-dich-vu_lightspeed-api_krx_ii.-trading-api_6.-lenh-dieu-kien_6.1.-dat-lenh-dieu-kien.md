---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/6.-lenh-dieu-kien/6.1.-dat-lenh-dieu-kien"
title: "6.1. Đặt lệnh điều kiện | ENTRADE X"
---

**url**

[https://api.dnse.com.vn/conditional-order-api/v1/orders](https://api.dnse.com.vn/conditional-order-api/v1/orders)

**method**

POST

**header**

Authorization: Bearer <token>

**param**

**request body**

`{
"condition": "price <= 26650",
"targetOrder": {
      "quantity": 100,
      "side": "NB",
      "price": 26600,
      "loanPackageId": 1531,
      "orderType": "LO"
    },
    "symbol": "HPG",
    "props": {
      "stopPrice": 26650,
      "marketId": "UNDERLYING"
    },
    "accountNo": "0001000006",
    "category": "STOP",
    "timeInForce": {
         "expireTime": "2024-10-23T07:30:00.000Z",   `

`         "kind": "GTD"
    }
}`

**success response body**

`{
    "id": "csc7iqa45sbpqutqm81g"
}`

**error response body**

`{
    "message":
    "Invalid signature"
}`

**Request body**

**Field**

**Type**

**Description**

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

**Response body**

Field

Type

Description

id

String

id của lệnh điều kiện

[Previous6\. Lệnh điều kiện](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/6.-lenh-dieu-kien) [Next6.2 Sổ lệnh điều kiện](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/6.-lenh-dieu-kien/6.2-so-lenh-dieu-kien)

Last updated 28 days ago

Was this helpful?