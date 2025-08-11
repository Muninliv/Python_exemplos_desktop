import tkinter as tk

def mostrar_mensagem():
    #obtém o texto da caixa de entrada 
    texto = caixa_texto.get()
    # Atualiza o rótulo com o texto da caixa de entrada
    label_resultado.config(text=texto)

# Criação da janela principal
janela = tk.Tk()
janela.title("Exemplo de Interface")
janela.geometry("400x150")

# Configuração da cor de fundo da janela
janela.configure(bg="green")

# Criação de uma caixa de entrada
caixa_texto = tk.Entry(janela, width=60)
caixa_texto.pack(pady=10)

# Criação de um botão
botao = tk.Button(janela, text="Mostrar Texto", command=mostrar_mensagem, bg="blue", fg="white")
botao.pack(pady=5)

# Criação de um rótulo para exibir o resultado
label_resultado = tk.Label(janela, text="")
label_resultado.pack(pady=10)

# Inicia o loop principal da interface
janela.mainloop()