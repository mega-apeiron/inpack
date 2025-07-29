import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading

class PyToExeConverter:
    def __init__(self, master):
        self.master = master
        master.title("Py to EXE Converter")
        master.geometry("700x500") # Aumenta um pouco a janela
        ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

        self.project_path = ctk.StringVar()
        self.main_script = ctk.StringVar()
        self.output_name = ctk.StringVar()
        self.icon_path = ctk.StringVar()

        self._create_widgets()

    def _create_widgets(self):
        # Frame principal para organização
        main_frame = ctk.CTkFrame(self.master)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        main_frame.grid_columnconfigure(1, weight=1) # Faz a coluna do meio expandir

        # Project Path
        ctk.CTkLabel(main_frame, text="Caminho do Projeto:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(main_frame, textvariable=self.project_path, width=350).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(main_frame, text="Procurar Pasta", command=self._browse_project_path).grid(row=0, column=2, padx=10, pady=10)

        # Main Script
        ctk.CTkLabel(main_frame, text="Arquivo Principal (.py):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(main_frame, textvariable=self.main_script, width=350).grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(main_frame, text="Procurar Arquivo", command=self._browse_main_script).grid(row=1, column=2, padx=10, pady=10)

        # Output Name
        ctk.CTkLabel(main_frame, text="Nome do Executável:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(main_frame, textvariable=self.output_name, width=350).grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Icon Path
        ctk.CTkLabel(main_frame, text="Ícone (.ico):").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(main_frame, textvariable=self.icon_path, width=350).grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(main_frame, text="Procurar Ícone", command=self._browse_icon_path).grid(row=3, column=2, padx=10, pady=10)

        # Options Frame
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        options_frame.grid_columnconfigure(0, weight=1) # Centraliza os checkboxes

        self.onefile_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(options_frame, text="Gerar arquivo único (onefile)", variable=self.onefile_var).pack(pady=5, anchor="w")

        self.noconsole_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(options_frame, text="Sem janela de console (noconsole)", variable=self.noconsole_var).pack(pady=5, anchor="w")

        # Convert Button
        ctk.CTkButton(main_frame, text="Converter para EXE (PyInstaller)", command=self._start_conversion_thread,
                      font=ctk.CTkFont(size=16, weight="bold")).grid(row=5, column=0, columnspan=3, pady=20)


    def _browse_project_path(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.project_path.set(folder_selected)

    def _browse_main_script(self):
        file_selected = filedialog.askopenfilename(
            initialdir=self.project_path.get() if self.project_path.get() else os.getcwd(),
            filetypes=[("Python files", "*.py")]
        )
        if file_selected:
            self.main_script.set(file_selected)

    def _browse_icon_path(self):
        file_selected = filedialog.askopenfilename(filetypes=[("Icon files", "*.png"), ("PNG files", "*.png")]) # PyInstaller prefere .ico, mas png é comum
        if file_selected:
            self.icon_path.set(file_selected)

    def _validate_inputs(self):
        if not self.project_path.get():
            messagebox.showerror("Erro de Validação", "Por favor, selecione o caminho do projeto.")
            return False
        if not self.main_script.get():
            messagebox.showerror("Erro de Validação", "Por favor, selecione o arquivo principal (.py).")
            return False
        if not self.main_script.get().endswith(".py"):
            messagebox.showerror("Erro de Validação", "O arquivo principal deve ser um arquivo Python (.py).")
            return False
        if not os.path.exists(self.main_script.get()):
            messagebox.showerror("Erro de Validação", "O arquivo principal não foi encontrado.")
            return False
        return True

    def _start_conversion_thread(self):
        if not self._validate_inputs():
            return

        self.loading_popup = self._show_loading_popup("Iniciando conversão...")
        # Inicia a conversão em uma thread separada para não bloquear a GUI
        conversion_thread = threading.Thread(target=self._convert_pyinstaller)
        conversion_thread.start()

    def _show_loading_popup(self, message="Carregando..."):
        popup = ctk.CTkToplevel(self.master)
        popup.title("Processando...")
        popup.geometry("300x100")
        popup.transient(self.master) # Faz o popup ficar sempre em cima da janela principal
        popup.grab_set() # Bloqueia interações com a janela principal

        # Centraliza o popup
        self.master.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")


        ctk.CTkLabel(popup, text=message, font=ctk.CTkFont(size=14)).pack(pady=10)
        progress_bar = ctk.CTkProgressBar(popup, orientation="horizontal", mode="indeterminate")
        progress_bar.pack(pady=10, padx=20, fill="x")
        progress_bar.start()

        return popup

    def _convert_pyinstaller(self):
        command = ["pyinstaller", self.main_script.get()]

        if self.onefile_var.get():
            command.append("--onefile")
        if self.noconsole_var.get():
            command.append("--noconsole")
        if self.output_name.get():
            command.extend(["--name", self.output_name.get()])
        if self.icon_path.get():
            # PyInstaller prefere .ico, mas suporta PNG se o Pillow estiver instalado
            if not (self.icon_path.get().endswith(".ico") or self.icon_path.get().endswith(".png")):
                messagebox.showwarning("Aviso de Ícone", "O arquivo de ícone deve ser .ico ou .png.")
            else:
                command.extend(["--icon", self.icon_path.get()])

        original_cwd = os.getcwd()
        try:
            # Tenta mudar para o diretório do script principal ou do projeto
            target_dir = os.path.dirname(self.main_script.get()) if self.main_script.get() else self.project_path.get()
            if os.path.exists(target_dir) and os.path.isdir(target_dir):
                os.chdir(target_dir)
            else:
                os.chdir(self.project_path.get()) # Garante que está no diretório do projeto
            
            # Atualiza o popup para indicar que a compilação está ativa
            self.master.after(0, lambda: self.loading_popup.children["!ctklabel"].configure(text="Compilando..."))
            
            process = subprocess.run(command, capture_output=True, text=True, check=True)
            self.master.after(0, lambda: self.loading_popup.destroy()) # Fecha o popup na thread principal
            messagebox.showinfo("Sucesso", f"Conversão concluída com sucesso! Verifique a pasta 'dist' no seu projeto.")
            # O output e erro podem ser muito longos para uma messagebox. É melhor direcionar o usuário.
            # print(f"Output: {process.stdout}\nErro: {process.stderr}")
        except subprocess.CalledProcessError as e:
            self.master.after(0, lambda: self.loading_popup.destroy())
            messagebox.showerror("Erro de Conversão", f"Ocorreu um erro durante a conversão:\n{e.stderr}")
        except FileNotFoundError:
            self.master.after(0, lambda: self.loading_popup.destroy())
            messagebox.showerror("Erro", "PyInstaller não encontrado. Certifique-se de que está instalado e no PATH. (pip install pyinstaller)")
        except Exception as e:
            self.master.after(0, lambda: self.loading_popup.destroy())
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")
        finally:
            os.chdir(original_cwd) # Restaura o diretório original
            if self.loading_popup and self.loading_popup.winfo_exists(): # Garante que o popup é fechado mesmo em erro inesperado
                 self.master.after(0, lambda: self.loading_popup.destroy())
                 self.loading_popup = None # Limpa a referência


if __name__ == "__main__":
    app = ctk.CTk()
    converter_app = PyToExeConverter(app)
    app.mainloop()