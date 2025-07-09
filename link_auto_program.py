import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import os

class LinkAutoProgram:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 링크 자동 클릭 프로그램")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        self.driver = None
        self.links = []
        self.is_running = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # 제목
        title_label = tk.Label(self.root, text="🚀 링크 자동 클릭 프로그램", 
                              font=('Arial', 20, 'bold'), bg='#f0f0f0', fg='#333')
        title_label.pack(pady=20)
        
        # 파일 선택 프레임
        file_frame = tk.Frame(self.root, bg='#f0f0f0')
        file_frame.pack(pady=10)
        
        tk.Label(file_frame, text="📁 엑셀 파일:", font=('Arial', 12), bg='#f0f0f0').pack(side=tk.LEFT)
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(file_frame, textvariable=self.file_path_var, width=50, font=('Arial', 10))
        self.file_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(file_frame, text="파일 선택", command=self.select_file, 
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # 버튼 클릭 설정 프레임
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        tk.Label(button_frame, text="🎯 클릭할 버튼:", font=('Arial', 12), bg='#f0f0f0').pack(side=tk.LEFT)
        self.button_selector_var = tk.StringVar()
        self.button_entry = tk.Entry(button_frame, textvariable=self.button_selector_var, width=40, font=('Arial', 10))
        self.button_entry.pack(side=tk.LEFT, padx=5)
        self.button_entry.insert(0, "button")  # 기본값
        
        tk.Label(button_frame, text="(예: button, .btn, #submit)", font=('Arial', 8), bg='#f0f0f0', fg='#666').pack(side=tk.LEFT, padx=5)
        
        # 딜레이 설정
        delay_frame = tk.Frame(self.root, bg='#f0f0f0')
        delay_frame.pack(pady=5)
        
        tk.Label(delay_frame, text="⏱️ 페이지 로딩 대기:", font=('Arial', 12), bg='#f0f0f0').pack(side=tk.LEFT)
        self.delay_var = tk.StringVar(value="3")
        delay_spinbox = tk.Spinbox(delay_frame, from_=1, to=10, textvariable=self.delay_var, width=5, font=('Arial', 10))
        delay_spinbox.pack(side=tk.LEFT, padx=5)
        tk.Label(delay_frame, text="초", font=('Arial', 10), bg='#f0f0f0').pack(side=tk.LEFT)
        
        # 컨트롤 버튼들
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(pady=20)
        
        self.analyze_btn = tk.Button(control_frame, text="📊 링크 분석", command=self.analyze_links,
                                   bg='#2196F3', fg='white', font=('Arial', 12, 'bold'), width=12)
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        self.start_btn = tk.Button(control_frame, text="🚀 시작", command=self.start_automation,
                                 bg='#FF9800', fg='white', font=('Arial', 12, 'bold'), width=12)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ 중지", command=self.stop_automation,
                                bg='#F44336', fg='white', font=('Arial', 12, 'bold'), width=12)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 프로그레스 바
        progress_frame = tk.Frame(self.root, bg='#f0f0f0')
        progress_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(progress_frame, text="진행 상황:", font=('Arial', 10), bg='#f0f0f0').pack(anchor=tk.W)
        self.progress = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # 로그 창
        log_frame = tk.Frame(self.root, bg='#f0f0f0')
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        tk.Label(log_frame, text="📋 실행 로그:", font=('Arial', 12), bg='#f0f0f0').pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, font=('Arial', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def log(self, message):
        """로그 메시지 출력"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def select_file(self):
        """엑셀 파일 선택"""
        file_path = filedialog.askopenfilename(
            title="엑셀 파일 선택",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.log(f"✅ 파일 선택됨: {os.path.basename(file_path)}")
            
    def analyze_links(self):
        """엑셀 파일에서 링크 분석"""
        if not self.file_path_var.get():
            messagebox.showerror("오류", "엑셀 파일을 먼저 선택해주세요!")
            return
            
        try:
            self.log("📊 링크 분석 시작...")
            file_path = self.file_path_var.get()
            
            # 엑셀 파일 읽기
            xls = pd.ExcelFile(file_path)
            self.links = []
            
            for sheet_name in xls.sheet_names:
                self.log(f"📄 {sheet_name} 시트 분석 중...")
                df = xls.parse(sheet_name)
                
                for col in df.columns:
                    if df[col].astype(str).str.contains("http", na=False).any():
                        links = df[col].dropna().astype(str).tolist()
                        # http로 시작하는 링크만 필터링
                        valid_links = [link for link in links if link.startswith('http')]
                        self.links.extend(valid_links)
                        self.log(f"  📎 {col} 열에서 {len(valid_links)}개 링크 발견")
            
            # 중복 제거
            self.links = list(set(self.links))
            
            if self.links:
                self.log(f"✅ 총 {len(self.links)}개의 고유 링크를 찾았습니다!")
                for i, link in enumerate(self.links[:5]):  # 처음 5개만 표시
                    self.log(f"  {i+1}. {link}")
                if len(self.links) > 5:
                    self.log(f"  ... 및 {len(self.links) - 5}개 더")
            else:
                self.log("❌ 링크를 찾을 수 없습니다.")
                
        except Exception as e:
            error_msg = f"❌ 분석 실패: {str(e)}"
            self.log(error_msg)
            messagebox.showerror("오류", error_msg)
            
    def start_automation(self):
        """자동화 시작"""
        if not self.links:
            messagebox.showerror("오류", "먼저 링크를 분석해주세요!")
            return
            
        if self.is_running:
            messagebox.showwarning("경고", "이미 실행 중입니다!")
            return
            
        # 새 스레드에서 실행
        thread = threading.Thread(target=self.run_automation)
        thread.daemon = True
        thread.start()
        
    def run_automation(self):
        """자동화 실행"""
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        
        try:
            self.log("🚀 자동화 시작!")
            
            # 브라우저 실행
            chromedriver_path = "chromedriver-mac-arm64/chromedriver"
            if not os.path.exists(chromedriver_path):
                raise Exception(f"chromedriver를 찾을 수 없습니다: {chromedriver_path}")
                
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service)
            self.log("✅ 브라우저 실행됨")
            
            # 진행률 설정
            self.progress['maximum'] = len(self.links)
            self.progress['value'] = 0
            
            button_selector = self.button_selector_var.get().strip()
            delay = int(self.delay_var.get())
            
            for i, link in enumerate(self.links):
                if not self.is_running:
                    break
                    
                self.log(f"🔗 [{i+1}/{len(self.links)}] {link} 접속 중...")
                
                try:
                    # 페이지 접속
                    self.driver.get(link)
                    time.sleep(delay)
                    
                    # 버튼 찾기 및 클릭
                    try:
                        if button_selector.startswith('#'):
                            # ID로 찾기
                            button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.ID, button_selector[1:]))
                            )
                        elif button_selector.startswith('.'):
                            # 클래스로 찾기
                            button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.CLASS_NAME, button_selector[1:]))
                            )
                        else:
                            # 태그명으로 찾기
                            button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.TAG_NAME, button_selector))
                            )
                        
                        button.click()
                        self.log(f"  ✅ 버튼 클릭 성공!")
                        
                    except Exception as e:
                        self.log(f"  ⚠️ 버튼 클릭 실패: {str(e)}")
                        
                    time.sleep(1)  # 추가 대기
                    
                except Exception as e:
                    self.log(f"  ❌ 접속 실패: {str(e)}")
                
                # 진행률 업데이트
                self.progress['value'] = i + 1
                
        except Exception as e:
            error_msg = f"❌ 자동화 실행 실패: {str(e)}"
            self.log(error_msg)
            messagebox.showerror("오류", error_msg)
            
        finally:
            self.stop_automation()
            
    def stop_automation(self):
        """자동화 중지"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        
        if self.driver:
            try:
                self.driver.quit()
                self.log("🧹 브라우저 종료됨")
            except:
                pass
            finally:
                self.driver = None
                
        self.log("⏹️ 자동화 중지됨")

def main():
    root = tk.Tk()
    app = LinkAutoProgram(root)
    root.mainloop()

if __name__ == "__main__":
    main() 