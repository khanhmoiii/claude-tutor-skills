---
name: retrieve
description: Ôn tập đầu buổi học bằng cách tự nhớ lại (retrieval practice) và lặp lại ngắt quãng (Leitner) — đọc sổ học tập .learning/, hỏi những khái niệm và lỗi sai đến hạn ôn, người học trả lời trước rồi mới đối chiếu, sau đó cập nhật lịch ôn. Dùng khi người dùng gõ /retrieve, hoặc đang ở chế độ học (/learn) và nói "ôn bài", "hôm trước học gì", "bắt đầu buổi học".
argument-hint: "[chủ đề muốn ôn | all]"
---

# /retrieve — Ôn tập bằng cách tự nhớ lại

Đầu vào: `$ARGUMENTS`

Nỗ lực nhớ lại — kể cả khi nhớ sai rồi được sửa — củng cố trí nhớ mạnh hơn nhiều so với đọc lại ghi chú (hiệu ứng kiểm tra, *testing effect*). Vì vậy **luôn hỏi trước, đối chiếu sau**; không bao giờ hiển thị nội dung ghi chú trước khi người học trả lời.

## Bước 1 — Đọc sổ

Tìm `.learning/` ở gốc dự án (gốc git nếu có, nếu không thì thư mục hiện tại). Nếu không có hoặc rỗng: nói rằng chưa có gì để ôn, gợi ý dùng `/reflect` cuối buổi học này, rồi hỏi hôm nay người học định làm gì (và có thể chuyển sang `/learn`).

Mỗi mục trong `concepts.md` và `mistakes.md` có dạng (do `/reflect` ghi):

```markdown
### C-20261022-01 · Tiêu đề
- Hộp: 1 | Ôn lần tới: 2026-10-23 | Ôn lần cuối: —
- Câu hỏi ôn: ...
- Theo lời bạn: ...        (mục lỗi sai: Triệu chứng / Nguyên nhân gốc / Cách nhận ra lần sau)
```

Lấy danh sách đến hạn bằng script đi kèm skill này. Đừng tự so sánh ngày bằng mắt: rất dễ sai khi qua tháng.

```bash
python <thư-mục-skill-này>/scripts/leitner.py due            # mục đến hạn hôm nay + thống kê theo hộp
python <thư-mục-skill-này>/scripts/leitner.py due --all      # mọi mục
```

(Đường dẫn thư mục skill được báo khi skill nạp. Chạy ở gốc dự án, hoặc thêm `--dir <đường-dẫn>/.learning`. Không có Python thì đọc file và so ngày cẩn thận.) Sau đó đọc nội dung đầy đủ của các mục được chọn, `open-questions.md`, và nhật ký mới nhất trong `sessions/`.

## Bước 2 — Chọn mục

- Có chủ đề trong đối số → chọn các mục liên quan chủ đề đó, bất kể hạn ôn.
- `all` → mọi mục, ưu tiên hộp thấp.
- Mặc định → các mục script báo đến hạn (đã xếp sẵn: hộp thấp và quá hạn lâu nhất lên đầu).

Lấy **3–5 mục**, trộn khái niệm với lỗi sai (xen kẽ — *interleaving* — giúp phân biệt các ý dễ nhầm). Nếu không có mục nào đến hạn, nói vậy và đề nghị ôn sớm 2 mục ở hộp thấp nhất, hoặc bỏ qua.

## Bước 3 — Hỏi từng mục

Mỗi lượt một câu. Dùng `Câu hỏi ôn` đã lưu làm gốc, nhưng có thể biến tấu để tránh học thuộc câu chữ:
- Giải thích khái niệm bằng lời của mình.
- Dự đoán kết quả một đoạn code ngắn (bạn tự viết đoạn mới, minh họa cùng khái niệm).
- Cho triệu chứng, hỏi nguyên nhân khả dĩ và cách kiểm tra (với mục lỗi sai).
- Áp dụng vào dự án hiện tại: "Trong code của bạn, chỗ nào có thể dính lỗi này?"

Sau khi người học trả lời:
1. Đối chiếu với ghi chú (kể cả phần "Theo lời bạn" — cho họ thấy mình đã hiểu thế nào hôm trước).
2. Phản hồi cụ thể: đúng ở đâu, thiếu gì, sai gì. Nếu sai, giải thích ngắn rồi hỏi lại bằng một câu khác.
3. Hỏi tự đánh giá: **Nhớ rõ / Mơ hồ / Quên**. Có thể gợi ý mức dựa trên câu trả lời, nhưng người học quyết định.

Nếu người học nói "không nhớ" ngay: khuyến khích đoán thử một câu trước khi xem đáp án — một lần đoán sai rồi được sửa vẫn có giá trị hơn xem đáp án luôn.

## Bước 4 — Cập nhật lịch ôn (hộp Leitner)

| Tự đánh giá | Hộp mới |
|---|---|
| Nhớ rõ | Hộp + 1 (tối đa 5) |
| Mơ hồ | Giữ nguyên hộp |
| Quên | Về Hộp 1 |

`Ôn lần tới` = hôm nay + khoảng cách theo hộp mới: Hộp 1 → 1 ngày · Hộp 2 → 3 ngày · Hộp 3 → 7 ngày · Hộp 4 → 16 ngày · Hộp 5 → 35 ngày. Script cập nhật đúng dòng đó:

```bash
python <thư-mục-skill-này>/scripts/leitner.py grade C-20261022-01 nho   # nho | mo | quen
```

Nếu người học diễn đạt tốt hơn trước, tự sửa thêm dòng "Theo lời bạn" của mục đó.

## Bước 5 — Câu hỏi bỏ ngỏ và chuyển sang buổi học

Nêu tối đa 1–2 câu hỏi còn `mở` trong `open-questions.md`: "Câu này giờ bạn đã trả lời được chưa?" Nếu được, đổi trạng thái thành `đã giải đáp` kèm câu trả lời ngắn của người học; nếu nó đã thành kiến thức rõ ràng, đề nghị chuyển sang `concepts.md`.

Kết thúc: một dòng tổng kết (ví dụ "4 mục: 2 nhớ rõ, 1 mơ hồ, 1 quên"), nhắc gợi ý từ nhật ký buổi trước nếu có, rồi hỏi hôm nay người học định làm gì.
