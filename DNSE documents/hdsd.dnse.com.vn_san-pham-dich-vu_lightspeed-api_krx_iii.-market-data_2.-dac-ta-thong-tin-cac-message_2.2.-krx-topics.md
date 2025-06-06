---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/iii.-market-data/2.-dac-ta-thong-tin-cac-message/2.2.-krx-topics"
title: "2.2. KRX Topics | ENTRADE X"
---

Stock Info

plaintext/quotes/krx/mdds/stockinfo/v1/roundlot/symbol/ **{symbol}**

Top Price

plaintext/quotes/krx/mdds/topprice/v1/roundlot/symbol/ **{symbol}**

Board Event

plaintext/quotes/krx/mdds/boardevent/v1/roundlot/market/ **{market}**/product/ **{tsczProductGrpId}**

Market Index

plaintext/quotes/krx/mdds/index/ **{indexName}**

Stock OHLC

plaintext/quotes/krx/mdds/v2/ohlc/stock/ **{resolution}**/ **{symbol}**

Derivative OHLC

plaintext/quotes/krx/mdds/v2/ohlc/derivative/ **{resolution}**/ **{symbol}**

Index OHLC

plaintext/quotes/krx/mdds/v2/ohlc/index/ **{resolution}**/ **{indexName}**

Tick

plaintext/quotes/krx/mdds/tick/v1/roundlot/symbol/ **{symbol}**

Field

Type

Description

symbol

String

Mã chứng khoán

indexName

String

Mã Index:

- VN30


- VNINDEX

- HNX30

- HNX

- UPCOM


resolution

String

Resolution của OHLC:

- 1: Phút

- 1H: Giờ

- 1D: Ngày

- W: Tuần


marketId

String

Ký hiệu sàn:

- STO: HoSE Stock Market


- STX: HNX Listed Stock Market

- BDX: HNX Government Bond Market

- DVX: HNX Derivative Market

- UPX: HNX UpCoM Stock Market

- HCX: HNX Corporate Bond Market


tscProductGrpId

String

Loại chứng khoán/nhóm sản phẩm trên sàn:

- STO : HoSE Stock

- BDX : Government Bond

- FIO : HoSE Index Futures (thuộc marketId DVX)

- FBX : HNX Bond Futures (thuộc marketId DVX)

- STX : HNX Stock

- UPX : HNX UpCom

- HCX : HNX Corporate Bond


Cấu trúc message được nhận qua WebSocket. Định dạng JSON

Type

Payload

Mô tả

Topic MQTT

MARKET\_INDEX

MarketIndex

Chứa thông tin chỉ số

Market Index

STOCK\_INFO

StockInfo

Chứa thông tin giá của mã

Stock Info

TOP\_PRICE

TopPrice

Chứa thông tin Bid/Offer

Top Price

BOARD\_EVENT

BoardEvent

Chứa thông tin thay đổi phiên

Board Event

OHLC

OHLC

Thông tin nến

OHLC

TICK

Tick

Thông tin khớp lệnh

Tick

Chi tiết message xem tại file **1\. DNSE MDDS System - KRX v1.4.xlsx** đính kèm.

[35KB\\
\\
DNSE - MDDS System - KRX v1.4.xlsx](https://539770798-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F-MJ0-9Tzhtqir6mnYmqv%2Fuploads%2FGFbpTG3956drMWvoEpLY%2FDNSE%20-%20MDDS%20System%20-%20KRX%20v1.4.xlsx?alt=media&token=45867462-dd43-45e6-9020-14c8850d252c)

(MQTT X client dùng để test kết nối: [https://www.emqx.com/en/try?product=MQTTX](https://www.emqx.com/en/try?product=MQTTX))

- Examples: [https://github.com/emqx/MQTT-Client-Examples](https://github.com/emqx/MQTT-Client-Examples)

- DNSE Python Example: theo file file đính kèm. Version gợi ý:



- python 3.13

- paho-mqtt: 2.1.0


[2KB\\
\\
MQTT.rar](https://539770798-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F-MJ0-9Tzhtqir6mnYmqv%2Fuploads%2F1ER8hEw94KmKlJ6w1HOL%2FMQTT.rar?alt=media&token=8a1d158c-0a13-4f03-b7cf-72f33f6d8c46)

[Previous2.1. Môi trường](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/iii.-market-data/2.-dac-ta-thong-tin-cac-message/2.1.-moi-truong) [NextAmi X](https://hdsd.dnse.com.vn/san-pham-dich-vu/ami-x)

Last updated 8 days ago

Was this helpful?