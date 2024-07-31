import tkinter as tk
from tkinter import ttk, Text, messagebox, filedialog
import subprocess
import threading
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import logging
import json
import requests

logging.basicConfig(level=logging.INFO)

class ScrapyGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Scrapy GUI with Chat API")
        self.geometry("1200x900")
        self.configure(bg='#e6f7ff')

        self.api_url = "http://127.0.0.1:5000"  # URL для доступа к API

        self.config = self.load_config()
        self.urls = self.config.get('urls', [])
        self.proxy = self.config.get('proxy', "")
        self.timeout = self.config.get('timeout', 120000)

        self.create_widgets()

    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_config(self):
        self.config['urls'] = self.urls
        self.config['proxy'] = self.proxy
        self.config['timeout'] = self.timeout
        with open('config.json', 'w') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def create_widgets(self):
        style = ttk.Style(self)
        style.configure('TButton', font=('Helvetica', 12), padding=10)
        style.configure('TLabel', font=('Helvetica', 12), padding=10)
        style.configure('TEntry', font=('Helvetica', 12), padding=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, fill=tk.BOTH, expand=True)

        self.url_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.url_frame, text="URL", compound=tk.LEFT)

        self.url_label = ttk.Label(self.url_frame, text="Enter URL for scraping:")
        self.url_label.pack(pady=10)
        self.url_entry = ttk.Entry(self.url_frame, width=70)
        self.url_entry.pack(pady=5)
        self.add_url_button = ttk.Button(self.url_frame, text="Add URL", command=self.add_url)
        self.add_url_button.pack(pady=5)
        self.url_listbox = tk.Listbox(self.url_frame, width=100, height=10)
        self.url_listbox.pack(pady=10)
        self.remove_url_button = ttk.Button(self.url_frame, text="Remove selected URL", command=self.remove_url)
        self.remove_url_button.pack(pady=5)
        self.update_url_listbox()

        self.proxy_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.proxy_frame, text="Proxy", compound=tk.LEFT)
        self.proxy_label = ttk.Label(self.proxy_frame, text="Enter proxy (optional):")
        self.proxy_label.pack(pady=10)
        self.proxy_entry = ttk.Entry(self.proxy_frame, width=70)
        self.proxy_entry.pack(pady=5)
        self.set_proxy_button = ttk.Button(self.proxy_frame, text="Set Proxy", command=self.set_proxy)
        self.set_proxy_button.pack(pady=5)

        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings", compound=tk.LEFT)
        self.timeout_label = ttk.Label(self.settings_frame, text="Set timeout (milliseconds):")
        self.timeout_label.pack(pady=10)
        self.timeout_entry = ttk.Entry(self.settings_frame, width=70)
        self.timeout_entry.pack(pady=5)
        self.set_timeout_button = ttk.Button(self.settings_frame, text="Set Timeout", command=self.set_timeout)
        self.set_timeout_button.pack(pady=5)

        self.run_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.run_frame, text="Run", compound=tk.LEFT)
        self.run_button = ttk.Button(self.run_frame, text="Run scraper", command=self.run_scraper_thread)
        self.run_button.pack(pady=10)

        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Results", compound=tk.LEFT)
        self.results_text = Text(self.results_frame, height=10, width=100, wrap=tk.WORD, bg='#ffffff')
        self.results_text.pack(pady=10)
        self.save_button = ttk.Button(self.results_frame, text="Save results", command=self.save_results)
        self.save_button.pack(pady=10)
        self.figure_frame = ttk.Frame(self.results_frame)
        self.figure_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.progress_frame = ttk.Frame(self)
        self.progress_frame.pack(pady=10, fill=tk.X)
        self.progress_label = ttk.Label(self.progress_frame, text="Progress:")
        self.progress_label.pack(side=tk.LEFT, padx=10)
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient='horizontal', mode='determinate', length=300)
        self.progress_bar.pack(side=tk.LEFT, padx=10)

        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="History", compound=tk.LEFT)
        self.history_text = Text(self.history_frame, height=10, width=100, wrap=tk.WORD, bg='#ffffff')
        self.history_text.pack(pady=10)

        self.chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="Chat", compound=tk.LEFT)
        self.chat_display = Text(self.chat_frame, height=20, width=100, wrap=tk.WORD, bg='#ffffff')
        self.chat_display.pack(pady=10)
        self.chat_input = ttk.Entry(self.chat_frame, width=100)
        self.chat_input.pack(pady=5)
        self.send_button = ttk.Button(self.chat_frame, text="Send", command=self.send_chat_message)
        self.send_button.pack(pady=5)

    def update_url_listbox(self):
        self.url_listbox.delete(0, tk.END)
        for url in self.urls:
            self.url_listbox.insert(tk.END, url)

    def add_url(self):
        url = self.url_entry.get()
        if url:
            self.urls.append(url)
            self.update_url_listbox()
            self.url_entry.delete(0, tk.END)
            self.save_config()
        else:
            messagebox.showwarning("Warning", "Please enter a URL to add.")

    def remove_url(self):
        selected_indices = self.url_listbox.curselection()
        if selected_indices:
            for index in selected_indices[::-1]:
                self.urls.pop(index)
                self.update_url_listbox()
            self.save_config()
        else:
            messagebox.showwarning("Warning", "Please select a URL to remove.")

    def set_proxy(self):
        self.proxy = self.proxy_entry.get()
        messagebox.showinfo("Info", f"Proxy set to: {self.proxy}")
        self.save_config()

    def set_timeout(self):
        try:
            self.timeout = int(self.timeout_entry.get())
            messagebox.showinfo("Info", f"Timeout set to: {self.timeout} milliseconds")
            self.save_config()
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid number for the timeout.")

    def run_scraper(self):
        if self.urls:
            with open('config.json', 'w') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)

            try:
                command = ['python', 'my_scraper/scraper.py']
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                for line in process.stdout:
                    self.update_progress(line)

                process.wait()

                self.results_text.delete('1.0', tk.END)
                if os.path.exists('output.csv'):
                    try:
                        with open('output.csv', 'r') as file:
                            self.results_text.insert(tk.END, file.read())
                        self.after(0, self.visualize_data)
                    except pd.errors.EmptyDataError:
                        self.results_text.insert(tk.END, "File output.csv is empty. Check the URL and try again.")
                    except Exception as e:
                        self.results_text.insert(tk.END, f"Error loading file: {e}")
                        logging.error(f"Error loading file: {e}")
                else:
                    self.results_text.insert(tk.END, "File output.csv not found. Check the scraper execution.")
            except Exception as e:
                logging.error(f"Error executing scraper: {e}")
                messagebox.showerror("Error", f"Error executing scraper: {e}")

            self.update_history()

    def run_scraper_thread(self):
        threading.Thread(target=self.run_scraper).start()

    def update_progress(self, line):
        if 'Found items:' in line:
            parts = line.strip().split(':')
            if len(parts) == 2 and parts[1].isdigit():
                found_items = int(parts[1])
                self.progress_bar['value'] = found_items
                self.progress_label.config(text=f"Progress: {found_items} items found")

    def save_results(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            with open('output.csv', 'r') as file:
                content = file.read()
                with open(file_path, 'w') as save_file:
                    save_file.write(content)
            messagebox.showinfo("Information", "Results saved.")

    def visualize_data(self):
        try:
            df = pd.read_csv('output.csv')
            if df.empty:
                raise ValueError("No data to visualize.")

            fig, ax = plt.subplots(figsize=(10, 6))
            df.plot(kind='bar', ax=ax)
            ax.set_title('Data Visualization from output.csv')

            for widget in self.figure_frame.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=self.figure_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        except Exception as e:
            logging.error(f"Error visualizing data: {e}")
            messagebox.showerror("Error", f"Error visualizing data: {e}")

    def update_history(self):
        if os.path.exists('history.txt'):
            with open('history.txt', 'r') as file:
                history = file.read()
        else:
            history = "Task history:\n"

        with open('history.txt', 'w') as file:
            file.write(history + f"\nTask completed. Items found: {self.progress_bar['value']}")

        self.history_text.delete('1.0', tk.END)
        self.history_text.insert(tk.END, history)

    def send_chat_message(self):
        message = self.chat_input.get()
        if message:
            self.chat_display.insert(tk.END, f"You: {message}\n")
            self.chat_input.delete(0, tk.END)
            self.process_chat_message(message)
        else:
            messagebox.showwarning("Warning", "Please enter a message to send.")

    def process_chat_message(self, message):
        # Обработка сообщения и отправка запросов к API
        if message.startswith("add_url"):
            urls = message.split()[1:]
            if urls:
                response = requests.post(f"{self.api_url}/add_url", json={"urls": urls})
                if response.status_code == 200:
                    self.chat_display.insert(tk.END, f"Bot: URLs added: {', '.join(urls)}\n")
                else:
                    self.chat_display.insert(tk.END, f"Bot: Failed to add URLs. {response.json().get('message')}\n")
            else:
                self.chat_display.insert(tk.END, "Bot: Please provide at least one URL.\n")
        elif message.startswith("list_urls"):
            response = requests.get(f"{self.api_url}/list_urls")
            if response.status_code == 200:
                urls = response.json().get("urls", [])
                if urls:
                    self.chat_display.insert(tk.END, f"Bot: URLs for scraping:\n" + "\n".join(urls) + "\n")
                else:
                    self.chat_display.insert(tk.END, "Bot: No URLs found.\n")
            else:
                self.chat_display.insert(tk.END, f"Bot: Failed to list URLs. {response.json().get('message')}\n")
        elif message.startswith("clear_urls"):
            response = requests.delete(f"{self.api_url}/clear_urls")
            if response.status_code == 200:
                self.chat_display.insert(tk.END, "Bot: All URLs cleared.\n")
            else:
                self.chat_display.insert(tk.END, f"Bot: Failed to clear URLs. {response.json().get('message')}\n")
        elif message.startswith("set_proxy"):
            proxy = message.split()[1]
            response = requests.post(f"{self.api_url}/set_proxy", json={"proxy": proxy})
            if response.status_code == 200:
                self.chat_display.insert(tk.END, f"Bot: Proxy set to: {proxy}\n")
            else:
                self.chat_display.insert(tk.END, f"Bot: Failed to set proxy. {response.json().get('message')}\n")
        elif message.startswith("clear_proxy"):
            response = requests.delete(f"{self.api_url}/clear_proxy")
            if response.status_code == 200:
                self.chat_display.insert(tk.END, "Bot: Proxy cleared.\n")
            else:
                self.chat_display.insert(tk.END, f"Bot: Failed to clear proxy. {response.json().get('message')}\n")
        elif message.startswith("run_scraper"):
            response = requests.post(f"{self.api_url}/run_scraper")
            if response.status_code == 200:
                self.chat_display.insert(tk.END, "Bot: Scraper executed.\n")
            else:
                self.chat_display.insert(tk.END, f"Bot: Failed to run scraper. {response.json().get('message')}\n")
        elif message.startswith("report_error"):
            error_message = " ".join(message.split()[1:])
            response = requests.post(f"{self.api_url}/report_error", json={"error_message": error_message})
            if response.status_code == 200:
                self.chat_display.insert(tk.END, "Bot: Error reported.\n")
            else:
                self.chat_display.insert(tk.END, f"Bot: Failed to report error. {response.json().get('message')}\n")
        elif message.startswith("request_improvement"):
            improvement_request = " ".join(message.split()[1:])
            response = requests.post(f"{self.api_url}/request_improvement", json={"improvement_request": improvement_request})
            if response.status_code == 200:
                self.chat_display.insert(tk.END, "Bot: Improvement request submitted.\n")
            else:
                self.chat_display.insert(tk.END, f"Bot: Failed to submit improvement request. {response.json().get('message')}\n")
        else:
            self.chat_display.insert(tk.END, "Bot: Unknown command. Please try again.\n")

if __name__ == '__main__':
    app = ScrapyGUI()
    app.mainloop()
