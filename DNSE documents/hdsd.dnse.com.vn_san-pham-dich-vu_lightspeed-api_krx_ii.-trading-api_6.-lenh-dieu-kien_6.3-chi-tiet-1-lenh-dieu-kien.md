---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/6.-lenh-dieu-kien/6.3-chi-tiet-1-lenh-dieu-kien"
title: "6.3 Chi tiết 1 lệnh điều kiện | ENTRADE X"
---

**url**

`https://api.dnse.dnse.com.vn/conditional-order-api/v1/orders/{id}`

**method**

GET

**header**

Authorization: Bearer <token>

**path**

id : id của lệnh điều kiện

**request body**

**success response body**

`{
"accountNo": "0001000006",
"category": "STOP",
"condition": "price <= 26650",
"createdAt": "2024-10-23T04:21:30.508841Z", "createdBy": "064C000006",
"id": "csc7jii45sbpqutqm820",
"investorId": "0001000006",
"metadata": {
"errorMessage": "",
"externalOrderId": 122,
"status": "OK"
},
"productGroupId": 0,
"props": {
"marketId": "UNDERLYING",
"stopPrice": 26650,
"trailingAmount": 0,
"trailingPercent": 0
},
"status": "ACTIVATED",
"symbol": "HPG",
"targetOrder": {
"loanPackageId": 1531,
"orderType": "LO",  `

`   "price": 26600,  `

`   "quantity": 100,  `

`   "side": "NB"  `

`},  `

`"timeInForce": {  `

`      "expireTime": "2024-10-23T07:30:00Z",
      "kind": "GTD"
},
"updatedAt": "2024-10-23T04:21:33.640466Z", "updatedBy": "064C000006" }`

**error response body**

`{
"message": "Invalid signature"
}`

[Previous6.2 Sổ lệnh điều kiện](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/6.-lenh-dieu-kien/6.2-so-lenh-dieu-kien) [Next6.4 Huỷ lệnh điều kiện](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/6.-lenh-dieu-kien/6.4-huy-lenh-dieu-kien)

Last updated 28 days ago

Was this helpful?