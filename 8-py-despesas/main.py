import customtkinter as ctk
import sqlite3

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Banco de dados
conn = sqlite3.connect('financeiro.db')
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS transacoes (
    id INTEGER PRIMARY KEY,
    tipo TEXT NOT NULL,
    descricao TEXT NOT NULL,
    valor REAL NOT NULL
)
""")
conn.commit()

def format_money(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_next_id():
    cursor.execute("SELECT id FROM transacoes ORDER BY id")
    ids = [row[0] for row in cursor.fetchall()]
    next_id = 1
    for i in range(1, len(ids) + 2):
        if i not in ids:
            next_id = i
            break
    return next_id

class FinanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gerenciador de Despesas Pessoais")
        self.geometry("500x600")
        self.resizable(True, True)
        self.create_widgets()
        self.load_transactions()
        self.update_balance()

    def create_widgets(self):
        self.label_title = ctk.CTkLabel(self, text="Controle Financeiro", font=("Arial", 22, "bold"))
        self.label_title.pack(pady=20)

        self.balance_var = ctk.StringVar(value="R$ 0,00")
        self.label_balance = ctk.CTkLabel(self, textvariable=self.balance_var, font=("Arial", 18))
        self.label_balance.pack(pady=10)

        self.feedback_var = ctk.StringVar(value="")
        self.label_feedback = ctk.CTkLabel(self, textvariable=self.feedback_var, text_color="red", font=("Arial", 12))
        self.label_feedback.pack(pady=2)

        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(pady=10, padx=20, fill="x")

        self.option_tipo = ctk.CTkOptionMenu(self.frame_form, values=["Receita", "Despesa"])
        self.option_tipo.set("Receita")
        self.option_tipo.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.entry_desc = ctk.CTkEntry(self.frame_form, placeholder_text="Descrição")
        self.entry_desc.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.entry_valor = ctk.CTkEntry(self.frame_form, placeholder_text="Valor (ex: 100.50)")
        self.entry_valor.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.frame_form.grid_columnconfigure(0, weight=1)
        self.frame_form.grid_columnconfigure(1, weight=3)
        self.frame_form.grid_columnconfigure(2, weight=2)

        self.button_add = ctk.CTkButton(self, text="Adicionar", command=self.add_transaction)
        self.button_add.pack(pady=5)

        self.frame_hist = ctk.CTkFrame(self)
        self.frame_hist.pack(pady=12, padx=20, fill="both", expand=True)

        self.label_hist = ctk.CTkLabel(self.frame_hist, text="Histórico de Transações", font=("Arial", 14, "bold"))
        self.label_hist.pack()

        self.listbox = ctk.CTkTextbox(self.frame_hist, font=("Arial", 12))
        self.listbox.pack(pady=5, fill="both", expand=True)
        self.listbox.configure(state="disabled")

        self.entry_del_id = ctk.CTkEntry(self, placeholder_text="ID para excluir")
        self.entry_del_id.pack(pady=2)

        self.button_delete = ctk.CTkButton(self, text="Excluir", fg_color="red", command=self.delete_transaction)
        self.button_delete.pack(pady=2)

    def add_transaction(self):
        tipo = self.option_tipo.get()
        desc = self.entry_desc.get()
        valor = self.entry_valor.get().replace(",", ".")

        try:
            valor = float(valor)
            if not desc:
                raise ValueError("Descrição vazia.")
            # ID manual
            next_id = get_next_id()
            cursor.execute("INSERT INTO transacoes (id, tipo, descricao, valor) VALUES (?, ?, ?, ?)",
                           (next_id, tipo, desc, valor))
            conn.commit()
            self.feedback_var.set(f"Transação adicionada com sucesso! (ID: {next_id})")
            self.entry_desc.delete(0, "end")
            self.entry_valor.delete(0, "end")
            self.load_transactions()
            self.update_balance()
        except Exception as e:
            self.feedback_var.set(f"Erro: {str(e)}")

    def load_transactions(self):
        self.listbox.configure(state="normal")
        self.listbox.delete("1.0", "end")
        cursor.execute("SELECT id, tipo, descricao, valor FROM transacoes ORDER BY id")
        rows = cursor.fetchall()
        for row in rows:
            line = f"ID: {row[0]} | {row[1]} | {row[2]} | {format_money(row[3])}\n"
            self.listbox.insert("end", line)
        if not rows:
            self.listbox.insert("end", "Nenhuma transação cadastrada.")
        self.listbox.configure(state="disabled")

    def delete_transaction(self):
        id_trans = self.entry_del_id.get()
        try:
            cursor.execute("DELETE FROM transacoes WHERE id=?", (id_trans,))
            if cursor.rowcount == 0:
                self.feedback_var.set("ID não encontrado.")
            else:
                conn.commit()
                self.feedback_var.set("Transação excluída!")
                self.entry_del_id.delete(0, "end")
                self.load_transactions()
                self.update_balance()
        except Exception as e:
            self.feedback_var.set(f"Erro: {str(e)}")

    def update_balance(self):
        cursor.execute("SELECT SUM(CASE WHEN tipo='Receita' THEN valor ELSE -valor END) FROM transacoes")
        saldo = cursor.fetchone()[0]
        saldo = saldo if saldo is not None else 0.0
        self.balance_var.set(format_money(saldo))
        if saldo >= 0:
            self.label_balance.configure(text_color="#35a964")
        else:
            self.label_balance.configure(text_color="#e43c3c")

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()