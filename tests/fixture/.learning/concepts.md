### C-20261015-01 · Mutable default argument trong Python
- Hộp: 2 | Ôn lần tới: 2026-10-18 | Ôn lần cuối: 2026-10-15
- Câu hỏi ôn: Vì sao `def f(x=[])` có thể gây lỗi khó hiểu khi gọi f nhiều lần?
- Theo lời bạn: list mặc định được tạo một lần lúc định nghĩa hàm, các lần gọi dùng chung nó
- Ví dụ: `def add(x, acc=[]): acc.append(x); return acc`
- Nguồn: sessions/2026-10-15-cart.md

### C-20261020-01 · async/await và Promise
- Hộp: 3 | Ôn lần tới: 2026-10-28 | Ôn lần cuối: 2026-10-21
- Câu hỏi ôn: `res.json()` trả về gì và vì sao cần await?
- Theo lời bạn: trả về Promise, không await thì nhận Promise chứ không phải dữ liệu
- Ví dụ: `const data = await res.json()`
- Nguồn: sessions/2026-10-20-profile.md
