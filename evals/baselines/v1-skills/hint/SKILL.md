---
name: hint
description: Thang gợi ý 7 cấp (0–6) cho người học bị bế tắc khi code — đi từ câu hỏi giúp tự đặt giả thuyết, đến khái niệm, vị trí, chiến lược, khung, code khuyết, và chỉ đưa lời giải đầy đủ ở cấp 6. Dùng khi người dùng gõ /hint, hoặc đang ở chế độ học (/learn) và nói "bí rồi", "gợi ý đi", "kẹt chỗ này". Không dùng khi người dùng chỉ muốn code chạy được ngoài chế độ học.
argument-hint: "[0-6] [mô tả chỗ đang kẹt]"
---

# /hint — Thang gợi ý

Đầu vào: `$ARGUMENTS`

Mục đích: cho đúng **lượng trợ giúp tối thiểu** để người học tự đi tiếp được. Trợ giúp quá ít → nản và bỏ cuộc; quá nhiều → không học được gì (nghịch lý trợ giúp — *assistance dilemma*). Thang gợi ý giải quyết bằng cách tăng dần, mỗi lần một nấc.

## Bước 1 — Hiểu vấn đề trước khi gợi ý

Âm thầm đọc code liên quan, lỗi, ngữ cảnh. Tự xác định lời giải đúng và **ý tưởng then chốt** (key insight) mà người học đang thiếu. Mọi cấp gợi ý đều dẫn về ý tưởng đó; gợi ý sai hướng còn tệ hơn không gợi ý.

## Bước 2 — Xác định cấp

- Đối số có số `0`–`6` → dùng đúng cấp đó.
- Đã có gợi ý trước đó cho **cùng vấn đề** trong phiên → lên một cấp so với lần trước.
- Vấn đề mới → bắt đầu từ cấp 0. Nếu người học đã tự nêu một giả thuyết rõ ràng, bắt đầu từ cấp 1.

Trước khi lên cấp, nếu người học chưa phản hồi gì về gợi ý trước, hỏi một dòng: "Với gợi ý vừa rồi bạn đã thử gì?" — lý do: chính nỗ lực giữa các nấc mới tạo ra việc học. Nhưng nếu họ vẫn muốn lên cấp, cứ lên; đừng biến việc này thành rào cản.

## Bước 3 — Các cấp

| Cấp | Tên | Bạn đưa gì | Không được đưa |
|---|---|---|---|
| 0 | Giả thuyết | Câu hỏi khiến người học tự nêu: điều gì đang xảy ra, họ mong đợi gì, đã loại trừ được gì | Bất kỳ manh mối nào về đáp án |
| 1 | Khái niệm | Tên khái niệm/lĩnh vực liên quan ("đây là chuyện phạm vi biến trong closure") và một câu hỏi về nó | Vị trí lỗi |
| 2 | Vị trí | File, hàm, khoảng dòng cần nhìn, và *nên quan sát điều gì* ở đó | Cách sửa |
| 3 | Chiến lược | Hướng giải bằng lời: các bước, công cụ nên dùng (log, debugger, test nhỏ) | Code |
| 4 | Khung | Pseudocode hoặc chữ ký hàm, cấu trúc — phần logic để trống | Code thật của phần then chốt |
| 5 | Code khuyết | Code thật, nhưng phần then chốt thay bằng `___` kèm chú thích gợi ý cho mỗi chỗ trống | Đáp án các chỗ trống |
| 6 | Lời giải | Code hoàn chỉnh + giải thích *vì sao* nó đúng + vì sao cách cũ sai | — |

Ở cấp 6, kết thúc bằng một yêu cầu tự giải thích hoặc biến thể nhỏ ("Thử viết lại cho trường hợp danh sách rỗng" / "Giải thích bằng lời của bạn vì sao dòng 3 cần thiết"). Đọc lời giải thì dễ quên; giải thích lại hoặc áp dụng sang biến thể mới khiến nó bám.

## Bước 4 — Định dạng trả lời

```
Gợi ý cấp N/6 — <Tên cấp>

<nội dung gợi ý, ngắn gọn>

👉 <một việc cụ thể để người học làm hoặc một câu hỏi để trả lời>

(Vẫn kẹt? Gõ /hint để lên cấp N+1.)
```

Ngắn là điều quan trọng: một gợi ý dài dòng thường vô tình lộ luôn cấp tiếp theo.

## Khi người học tự giải được

Dừng thang gợi ý. Hỏi một câu củng cố: "Lần sau gặp triệu chứng tương tự, dấu hiệu nào sẽ giúp bạn nhận ra nhanh hơn?" Ghi nhận cấp cao nhất đã dùng — đó là tín hiệu độ khó cho `/reflect` (cấp ≥ 4 nghĩa là khái niệm này nên được ôn lại).
