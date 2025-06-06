---
url: "https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/1.-gioi-thieu-chung"
title: "1.\tGiới thiệu chung | ENTRADE X"
---

DNSE cung cấp các API theo chuẩn Restful API với format JSON để phục vụ cho việc giao dịch chứng khoán. Để truy cập được các API này, khách hàng cần phải đăng nhập và sử dụng token sau đăng nhập để gọi API giao dịch. DNSE cung cấp cơ chế bảo mật 2 lớp gồm:

· Lớp 1: sử dụng tài khoản và mật khẩu

· Lớp 2: Sử dụng mã OTP

Sau khi đăng nhập lớp 1, khách hàng được cấp một jwt-token. Tuy nhiên để có thể đặt lệnh thì cần thêm xác thực OTP lớp 2: kết quả ở bước này, khách hàng sẽ nhận được trading-token và dùng thêm token này để giao dịch.

· Với các API lấy thông tin, khi gọi lên server cần truyền theo header Authorization: "Bearer < jwt-token>" trong đó jwt-token là giá trị token trả về lúc đăng nhập thành công lớp 1 (Mục 2.a)

· Với các API làm thay đổi dữ liệu: ví dụ: đặt, huỷ lệnh, cần gửi thêm thông tin trên header có jwt-token cùng với trading-token lấy ở lớp 2 (Mục 2.2)

[PreviousII. Trading API](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api) [Next2\. Đăng nhập và xác thực](https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api_krx/ii.-trading-api/2.-dang-nhap-va-xac-thuc)

Last updated 10 months ago

Was this helpful?