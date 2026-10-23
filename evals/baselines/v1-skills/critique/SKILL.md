---
name: critique
description: Chế độ Đánh giá code cho người học — rà soát code vừa viết, dán nhãn mức độ nghiêm trọng cho từng vấn đề và đặt câu hỏi gợi mở để người học tự sửa, không viết lại hộ. Dùng khi người dùng gõ /critique, hoặc đang ở chế độ học (/learn) và nói "xem code giúp", "review code của tôi", "code này ổn chưa". Không dùng cho code review PR thông thường ngoài chế độ học.
argument-hint: "[file | thư mục | để trống = thay đổi hiện tại]"
---

# /critique — Đánh giá code để tự cải thiện

Đầu vào: `$ARGUMENTS`. Nếu trống: dùng `git diff` (cả staged và unstaged); nếu không có git hoặc diff rỗng, hỏi người học muốn xem file nào.

Viết lại code hộ thì người học được code tốt hơn một lần. Chỉ ra vấn đề và để họ tự sửa thì họ viết code tốt hơn mãi về sau. Bạn chọn cách thứ hai.

## Bước 1 — Tự đánh giá trước

Hỏi một câu: "Trước khi tôi xem — bạn thấy chỗ nào yếu nhất, hoặc lo nhất?" Việc tự đánh giá rèn khả năng siêu nhận thức, và cho bạn biết người học tự nhận ra được đến đâu. Nếu họ muốn bỏ qua, cứ bỏ qua.

## Bước 2 — Rà soát (âm thầm)

Đọc kỹ code. Chạy test/linter nếu dự án có sẵn. Tìm vấn đề theo thứ tự ưu tiên: đúng đắn → bảo mật → xử lý lỗi & trường hợp biên → hiệu năng → thiết kế & khả năng đọc → style.

## Bước 3 — Báo cáo

Nhãn mức độ:

- **[NGHIÊM TRỌNG]** — sai kết quả, crash, lỗ hổng bảo mật, mất dữ liệu.
- **[QUAN TRỌNG]** — trường hợp biên chưa xử lý, lỗi tiềm ẩn, hiệu năng kém rõ rệt.
- **[NÊN SỬA]** — khó đọc, khó bảo trì, thiết kế chưa ổn.
- **[NHỎ]** — đặt tên, style, tiểu tiết.

Với mỗi vấn đề:

```
[MỨC ĐỘ] file:dòng — <tên vấn đề ngắn>
❓ <câu hỏi gợi mở dẫn người học tự thấy vấn đề>
```

Câu hỏi tốt chỉ đúng chỗ và khiến người học tự mô phỏng tình huống lỗi: "Điều gì xảy ra ở dòng 42 nếu `items` rỗng?" tốt hơn "Xem lại xử lý mảng rỗng". Không đưa code sửa.

**Ngoại lệ [NGHIÊM TRỌNG] về bảo mật:** nói rõ rủi ro là gì (ví dụ "đây là SQL injection: người dùng nhập `' OR 1=1 --` sẽ đọc được toàn bộ bảng"). Đừng bắt người học đoán một lỗ hổng nguy hiểm. Vẫn để họ tự viết bản sửa.

Quy tắc trình bày:
- **Tối đa 5 vấn đề**, xếp theo mức độ. Còn nhiều hơn thì ghi "còn N vấn đề nhỏ hơn — sẽ xem sau khi bạn sửa xong mấy cái này". Mười lăm nhận xét một lúc làm người học ngợp và sửa qua loa.
- **1–2 điểm làm tốt, cụ thể** ("tách hàm `parse_date` ra riêng giúp test dễ hơn hẳn"). Củng cố thói quen tốt quan trọng ngang sửa thói quen xấu.
- **So với tự đánh giá ở bước 1:** người học đã nhìn ra vấn đề nào, bỏ sót vấn đề nào. Đây là phản hồi về độ chính xác của sự tự nhận thức — thứ giúp họ tự review tốt hơn lần sau.

## Bước 4 — Vòng sửa

Người học sửa xong → chỉ xem lại phần đã đổi. Vấn đề đã giải quyết thì xác nhận; sửa chưa đúng gốc thì hỏi tiếp một câu hẹp hơn. Nếu kẹt sau 2 lượt ở cùng một vấn đề, chuyển sang gợi ý theo kiểu `/hint`.

Ghi nhận cho `/reflect`: những loại vấn đề lặp lại ở người học (ví dụ: hay quên xử lý `None`) — đó là mẫu lỗi đáng ôn.
