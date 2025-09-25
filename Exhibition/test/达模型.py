import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from openai import OpenAI


class OpenAITester:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenAI API 测试工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # 尝试从环境变量获取API密钥
        self.api_key = os.environ.get("OPENAI_API_KEY", "")

        self.setup_ui()

    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # API密钥输入
        ttk.Label(main_frame, text="API密钥:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar(value=self.api_key)
        self.api_key_entry = ttk.Entry(main_frame, textvariable=self.api_key_var, width=70, show="*")
        self.api_key_entry.grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))

        # 模型选择
        ttk.Label(main_frame, text="模型:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value="gpt-4o-mini")
        #self.model_var = tk.StringVar(value="qwen-turbo")
        model_combo = ttk.Combobox(main_frame, textvariable=self.model_var, width=67)
        model_combo['values'] = ('gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo')
        model_combo.grid(row=1, column=1, pady=5, sticky=(tk.W, tk.E))

        # 输入文本
        ttk.Label(main_frame, text="输入内容:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        self.input_text = scrolledtext.ScrolledText(main_frame, width=70, height=8)
        self.input_text.grid(row=2, column=1, pady=5, sticky=(tk.W, tk.E))
        self.input_text.insert(tk.END, "write a haiku about ai")

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=1, pady=10, sticky=tk.E)

        self.test_btn = ttk.Button(button_frame, text="测试API", command=self.test_api)
        self.test_btn.pack(side=tk.RIGHT, padx=5)

        self.clear_btn = ttk.Button(button_frame, text="清除", command=self.clear_text)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)

        # 输出区域
        ttk.Label(main_frame, text="API响应:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.output_text = scrolledtext.ScrolledText(main_frame, width=70, height=15)
        self.output_text.grid(row=4, column=1, pady=5, sticky=(tk.W, tk.E))

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)

    def test_api(self):
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入API密钥")
            return

        input_text = self.input_text.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showerror("错误", "请输入测试内容")
            return

        self.status_var.set("正在调用API...")
        self.test_btn.config(state=tk.DISABLED)
        self.root.update()

        try:
            # 初始化OpenAI客户端
            client = OpenAI(api_key=api_key)

            # 调用API
            response = client.chat.completions.create(
                model=self.model_var.get(),
                messages=[
                    {"role": "user", "content": input_text}
                ]
            )

            # 显示响应
            output = response.choices[0].message.content
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, output)

            self.status_var.set("API调用成功")

        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")
            messagebox.showerror("API错误", f"调用API时发生错误:\n{str(e)}")

        finally:
            self.test_btn.config(state=tk.NORMAL)

    def clear_text(self):
        self.output_text.delete("1.0", tk.END)


def main():
    root = tk.Tk()
    app = OpenAITester(root)
    root.mainloop()


if __name__ == "__main__":
    main()