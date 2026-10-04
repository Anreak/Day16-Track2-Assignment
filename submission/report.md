1. Tôi dùng Azure, East Asia, Standard_B2als_v2, source commit 14ffb79d8e27dc1c2cac9c02beea3f6e1c6123d4.
2. Dataset có 284.807 dòng, chia train/validation/test 80%/0%/20% theo stratified split, seed 42.
3. Load dữ liệu mất 1,221 giây; training mất 12,934 giây; best iteration là 500.
4. AUC 0,945095, Accuracy 0,999544, F1 0,861702, Precision 0,900000, Recall 0,826531 trên tập test.
5. Latency 1 dòng 1,499 ms; throughput batch 1.000 dòng 42.381,39 dòng/giây; cách đo time.perf_counter quanh predict_proba.
6. CPU/RAM/Network tôi quan sát lúc 21h ngày 02/10/2026 là CPU 6,2%, RAM dùng 253 MiB/tổng 3,8 GiB, Network RX 410.883.247 bytes/TX 18.226.148 bytes; ảnh đính kèm screenshots/resource_usage.png.
7. Billing tại 21h ngày 02/10/2026 ghi nhận chưa cập nhật; ước tính riêng nếu có: 0,0576 USD/giờ (VM 0,0526 + Public IP 0,005).
8. Tôi đã tải kết quả và xóa tài nguyên lúc 21h ngày 02/10/2026; bằng chứng dọn dẹp evidence/cleanup.json.