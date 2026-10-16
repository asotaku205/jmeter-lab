# Báo cáo thực hành: Học công cụ kiểm thử hiệu năng Apache JMeter

> Môn: Kiểm định & Chất lượng Phần mềm — Bài thực hành công cụ JMeter
> Người thực hiện: Đỗ Trần Anh Sơn

## 1. Mục tiêu

- Tìm hiểu và sử dụng thành thạo các thành phần cốt lõi của **Apache JMeter**: Test Plan, Thread Group,
  Sampler, Config Element, Timer, Assertion, Listener.
- Xây dựng một kịch bản kiểm thử hiệu năng hoàn chỉnh cho một ứng dụng web demo.
- Thực thi kiểm thử, thu thập số liệu (response time, throughput, error rate) và sinh báo cáo dashboard.

## 2. Môi trường thực hiện

| Thành phần | Phiên bản / Thông tin |
|---|---|
| Apache JMeter | 5.6.3 |
| Java | OpenJDK 17 |
| Ứng dụng demo | Demo Shop API (Flask, Python) chạy tại `http://127.0.0.1:5000` |
| Hệ điều hành | Ubuntu (máy lab) |

## 3. Đối tượng kiểm thử: Demo Shop API

Ứng dụng web demo mô phỏng một cửa hàng trực tuyến đơn giản, gồm các endpoint:

| Endpoint | Method | Mô tả |
|---|---|---|
| `/` | GET | Trang chủ (HTML) |
| `/api/products` | GET | Danh sách 8 sản phẩm (JSON) |
| `/api/products/{id}` | GET | Chi tiết một sản phẩm (JSON), 404 nếu không tồn tại |
| `/api/login` | POST | Đăng nhập bằng JSON `{username, password}`, trả về `token` |
| `/api/orders?user={u}` | GET | Danh sách đơn hàng của user (JSON) |
| `/health` | GET | Kiểm tra trạng thái ứng dụng |

Mã nguồn ứng dụng nằm trong thư mục [`demo-app/`](demo-app/).

## 4. Kịch bản kiểm thử (`jmeter/DemoShop_TestPlan.jmx`)

### 4.1. Cấu trúc Test Plan

```
Kiểm thử hiệu năng - Demo Shop API (Test Plan)
├── HTTP Header Manager                    # Header chung: Accept + Content-Type = application/json
├── TG01 - Luồng xem sản phẩm              # 20 threads, ramp-up 20s, lặp 10 lần
│   ├── HTTP Request Defaults              # Server mặc định: 127.0.0.1:5000
│   ├── GET Trang chủ                      # /
│   │   ├── Assert - Response code 200
│   │   └── Assert - Trang chứa 'Demo Shop'
│   ├── GET Danh sách sản phẩm             # /api/products
│   │   ├── Assert - Response code 200
│   │   └── Assert - Response time < 2000ms (Duration Assertion)
│   ├── GET Chi tiết sản phẩm (ngẫu nhiên) # /api/products/${__Random(1,8)}
│   │   └── Assert - Response code 200
│   ├── Think Time                          # Gaussian Random Timer: nghỉ ~800ms ± 400ms
│   └── View Results Tree                  # Xem chi tiết từng request khi debug
├── TG02 - Luồng đăng nhập & đơn hàng     # 20 threads, ramp-up 20s, lặp 10 lần
│   ├── HTTP Request Defaults
│   ├── CSV Data Set Config                # Đọc 10 tài khoản từ test-data/users.csv
│   ├── POST Đăng nhập                     # /api/login với ${username}/${password}
│   │   ├── Assert - Response code 200
│   │   └── Assert - Response chứa 'token'
│   ├── GET Đơn hàng của user             # /api/orders?user=${username}
│   │   ├── Assert - Response code 200
│   │   └── Assert - Response time < 2000ms
│   └── Think Time
└── Aggregate Report                       # Tổng hợp số liệu, ghi ra results/aggregate.csv
```

Tổng cộng: **40 user ảo**, mỗi user lặp 10 lần → khoảng **1000 requests**.

### 4.2. Các khái niệm JMeter đã áp dụng

| Thành phần | Vai trò trong bài này |
|---|---|
| **Thread Group** | Mô phỏng nhóm người dùng đồng thời; cấu hình số thread, thời gian ramp-up, số vòng lặp |
| **HTTP Request** (Sampler) | Gửi request GET/POST tới từng endpoint |
| **HTTP Request Defaults** (Config) | Khai báo server/port một lần, các sampler kế thừa |
| **HTTP Header Manager** (Config) | Gửi header chung cho mọi request |
| **CSV Data Set Config** (Config) | Tham số hóa dữ liệu đầu vào (10 tài khoản đăng nhập) |
| **Gaussian Random Timer** (Timer) | Mô phỏng thời gian "suy nghĩ" của user giữa các thao tác |
| **Response Assertion** | Kiểm tra mã trạng thái và nội dung response (pass/fail từng sample) |
| **Duration Assertion** | Fail nếu response time vượt ngưỡng 2000ms |
| **View Results Tree / Aggregate Report** (Listener) | Xem chi tiết và tổng hợp kết quả |
| **HTML Dashboard Report** | Báo cáo đồ họa sinh từ file `.jtl` (`jmeter -g results.jtl -o dashboard/`) |

### 4.3. Giao diện JMeter mở Test Plan

![Giao diện JMeter với Test Plan Demo Shop](screenshots/01-gui-test-plan.png)

## 5. Thực thi và kết quả

> ⏳ **Đang chờ chạy kiểm thử** (môi trường lab cần được cấp quyền mạng cho tiến trình Java).
> Phần này sẽ được cập nhật ngay sau khi có kết quả, gồm:
> - Ảnh chụp terminal chạy JMeter ở chế độ headless (`-n`)
> - Bảng Aggregate Report (average / min / max / throughput / error %)
> - Ảnh HTML Dashboard: biểu đồ response time, throughput theo thời gian

Câu lệnh thực thi (dự kiến):

```bash
cd jmeter
../apache-jmeter-5.6.3/bin/jmeter -n -t DemoShop_TestPlan.jmx \
  -l results/results.jtl -e -o results/dashboard
```

## 6. Nhận xét và kết luận

*(Sẽ bổ sung sau khi phân tích kết quả đo: response time trung bình, throughput, tỉ lệ lỗi
và đánh giá khả năng chịu tải của Demo Shop API.)*

## 7. Cách chạy lại

```bash
# 1. Khởi động app demo
cd demo-app
pip install -r requirements.txt
python app.py          # chạy tại http://127.0.0.1:5000

# 2. Mở test plan bằng JMeter GUI (tuỳ chọn)
jmeter -t jmeter/DemoShop_TestPlan.jmx

# 3. Chạy kiểm thử headless + sinh báo cáo HTML
cd jmeter
jmeter -n -t DemoShop_TestPlan.jmx -l results/results.jtl -e -o results/dashboard
```

## 8. Cấu trúc thư mục

```
jmeter-lab/
├── README.md                    # Báo cáo này
├── demo-app/                    # Ứng dụng demo làm mục tiêu kiểm thử
│   ├── app.py
│   └── requirements.txt
├── jmeter/                      # Test plan và dữ liệu kiểm thử
│   ├── DemoShop_TestPlan.jmx
│   └── test-data/users.csv
├── results/                     # Kết quả chạy (.jtl, aggregate.csv, dashboard HTML)
└── screenshots/                 # Hình ảnh minh hoạ
```
