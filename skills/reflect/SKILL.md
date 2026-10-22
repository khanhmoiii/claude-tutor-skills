---
name: reflect
description: Tổng kết cuối buổi học — người học tự nhắc lại điều đã học, rồi Claude ghi khái niệm, lỗi sai (kèm nguyên nhân gốc) và câu hỏi bỏ ngỏ vào sổ học tập .learning/ để /retrieve ôn lại ở các phiên sau. Dùng khi người dùng gõ /reflect, hoặc đang ở chế độ học (/learn) và nói "xong rồi", "hôm nay vậy thôi", "tổng kết buổi học", "lưu lại những gì đã học".
argument-hint: "[ghi chú thêm]"
---

# /reflect — Tổng kết và lưu sổ học tập

Đầu vào: `$ARGUMENTS`

Ghi chép là nguyên liệu cho `/retrieve`. Sổ học tập tốt ghi bằng **lời của người học** và kèm sẵn **câu hỏi ôn**, vì thứ được ôn bằng cách tự nhớ lại (retrieval practice) bám lâu hơn nhiều so với đọc lại ghi chú.

## Bước 1 — Người học tự nhớ lại trước

Hỏi: "Trước khi tôi tổng kết: kể 2–3 điều bạn học được hôm nay, và một chỗ bạn vẫn còn mơ hồ." Tự nhớ lại ngay cuối buổi là một lần ôn đầu tiên — đừng bỏ qua bước này để tiết kiệm thời gian. Nếu người học muốn bỏ qua, tôn trọng.

## Bước 2 — Bổ sung từ những gì bạn quan sát

Rà lại phiên học và đối chiếu với câu trả lời của người học:
- **Khái niệm** mới hoặc vừa hiểu sâu hơn.
- **Lỗi sai**: triệu chứng, nguyên nhân gốc, cách nhận ra lần sau. Ưu tiên lỗi về tư duy/khái niệm hơn lỗi gõ nhầm.
- **Câu hỏi bỏ ngỏ** chưa được giải đáp.
- **Tín hiệu độ khó**: chỗ phải dùng `/hint` cấp ≥ 4, chỗ debug lâu, chiều thiết kế bị bỏ sót trong `/r`, mẫu lỗi lặp lại trong `/critique`.

**Đối chiếu với sổ cũ trước khi tạo mục mới.** Đọc `.learning/` (nếu có). Khi người học mơ hồ hoặc sai về một thứ **đã có trong sổ**, đó không phải câu hỏi mới. Đó là dấu hiệu mục cũ chưa vững: hạ mục đó về Hộp 1 (xem bước 3) thay vì tạo câu hỏi bỏ ngỏ trùng nội dung. Chỉ ghi vào `open-questions.md` những thắc mắc thật sự chưa có lời giải trong sổ.

Đưa danh sách đề xuất (ngắn, dạng gạch đầu dòng) cho người học xem, hỏi có muốn thêm/bớt/sửa gì không. Chỉ lưu những gì đáng ôn — mười mục nhạt kém hơn ba mục chất.

## Bước 3 — Ghi vào sổ

Thư mục: `.learning/` ở gốc dự án (gốc git nếu có, nếu không thì thư mục hiện tại). Tạo nếu chưa có. Lần đầu tạo, nói với người học một dòng rằng có thể thêm `.learning/` vào `.gitignore` nếu không muốn commit.

```
.learning/
├── concepts.md          # khái niệm
├── mistakes.md          # lỗi sai
├── open-questions.md    # câu hỏi bỏ ngỏ
└── sessions/
    └── YYYY-MM-DD-<chủ-đề>.md   # nhật ký từng buổi
```

Thêm mục mới vào **cuối** file (không ghi đè mục cũ), cách mục trước một dòng trống. Nếu khái niệm/lỗi đã có sẵn, cập nhật mục cũ thay vì tạo trùng:
- Người học **mắc lại** lỗi đó, hoặc **mơ hồ/sai** về khái niệm đó → đặt `Hộp: 1`, `Ôn lần tới` = ngày mai, `Ôn lần cuối` = hôm nay.
- Người học chỉ **dùng đúng** hoặc nhắc lại đúng → giữ nguyên lịch. Hạ hộp lúc này sẽ phạt đúng thứ họ đã nhớ.

Nếu người học vừa diễn đạt lại tốt hơn, cập nhật luôn dòng "Theo lời bạn".

**Ngày và ID — đừng tính nhẩm.** Lấy ngày hôm nay từ ngữ cảnh; không chắc thì chạy `date +%F`. Để lấy ID kế tiếp không trùng, dùng script của skill `retrieve` (thư mục anh em với skill này; đường dẫn gốc của skill hiện tại được báo khi skill nạp):

```bash
python <thư-mục-skill-này>/../retrieve/scripts/leitner.py next-id C   # hoặc M, Q
```

Không chạy được (không có Python, không tìm thấy script) thì tìm ID lớn nhất cùng ngày trong file và cộng 1.

### Định dạng mục (giữ chính xác — `/retrieve` đọc theo định dạng này)

**concepts.md** — ID dạng `C-YYYYMMDD-NN`:
```markdown
### C-20261022-01 · Closure trong vòng lặp
- Hộp: 1 | Ôn lần tới: 2026-10-23 | Ôn lần cuối: —
- Câu hỏi ôn: Vì sao các callback tạo trong `for (var i ...)` đều in ra cùng một giá trị?
- Theo lời bạn: <câu người học tự diễn đạt, giữ nguyên giọng của họ>
- Ví dụ: <đoạn code ngắn hoặc tình huống cụ thể>
- Nguồn: sessions/2026-10-22-auth-bug.md
```

**mistakes.md** — ID dạng `M-YYYYMMDD-NN`:
```markdown
### M-20261022-01 · Gọi API trước khi token được làm mới
- Hộp: 1 | Ôn lần tới: 2026-10-23 | Ôn lần cuối: —
- Câu hỏi ôn: Request trả 401 ngẫu nhiên sau khoảng 1 giờ — bạn nghi ngờ gì đầu tiên và kiểm tra thế nào?
- Triệu chứng: ...
- Nguyên nhân gốc: ...
- Cách nhận ra lần sau: ...
- Nguồn: sessions/2026-10-22-auth-bug.md
```

**open-questions.md** — ID dạng `Q-YYYYMMDD-NN`:
```markdown
### Q-20261022-01 · Khi nào nên dùng refresh token xoay vòng?
- Trạng thái: mở | Ngày: 2026-10-22
- Ngữ cảnh: ...
```

**sessions/YYYY-MM-DD-<chủ-đề>.md** — nhật ký ngắn: mục tiêu buổi học, đã làm gì, các ID mục mới tạo/cập nhật, gợi ý bắt đầu buổi sau.

Câu hỏi ôn phải **trả lời được mà không cần xem code hôm nay** và kiểm tra sự hiểu, không kiểm tra trí nhớ vẹt ("Vì sao…", "Điều gì xảy ra nếu…", "Bạn sẽ kiểm tra thế nào…" — tránh "Hàm X nằm ở dòng nào").

Lịch ôn theo hộp Leitner: mục mới luôn vào Hộp 1, ôn lần tới = ngày mai.

## Bước 4 — Kết

Một dòng tóm tắt: đã lưu bao nhiêu mục, và nhắc "Buổi sau bắt đầu bằng `/retrieve` để ôn lại nhé."
