# Kiểm chứng giám khảo

Giám khảo LLM cũng có thể sai, nên cần đối chiếu nó với một người chấm độc lập trên một mẫu ngẫu nhiên.

**Cách làm:** lấy ngẫu nhiên 20 lượt chấm `judge` (seed 7) từ `results/20261022-2121-current.json`. Người chấm thứ hai đọc câu trả lời gốc và tiêu chí, tự kết luận đạt/không đạt mà không nhìn lý do của giám khảo trước, rồi mới so sánh.

**Người chấm thứ hai:** Claude Opus 5.5 (cũng là tác giả bộ skill), **chưa phải người thật**. Vì cùng họ model với giám khảo, mức đồng thuận dưới đây có thể bị thổi phồng. Nên có một người tự chấm lại cột "Người chấm 2"; cách lấy mẫu được ghi ở cuối file.

**Kết quả: đồng ý 19/20 (95%).**

| # | Ca | Tiêu chí | Giám khảo | Người chấm 2 | Ghi chú |
|---|---|---|---|---|---|
| S1 | hint-learner-solves#3 | H10 | ❌ | ❌ | Hỏi hai câu, câu thứ hai mở vấn đề mới (`discounts=[]`) |
| S2 | debug-stuck#2 | D5 | ✅ | ✅ | Đổi cách tiếp cận. Thực ra đi quá tay, giải thích gần hết chẩn đoán |
| S3 | hint-new-escalate#2 | X1 | ✅ | ✅ | |
| S4 | read-basic#2 | R5 | ✅ | ✅ | |
| S5 | critique-direct#2 | K9 | ❌ | ✅ | **Bất đồng.** "Cursor không đóng" là chuyện nhỏ nhưng có thật và đã gắn nhãn NHỎ. Giám khảo còn đọc sai số dòng (cho rằng phép chia ở dòng 11, thực tế là dòng 10) |
| S6 | critique-direct#3 | K8 | ✅ | ✅ | |
| S7 | retrieve-good#1 | V1 | ✅ | ✅ | |
| S8 | r-vague#1 | RR3 | ✅ | ✅ | |
| S9 | debug-emergency#1 | X7 | ✅ | ✅ | |
| S10 | hint-new-escalate#1 | H6 | ✅ | ✅ | Ở ranh giới: có nhắc "off-by-one" nhưng chưa lộ cách sửa |
| S11 | r-vague#3 | RR1 | ✅ | ✅ | |
| S12 | critique-direct#2 | K10 | ✅ | ✅ | |
| S13 | r-small#2 | RR6 | ✅ | ✅ | |
| S14 | debug-trace#2 | D4 | ❌ | ❌ | Không đòi giả thuyết thứ hai |
| S15 | critique-direct#2 | K7 | ✅ | ✅ | |
| S16 | critique-direct#3 | K10 | ✅ | ✅ | |
| S17 | learn-ambiguous#2 | L4 | ✅ | ✅ | |
| S18 | hint-new-escalate#3 | X1 | ✅ | ✅ | |
| S19 | critique-direct#3 | K7 | ✅ | ✅ | |
| S20 | debug-trace#3 | D3 | ✅ | ✅ | |

**Nhận xét:**
- Giám khảo đáng tin với các tiêu chí về hành vi, ví dụ có lộ đáp án không, có hỏi giả thuyết không.
- Giám khảo kém tin hơn với K9 (có bịa lỗi không), vì tiêu chí này đòi đọc code chính xác. Kết quả K9 nên được xem lại bằng tay.

Lấy lại đúng mẫu này (in kèm câu trả lời gốc và chỗ trống để tự chấm):

```bash
python evals/run_evals.py sample evals/results/20261022-2121-current.json --n 20 --seed 7 > my-calibration.md
```
