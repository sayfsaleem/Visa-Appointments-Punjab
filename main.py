import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.font as tkFont
from tkinter import ttk
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from botasaurus.browser import browser, Driver # BotaSauras Driver
from botasaurus.browser import Wait
import time
from PIL import Image
import requests
from io import BytesIO
import pytesseract
# Define constants
HARD_CODED_EMAIL = ""
HARD_CODED_PASSWORD = ""
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
class VisaBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visa Appointment Automation Bot")
        self.credentials = []  # Initialize credentials as an empty list
        self.setup_login_screen()

    def setup_login_screen(self):
        self.login_frame = tk.Frame(self.root, padx=20, pady=20)
        self.login_frame.pack(fill=tk.BOTH, expand=True)

        custom_font = tkFont.Font(family="Helvetica", size=16, weight="bold")

        tk.Label(self.login_frame, text="Login", font=custom_font).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(self.login_frame, text="Email:").grid(row=1, column=0, pady=5, sticky="e")
        self.email_entry = tk.Entry(self.login_frame)
        self.email_entry.grid(row=1, column=1, pady=5, sticky="ew")

        tk.Label(self.login_frame, text="Password:").grid(row=2, column=0, pady=5, sticky="e")
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5, sticky="ew")

        tk.Button(self.login_frame, text="Login", command=self.perform_login).grid(row=3, column=0, columnspan=2, pady=10)

        self.login_frame.columnconfigure(1, weight=1)

    def perform_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if email == HARD_CODED_EMAIL and password == HARD_CODED_PASSWORD:
            self.login_frame.pack_forget()
            self.setup_dashboard()
        else:
            messagebox.showerror("Login Error", "Incorrect email or password")

    def setup_dashboard(self):
        self.dashboard_frame = tk.Frame(self.root, padx=20, pady=20)
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.dashboard_frame, text="Dashboard", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(self.dashboard_frame, text="Proxy Field:").grid(row=1, column=0, pady=5, sticky="e")
        self.proxy_entry = tk.Entry(self.dashboard_frame)
        self.proxy_entry.grid(row=1, column=1, pady=5, sticky="ew")

        tk.Button(self.dashboard_frame, text="Upload CSV", command=self.upload_csv).grid(row=2, column=0, columnspan=2, pady=10)

        self.email_var = tk.IntVar()
        tk.Checkbutton(self.dashboard_frame, text="Email me when appointments open", variable=self.email_var).grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(self.dashboard_frame, text="Start Bot", command=self.start_bot).grid(row=4, column=0, columnspan=2, pady=10)

        self.dashboard_frame.columnconfigure(1, weight=1)

    def upload_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.process_csv(file_path)

    def process_csv(self, file_path):
        self.credentials = []
        try:
            with open(file_path, mode='r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    self.credentials.append({
                        'First Name': row.get('First Name', ''),
                        'Last Name': row.get('Last Name', ''),
                        'Email': row.get('Email', row.get('Username', '')),
                        'Password': row.get('Password', '')
                    })
            messagebox.showinfo("CSV Processing", "CSV file processed successfully")
        except Exception as e:
            messagebox.showerror("CSV Error", f"Failed to process CSV file: {e}")
    def download_captcha_image(self, img_url):
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))
            return img

    def solve_captcha(self, img):
        captcha_text = pytesseract.image_to_string(img).strip()
        return captcha_text
    def start_bot(self):
        @browser
        def check_visa_appointments(driver:Driver,data=None):
                    driver.get("https://blsitalypakistan.com/account/login",wait=20)
                    while True:
                        for credential in self.credentials:
                            # Logging In
                            driver.type("input[placeholder='Enter Email']", credential['Email'])
                            driver.type("input[placeholder='Enter Password']", credential['Password'])
                             # Solve CAPTCHA
                            captcha_img_url = driver.evaluate_js("document.getElementById('Imageid').src")
                            captcha_image = self.download_captcha_image(captcha_img_url)
                            captcha_text = self.solve_captcha(captcha_image)

                            driver.type("input[placeholder='Enter Captcha']", captcha_text)
                            time.sleep(3)
                            driver.type("input[placeholder='Enter Captcha']", captcha_text)
                            driver.select("button[name='submitLogin']").click()
                            time.sleep(5)  # Wait for login to process

                            while True:
                                driver.refresh()
                                time.sleep(2)  # Wait for page to reload

                                try:
                                    appointment_button = driver.select("button:contains('Appointment Open')")
                                    if appointment_button:
                                        print(f"Appointment open for {credential['Email']}")
                                        # Implement further actions here if needed
                                        return  # Exit if appointment found
                                except Exception as e:
                                    print(f"Error checking appointments: {e}")

                                time.sleep(70)  # Refresh every 70 seconds
        check_visa_appointments()

    def send_email_notification(self, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = HARD_CODED_EMAIL
            msg['To'] = HARD_CODED_EMAIL
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(HARD_CODED_EMAIL, HARD_CODED_PASSWORD)
                server.sendmail(HARD_CODED_EMAIL, HARD_CODED_EMAIL, msg.as_string())
        except Exception as e:
            print(f"Failed to send email: {e}")























if __name__ == "__main__":
    root = tk.Tk()
    app = VisaBotApp(root)
    root.mainloop()
