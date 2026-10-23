### C-{{dc-7}}-01 · Mutable default argument trong Python
- Hộp: 2 | Ôn lần tới: {{d-4}} | Ôn lần cuối: {{d-7}}
- Câu hỏi ôn: Vì sao `def f(x=[])` có thể gây lỗi khó hiểu khi gọi f nhiều lần?
- Theo lời bạn: list mặc định được tạo một lần lúc định nghĩa hàm, các lần gọi dùng chung nó
- Ví dụ: `def add(x, acc=[]): acc.append(x); return acc`
- Nguồn: sessions/{{d-7}}-cart.md

### C-{{dc-2}}-01 · async/await và Promise
- Hộp: 3 | Ôn lần tới: {{d+6}} | Ôn lần cuối: {{d-1}}
- Câu hỏi ôn: `res.json()` trả về gì và vì sao cần await?
- Theo lời bạn: trả về Promise, không await thì nhận Promise chứ không phải dữ liệu
- Ví dụ: `const data = await res.json()`
- Nguồn: sessions/{{d-2}}-profile.md
