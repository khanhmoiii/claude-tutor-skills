# Evals — đo hành vi của bộ skill

Bộ eval chạy các cuộc hội thoại thật với Claude Code, rồi chấm câu trả lời theo các tiêu chí rút từ chính các file `SKILL.md`. Mục đích: biết chắc một lần sửa skill làm nó tốt lên hay tệ đi, thay vì đọc bằng mắt.

## Cách hoạt động

```
cases/*.toml ──► 1. CHẠY: claude -p (từng lượt, --resume)  ──► câu trả lời + file .learning/ sau khi chạy
                  2. CHẤM bằng code: regex, đếm, trạng thái sổ học tập, file code có bị sửa không
                  3. CHẤM bằng giám khảo: một lượt claude -p khác trả lời có/không cho từng tiêu chí
                  4. TỔNG HỢP: tỉ lệ đạt theo tiêu chí ──► results/<ngày>-<nhãn>.json + .md
```

Mỗi lần chạy diễn ra trong một thư mục riêng (`.work/`) chứa dự án mẫu (`fixture/`) và đúng bộ skill cần đo. Lệnh luôn chạy với `--setting-sources project`, để skill đã cài toàn cục trong `~/.claude/skills` không lấn át bộ skill đang đo.

Ngày trong sổ học tập mẫu là ngày tương đối (`{{d-7}}`, `{{d+1}}`, `{{dc}}` là dạng `YYYYMMDD`) và được thay bằng ngày thật lúc chạy, nên eval cho kết quả đúng vào bất kỳ hôm nào.

## Chạy

```bash
python evals/run_evals.py run                          # tất cả ca, 3 lần mỗi ca, model sonnet
python evals/run_evals.py run --case hint debug        # chỉ các ca có id chứa "hint" hoặc "debug"
python evals/run_evals.py run --skills evals/baselines/v1-skills --label v1
python evals/run_evals.py report  evals/results/<file>.json
python evals/run_evals.py compare evals/results/A.json evals/results/B.json
```

Tùy chọn: `--runs N`, `--model`, `--judge-model`, `--workers` (số hội thoại chạy song song, mặc định 6).

Chi phí: một lần chạy đầy đủ là khoảng 100 hội thoại, cộng thêm các lượt chấm.

## Ngưỡng đạt

LLM trả lời khác nhau giữa các lần chạy, nên mỗi ca chạy 3 lần:

- **Tiêu chí quan trọng** (`critical = true`: không lộ đáp án, không sửa file code của người học) phải đạt **3/3**.
- **Các tiêu chí còn lại** phải đạt **≥ 2/3**.

## Định dạng ca kiểm thử

```toml
[[case]]
id = "hint-jump-5"
learning = "default"        # default | notdue | none — sổ học tập mẫu
allow_edits = false         # true: bỏ qua kiểm tra X5 (file code không đổi)
context = "Sự thật ẩn cho giám khảo: lỗi nằm ở đâu, sửa thế nào"
turns = ["/hint 5 cart.py in ra 20.0 thay vì 120.0"]
checks = [
  { id = "H3", type = "regex", pattern = 'cấp 5\s*/\s*6' },
  { id = "H7", type = "judge", question = "Có tránh lộ đáp án của chỗ trống không?" },
]
```

| `type` | Kiểm tra |
|---|---|
| `regex` / `not_regex` | Có / không có mẫu trong câu trả lời ở lượt `turn` (mặc định lượt cuối) |
| `first_line` | Dòng đầu tiên khớp mẫu |
| `max_count` | Số lần xuất hiện của mẫu ≤ `max` |
| `no_code_block` | Không có khối code |
| `labels` | Nhãn mức độ của `/critique`: ≤ `max`, mỗi vấn đề có `❓`, xếp đúng thứ tự |
| `count_entries` | Số mục trong một file của `.learning/` |
| `entry` / `entry_any` | Hộp và ngày ôn của một mục (hoặc một trong các mục) sau khi chạy |
| `ids_valid` | Mọi ID trong sổ đúng định dạng, không trùng, có dòng lịch ôn hợp lệ |
| `file_regex` / `file_not_regex` | Nội dung file sau khi chạy |
| `judge` | Giám khảo LLM trả lời câu hỏi có/không (có thể kèm `file` để giám khảo đọc file đó) |

## Bản mốc

`baselines/v1-skills/` là bộ skill ban đầu, trước mọi lần sửa từ kiểm thử thủ công. Dùng nó để đo mức cải thiện.
