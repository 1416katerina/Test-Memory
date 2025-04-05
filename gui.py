import customtkinter as ctk
from tkinter import messagebox
from functionality import evaluate_level, generate_sequence, save_result, analyze_results
import os

# Настройки интерфейса
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
FONT_LARGE = ("Arial", 28)
FONT_MEDIUM = ("Arial", 22)
FONT_SMALL = ("Arial", 18)
BUTTON_COLOR = "#9BB8FF"
HOVER_COLOR = "#7A9CFF"
TEXT_COLOR = "#333333"


class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🧠 Тести на увагу та пам'ять")
        self.geometry("1280x1024")
        self.minsize(1024, 768)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, fg_color="white")
        self.container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.frames = {}
        for F in (MenuFrame, TestFrame1, TestFrame2, InfoFrame, ResultsFrame):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MenuFrame)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()


class MenuFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white")
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self,
            text="🧠 Тести на увагу та пам'ять",
            font=FONT_LARGE,
            text_color=TEXT_COLOR
        )
        title.grid(row=0, column=0, pady=(40, 60))

        buttons = [
            ("🔢 Метод відтворення рядів", TestFrame1),
            ("🔄 Відтворення у зворотному порядку", TestFrame2),
            ("📝 Інфо", InfoFrame),
            ("📊 Результати", ResultsFrame),
        ]

        for i, (text, frame_class) in enumerate(buttons, start=1):
            button = ctk.CTkButton(
                self,
                text=text,
                font=FONT_MEDIUM,
                command=lambda fc=frame_class: self.controller.show_frame(fc),
                fg_color=BUTTON_COLOR,
                hover_color=HOVER_COLOR,
                height=70,
                corner_radius=15,
                text_color="white"
            )
            button.grid(row=i, column=0, pady=15, padx=150, sticky="ew")


class BaseTestFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, test_name, emoji):
        super().__init__(parent, fg_color="white")
        self.controller = controller
        self.test_name = f"{emoji} {test_name}"
        self.username = ""
        self.current_length = 4
        self.results = {}
        self.current_sequence = ""
        self.remaining_time = 5
        self.timer_id = None

        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkLabel(
            self,
            text=self.test_name,
            font=FONT_LARGE,
            text_color=TEXT_COLOR
        )
        self.header.grid(row=0, column=0, pady=(20, 30))

        self.name_frame = ctk.CTkFrame(self, fg_color="white")
        self.name_label = ctk.CTkLabel(
            self.name_frame,
            text="✏️ Введіть Ваше ім'я:",
            font=FONT_MEDIUM,
            text_color=TEXT_COLOR
        )
        self.name_label.pack(side="left", padx=10)

        self.name_entry = ctk.CTkEntry(
            self.name_frame,
            font=FONT_MEDIUM,
            width=300,
            border_width=2,
            fg_color="white"
        )
        self.name_entry.pack(side="left", padx=10)

        self.name_button = ctk.CTkButton(
            self.name_frame,
            text="🚀 Почати тест",
            font=FONT_MEDIUM,
            command=self.start_test,
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            height=60,
            text_color="white"
        )
        self.name_button.pack(side="left", padx=10)
        self.name_frame.grid(row=1, column=0, pady=20)

        self.test_frame = ctk.CTkFrame(self, fg_color="white")
        self.test_frame.grid(row=2, column=0, sticky="nsew", padx=50, pady=20)
        self.test_frame.grid_columnconfigure(0, weight=1)

        self.instruction_label = ctk.CTkLabel(
            self.test_frame,
            text="",
            font=FONT_MEDIUM,
            text_color=TEXT_COLOR,
            wraplength=800
        )
        self.instruction_label.grid(row=0, column=0, pady=10)

        self.display_label = ctk.CTkLabel(
            self.test_frame,
            text="",
            font=("Arial", 72, "bold"),
            text_color="#4B7BFF"
        )
        self.display_label.grid(row=1, column=0, pady=20)

        self.timer_label = ctk.CTkLabel(
            self.test_frame,
            text="",
            font=FONT_MEDIUM,
            text_color="#FF6B6B"
        )
        self.timer_label.grid(row=2, column=0, pady=10)

        self.entry = ctk.CTkEntry(
            self.test_frame,
            font=FONT_MEDIUM,
            width=400,
            border_width=2,
            fg_color="white"
        )

        self.submit_button = ctk.CTkButton(
            self.test_frame,
            text="📤 Відправити",
            font=FONT_MEDIUM,
            command=self.check_answer,
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            height=60,
            text_color="white"
        )

        self.back_button = ctk.CTkButton(
            self,
            text="🔙 Головне меню",
            font=FONT_MEDIUM,
            command=self.back_to_menu,
            fg_color="#F0F0F0",
            hover_color="#E0E0E0",
            text_color=TEXT_COLOR,
            height=60,
            border_width=0
        )
        self.back_button.grid(row=3, column=0, pady=20)

    def start_test(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Увага", "Будь ласка, введіть ім'я!")
            return

        self.username = name
        self.name_frame.grid_forget()
        self.instruction_label.configure(text="Приготуйтеся до першого ряду...")
        self.after(1000, self.next_trial)

    def next_trial(self):
        if self.current_length > 10:
            self.end_test()
            return

        self.remaining_time = 5
        self.current_sequence = generate_sequence(self.current_length)
        self.display_label.configure(text=self.current_sequence)
        self.timer_label.configure(text=f"Час: {self.remaining_time} сек")
        self.entry.grid_forget()
        self.submit_button.grid_forget()
        self.countdown()

    def countdown(self):
        if self.remaining_time > 0:
            self.timer_label.configure(text=f"Час: {self.remaining_time} сек")
            self.remaining_time -= 1
            self.timer_id = self.after(1000, self.countdown)
        else:
            self.after_cancel(self.timer_id)
            self.prompt_answer()

    def prompt_answer(self):
        self.display_label.configure(text="")
        prompt = f"Довжина: {self.current_length}\nВведіть запам'ятований ряд:"
        self.instruction_label.configure(text=prompt)
        self.timer_label.configure(text="")
        self.entry.grid(row=3, column=0, pady=10)
        self.submit_button.grid(row=4, column=0, pady=10)

    def check_answer(self):
        user_input = self.entry.get().strip()
        correct = (user_input == self.get_correct_answer())
        self.results[self.current_length] = correct

        if correct:
            messagebox.showinfo("Результат", "Правильно!")
        else:
            messagebox.showinfo("Результат",
                                f"Неправильно!\nПравильний ряд: {self.get_correct_answer()}")

        self.current_length += 1
        self.instruction_label.configure(text="Приготуйтеся до наступного ряду...")
        self.entry.delete(0, "end")
        self.entry.grid_forget()
        self.submit_button.grid_forget()
        self.after(1000, self.next_trial)

    def get_correct_answer(self):
        return self.current_sequence

    def end_test(self):
        A = 3
        for length in range(4, 11):
            if self.results.get(length, False):
                A = length
            else:
                break

        m = 0
        n = 0
        for length in range(A + 1, 11):
            if length in self.results:
                m += 1 if self.results[length] else 0
                n += 1

        V = A + (m / n if n > 0 else 0)
        level = evaluate_level(V)

        result_text = (
            f"Результати тесту:\n"
            f"Тест: {self.test_name}\n"
            f"Ім'я: {self.username}\n"
            f"A = {A}\n"
            f"m = {m}, n = {n}\n"
            f"V = {V:.2f}\n"
            f"Рівень: {level}"
        )

        self.show_result_window(result_text)
        save_result(self.username, self.test_name, result_text)
        self.reset_test()
        self.controller.show_frame(MenuFrame)

    def show_result_window(self, text):
        win = ctk.CTkToplevel(self)
        win.title("Результати тесту")
        win.geometry("600x500")

        textbox = ctk.CTkTextbox(win, font=ctk.CTkFont(size=16), wrap="word")
        textbox.pack(fill="both", expand=True, padx=20, pady=20)
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")

        btn = ctk.CTkButton(
            win,
            text="ОК",
            command=win.destroy,
            font=ctk.CTkFont(size=16)
        )
        btn.pack(pady=10)

    def reset_test(self):
        self.username = ""
        self.current_length = 4
        self.results = {}
        self.current_sequence = ""
        self.name_entry.delete(0, "end")
        self.name_frame.grid(row=1, column=0, pady=20)
        self.instruction_label.configure(text="")
        self.display_label.configure(text="")
        self.timer_label.configure(text="")
        self.entry.grid_forget()
        self.submit_button.grid_forget()

    def back_to_menu(self):
        if messagebox.askyesno("Підтвердження", "Вийти з тесту і повернутися в меню?"):
            if self.timer_id:
                self.after_cancel(self.timer_id)
            self.reset_test()
            self.controller.show_frame(MenuFrame)


class TestFrame1(BaseTestFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Метод відтворення рядів", "🔢")


class TestFrame2(BaseTestFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Відтворення у зворотному порядку", "🔄")

    def get_correct_answer(self):
        return self.current_sequence[::-1]

    def prompt_answer(self):
        self.display_label.configure(text="")
        prompt = (
            f"Довжина: {self.current_length}\n"
            "Введіть запам'ятований ряд у зворотному порядку:"
        )
        self.instruction_label.configure(text=prompt)
        self.timer_label.configure(text="")
        self.entry.grid(row=3, column=0, pady=10)
        self.submit_button.grid(row=4, column=0, pady=10)


class InfoFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white")
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self,
            text="📚 Інформація про тести",
            font=FONT_LARGE,
            text_color=TEXT_COLOR
        )
        title.grid(row=0, column=0, pady=(20, 30))

        info_text = """
        Ці тести створені для перевірки уваги та оперативної пам'яті.

        🔢 Тест "Метод відтворення рядів":
        - Вам показують ряд чисел (від 4 до 10 цифр) на 5 секунд.
        - Потім потрібно ввести ці числа в тому ж порядку.

        🔄 Тест "Відтворення у зворотному порядку":
        - Аналогічний, але числа треба вводити у зворотному порядку.

        📈 Формула оцінки:
        V = A + (m/n), де:
        - A – максимальна довжина, яку ви вгадали правильно.
        - m – кількість вдалих спроб для довжин > A.
        - n – загальна кількість спроб для довжин > A.

        🏆 Рівні:
        - V < 4: Низький рівень пам'яті
        - 4 ≤ V < 6: Середній рівень
        - V ≥ 6: Високий рівень
        """

        text_area = ctk.CTkTextbox(
            self,
            font=FONT_SMALL,
            wrap="word",
            fg_color="white",
            text_color=TEXT_COLOR,
            border_width=2,
            border_color="#E0E0E0",
            activate_scrollbars=True
        )
        text_area.grid(row=1, column=0, sticky="nsew", padx=50, pady=(0, 20))
        text_area.insert("1.0", info_text)
        text_area.configure(state="disabled")

        back_button = ctk.CTkButton(
            self,
            text="🔙 Головне меню",
            font=FONT_MEDIUM,
            command=lambda: self.controller.show_frame(MenuFrame),
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            height=60,
            text_color="white"
        )
        back_button.grid(row=2, column=0, pady=20)


class ResultsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white")
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self,
            text="📊 Результати тестів",
            font=FONT_LARGE,
            text_color=TEXT_COLOR
        )
        title.grid(row=0, column=0, pady=(20, 30))

        self.text_area = ctk.CTkTextbox(
            self,
            font=FONT_SMALL,
            wrap="word",
            fg_color="white",
            text_color=TEXT_COLOR,
            border_width=2,
            border_color="#E0E0E0",
            activate_scrollbars=True
        )
        self.text_area.grid(row=1, column=0, sticky="nsew", padx=50, pady=(0, 20))
        self.text_area.configure(state="disabled")

        button_frame = ctk.CTkFrame(self, fg_color="white")
        button_frame.grid(row=2, column=0, pady=10)

        clear_btn = ctk.CTkButton(
            button_frame,
            text="🧹 Очистити результати",
            font=FONT_MEDIUM,
            command=self.clear_results,
            fg_color="#FF9BB8",
            hover_color="#FF7A9C",
            height=60,
            text_color="white"
        )
        clear_btn.pack(side="left", padx=10)

        analysis_btn = ctk.CTkButton(
            button_frame,
            text="📈 Аналіз трендів",
            font=FONT_MEDIUM,
            command=self.analyze_results,
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            height=60,
            text_color="white"
        )
        analysis_btn.pack(side="left", padx=10)

        back_button = ctk.CTkButton(
            button_frame,
            text="🔙 Головне меню",
            font=FONT_MEDIUM,
            command=lambda: self.controller.show_frame(MenuFrame),
            fg_color="#F0F0F0",
            hover_color="#E0E0E0",
            height=60,
            text_color=TEXT_COLOR
        )
        back_button.pack(side="left", padx=10)

    def on_show(self):
        self.load_results()

    def load_results(self):
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", "end")

        if os.path.exists("results.txt"):
            with open("results.txt", "r", encoding="utf-8") as f:
                content = f.read()
                self.text_area.insert("1.0", content)
        else:
            self.text_area.insert("1.0", "Поки що немає збережених результатів.")

        self.text_area.configure(state="disabled")

    def clear_results(self):
        if messagebox.askyesno("Підтвердження", "Ви впевнені, що хочете очистити результати?"):
            with open("results.txt", "w", encoding="utf-8") as f:
                f.write("")
            self.load_results()
            messagebox.showinfo("Результати", "Результати очищено.")

    def analyze_results(self):
        analysis_data = analyze_results()
        if not analysis_data:
            messagebox.showinfo("Аналіз", "Поки що немає даних для аналізу.")
            return

        analysis_text = (
            f"Аналіз трендів:\n\n"
            f"Загальна кількість тестів: {analysis_data['total_tests']}\n"
            f"Загальне середнє V: {analysis_data['overall_avg']:.2f}\n"
            f"Загальне стандартне відхилення: {analysis_data['overall_std']:.2f}\n\n"
            "За тестами:\n"
        )

        for test, stats in analysis_data["tests_stats"].items():
            analysis_text += (
                f"{test}:\n"
                f"  Кількість: {stats['count']}\n"
                f"  Середнє V: {stats['avg']:.2f}\n"
                f"  Std: {stats['std']:.2f}\n\n"
            )

        analysis_text += "За користувачами:\n"
        for user, stats in analysis_data["users_stats"].items():
            analysis_text += (
                f"{user}:\n"
                f"  Кількість: {stats['count']}\n"
                f"  Середнє V: {stats['avg']:.2f}\n"
                f"  Std: {stats['std']:.2f}\n\n"
            )

        win = ctk.CTkToplevel(self)
        win.title("Аналіз трендів")
        win.geometry("700x600")

        textbox = ctk.CTkTextbox(win, font=ctk.CTkFont(size=16), wrap="word")
        textbox.pack(fill="both", expand=True, padx=20, pady=20)
        textbox.insert("1.0", analysis_text)
        textbox.configure(state="disabled")

        btn = ctk.CTkButton(
            win,
            text="ОК",
            command=win.destroy,
            font=ctk.CTkFont(size=16)
        )
        btn.pack(pady=10)


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()