---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.8-cai-chot-loi-cat-lo-theo-deal"
title: "5.8 Cài chốt lời cắt lỗ theo Deal | ENTRADE X"
---

URL

Method

https://api.dnse.com.vn/derivative-deal-risk/pnl-configs/{dealId}

POST

**Path param**

Field

Type

Description

dealId

Mã deal

**Resquest header**

Field

Type

Description

Authorization

string

Bearer <JWT token>

trading-token

string

Trading token lấy từ hệ thống auth

**Resquest body**

Field

Type

Description

Supported Values

takeProfitEnabled

Boolean

Trạng thái bật/ tắt cài đặt Chốt lời

true: bật chốt lời

false: tắt chốt lời

stopLossEnabled

Boolean

Trạng thái bật/ tắt cài đặt Cắt lỗ

true: bật chốt lời

false: tắt chốt lời

takeProfitStrategy

String

Kiểu cấu hình chốt lời

PNL\_RATE: kích hoạt chốt lời theo tỷ lệ lãi

DELTA\_PRICE : kích hoạt chốt lời theo khoảng điểm

stopLossStrategy

String

Kiểu cấu hình cắt lỗ

PNL\_RATE: kích hoạt cắt lỗ theo tỷ lệ lãi

DELTA\_PRICE : kích hoạt cắt lỗ theo khoảng điểm

takeProfitOrderType

String

Kiểu cấu hình giá đặt lệnh chốt lời

FASTEST : đặt lệnh tp khớp ngay

DELTA\_PRICE : đặt lệnh tp theo giá tuỳ chọn

stopLossOrderType

String

Kiểu cấu hình giá đặt lệnh cắt lỗ

FASTEST : đặt lệnh sl khớp ngay

DELTA\_PRICE : đặt lệnh sl theo giá tuỳ chọn

takeProfitRate

Double

Tỷ lệ lãi kích hoạt chốt lời
_Hệ thống chỉ ghi nhận trường này nếu sử dụng takeProfitStrategy: PNL\_RATE_

0< x

stopLossRate

Double

Tỷ lệ lỗ kích hoạt cắt lỗ
_Hệ thống chỉ ghi nhận trường này nếu sử dụng stopLossStrategy: PNL\_RATE_

-1 <= x < 0

takeProfitDeltaPrice

Double

Khoảng điểm kích hoạt chốt lời

_Hệ thống chỉ ghi nhận trường này nếu sử dụng takeProfitStrategy: DELTA\_PRICE_

0 < x

takeProfitDeltaPrice

Double

Khoảng điểm kích hoạt cắt lỗ

_Hệ thống chỉ ghi nhận trường này nếu sử dụng_

_stopLossStrategy :_

_DELTA\_PRICE_

0 < x

takeProfitOrderDeltaPrice

Double

Khoảng điểm tuỳ chỉnh của gía đặt so với giá kích hoạt

x là dạng số, mang dấu âm hoặc dương

stopLossOrderDeltaPrice

Double

Khoảng điểm tuỳ chỉnh của gía đặt so với giá kích hoạt

x là dạng số, mang dấu âm hoặc dương

**Response body**

Field

Type

Description

Supported Values

id

int

Mã bản ghi

dealId

int

Mã deal

accountNo

string

Tiểu khoản

status

string

Trạng thái cài đặt của cấu hình hệ thống

ACTIVE

takeProfitEnabled

Boolean

Trạng thái bật/ tắt cài đặt Chốt lời

true: bật chốt lời

false: tắt chốt lời

stopLossEnabled

Boolean

Trạng thái bật/ tắt cài đặt Cắt lỗ

true: bật chốt lời

false: tắt chốt lời

takeProfitStrategy

string

Kiểu cấu hình chốt lời

PNL\_RATE: kích hoạt chốt lời theo tỷ lệ lãi

DELTA\_PRICE : kích hoạt chốt lời theo khoảng điểm

stopLossStrategy

string

Kiểu cấu hình cắt lỗ

PNL\_RATE: kích hoạt cắt lỗ theo tỷ lệ lãi

DELTA\_PRICE : kích hoạt cắt lỗ theo khoảng điểm

takeProfitOrderType

string

Kiểu cấu hình giá đặt lệnh chốt lời

FASTEST : đặt lệnh tp khớp ngay

DELTA\_PRICE : đặt lệnh tp theo giá tuỳ chọn

stopLossOrderType

string

Kiểu cấu hình giá đặt lệnh cắt lỗ

FASTEST : đặt lệnh sl khớp ngay

DELTA\_PRICE : đặt lệnh sl theo giá tuỳ chọn

takeProfitRate

Double

Tỷ lệ lãi kích hoạt chốt lời

0< x

stopLossRate

Double

Tỷ lệ lỗ kích hoạt cắt lỗ

-1 <= x < 0

takeProfitDeltaPrice

Double

Khoảng điểm kích hoạt chốt lời

0 < x

takeProfitDeltaPrice

Double

Khoảng điểm kích hoạt cắt lỗ

0 < x

takeProfitOrderDeltaPrice

Double

Khoảng điểm tuỳ chỉnh của gía đặt so với giá kích hoạt

x là dạng số, mang dấu âm hoặc dương

stopLossOrderDeltaPrice

Double

Khoảng điểm tuỳ chỉnh của gía đặt so với giá kích hoạt

x là dạng số, mang dấu âm hoặc dương

autoHandleWarning

Boolean

Hiện tại chưa sử dụng tính năng này

Mặc định: true

createdDate

Date time

Thời gian cài cấu hình

Date time

modifiedDate

Date time

Thời gian lần cập nhật cấu hình cuối

Date time

[Previous5.7. Danh sách deal nắm giữ](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.7.-danh-sach-deal-nam-giu) [Next5.9 Cài chốt lời cắt lỗ theo Account](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/5.-giao-dich-phai-sinh/5.9-cai-chot-loi-cat-lo-theo-account)

Last updated 28 days ago

Was this helpful?