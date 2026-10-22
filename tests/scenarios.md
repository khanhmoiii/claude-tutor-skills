# Kịch bản kiểm thử

Các kịch bản dưới đây chạy bằng Claude Code headless (`claude -p`, model Sonnet) trên dự án mẫu `fixture/`. Skill được đặt trong `fixture/.claude/skills/`. Lượt thứ hai dùng `claude -p -c`.

Lỗi cài sẵn trong dự án mẫu:
- `cart.py`: `range(1, len(items))` bỏ sót phần tử đầu tiên. Còn có mutable default argument.
- `users.py`: SQL injection, crash khi `fetchone()` trả `None`, chia cho 0 khi danh sách rỗng.
- `app.js`: quên `await res.json()`.
- `.learning/`: 3 mục. Ngày 2026-10-22 có 2 mục đến hạn.

| # | Lệnh | Hành vi mong đợi | Kết quả |
|---|---|---|---|
| 1 | `/hint cart.py in ra 20.0…` | Cấp 0, chỉ hỏi để người học đặt giả thuyết, **không** chỉ ra vòng lặp | v1: lộ vị trí (hỏi "`i` chạy qua những giá trị nào") → đã sửa; v2: đạt |
| 2 | `/hint 5` (lượt 2) | Code thật, chỗ then chốt là `___` | Đạt |
| 3 | `/debug TypeError … app.js:4` | Hỏi mong đợi/thực tế và đọc lỗi; không sửa hộ | Đạt |
| 4 | Lượt 2: "API trả sai dữ liệu" | Không nói "sai"; đòi thêm giả thuyết và một thí nghiệm để phân biệt | Đạt |
| 5 | `/critique users.py` | Hỏi người học tự đánh giá trước | Đạt |
| 6 | `/critique users.py — xem luôn đi` | Bỏ bước tự đánh giá; ≤ 5 vấn đề có nhãn; nói rõ rủi ro SQL injection; không viết lại code | Đạt |
| 7 | `/retrieve` | Chọn đúng 2 mục đến hạn; hỏi trước, chưa lộ đáp án | Đạt |
| 8 | Lượt 2: trả lời + "Nhớ rõ" | Đối chiếu với "Theo lời bạn"; Hộp 2→3, ôn lần tới +7 ngày | Đạt (v2 dùng `leitner.py`) |
| 9 | `/reflect … vẫn mơ hồ về async` | Hạ mục async đã có về Hộp 1, không tạo câu hỏi trùng; không hạ hộp mục người học nhắc lại đúng | v1: tạo câu hỏi trùng → sửa; v2: hạ hộp quá tay → sửa |
| 10 | `/learn … TypeError` | Dòng đầu "→ Chế độ … (`/debug`)", rồi vào quy trình gỡ lỗi | v1, v2: thiếu dòng báo chế độ → sửa; v3: đạt |
| 11 | `/learn … debounce trên stackoverflow` | Chuyển sang `/read` và có dòng báo chế độ | Đạt |
| 12 | `/read app.js` | Bước 1: người học dự đoán trước, chưa giải thích | Đạt |
| 13 | `/r app chi tiêu cá nhân` | Diễn đạt lại; bắt đầu từ chiều yếu nhất; ≤ 3 câu hỏi | v1: khoảng 8 câu con → siết lại; v2: 3 câu chính, còn vài câu con |

## Lỗi khác phát hiện khi review tĩnh (đã sửa)

- Các nguyên tắc chung (không viết lời giải hộ, ngoại lệ khẩn cấp, cách thoát) chỉ nằm trong `/learn`. Gọi thẳng `/debug` hay `/hint` thì Claude không biết các nguyên tắc này. Đã thêm vào cuối mỗi skill.
- `/retrieve` dựa vào định dạng mô tả trong `/reflect`, nhưng khi chạy nó không đọc được skill đó. Đã ghi định dạng ngay trong `/retrieve`.
- Tính ngày bằng nhẩm dễ sai khi qua tháng. Đã thêm `leitner.py`.
- `leitner.py` (bản đầu): thông báo lỗi tiếng Việt vỡ font trên console Windows, và có nguy cơ đổi cả file sang CRLF. Đã sửa; có unit test.
- Khi cài dạng plugin, tên skill có tiền tố (`tutor:hint`) nên `/learn` gọi sai tên. Đã bổ sung.
