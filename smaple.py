import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

def int_to_time_str(num_int):
    if not num_int: return ""
    s = str(num_int).strip().zfill(4)
    return f"{s[:2]}:{s[2:]}"

def calculate_pt_hours(start_in, end_in):
    try:
        if not start_in or not end_in: return 0.0
        t1_str, t2_str = int_to_time_str(start_in), int_to_time_str(end_in)
        fmt = "%H:%M"
        t1, t2 = datetime.strptime(t1_str, fmt), datetime.strptime(t2_str, fmt)
        if t2 < t1: t2 += timedelta(days=1)
        return round((t2 - t1).total_seconds() / 3600, 2)
    except: return 0.0

def judge_fulltime_attendance(check_in, attendance_type):
    try:
        if not check_in: return 0.0
        t_str = int_to_time_str(check_in)
        fmt = "%H:%M"
        t_check = datetime.strptime(t_str, fmt)
        b_late1 = datetime.strptime("03:00", fmt)
        b_late2 = datetime.strptime("05:30", fmt)
        b_base12 = datetime.strptime("12:00", fmt)
        
        hours = 0.0
        if "遲到①" in attendance_type and t_check > b_late1:
            hours = (t_check - b_late1).total_seconds() / 3600
        elif "遲到②" in attendance_type and t_check > b_late2:
            hours = (t_check - b_late2).total_seconds() / 3600
        elif "早退" in attendance_type and t_check < b_base12:
            hours = (b_base12 - t_check).total_seconds() / 3600
        elif "加班" in attendance_type and t_check > b_base12:
            hours = (t_check - b_base12).total_seconds() / 3600
        return round(hours, 2)
    except: return 0.0

class PureAttendanceCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("考勤工時計算機 - 30天全視覽工作面板")
        self.root.geometry("920x680")
        self.root.configure(bg="#f8fafc")
        
        # 記憶體中的 30 天數據
        self.days_data = {i: {"ft_in": "", "ft_type": "遲到① (03:00後)", "ft_total": 0.0, 
                             "pt_in": "", "pt_out": "", "pt_total": 0.0} for i in range(1, 31)}
        
        # 🟢 內建 5 天模擬數據（方便您一打開就能看見畫面效果）
        self.days_data[1] = {"ft_in": "330", "ft_type": "遲到① (03:00後)", "ft_total": 0.5, "pt_in": "", "pt_out": "", "pt_total": 0.0}
        self.days_data[2] = {"ft_in": "", "ft_type": "遲到① (03:00後)", "ft_total": 0.0, "pt_in": "541", "pt_out": "1121", "pt_total": 5.67}
        self.days_data[3] = {"ft_in": "540", "ft_type": "遲到② (05:30後)", "ft_total": 0.17, "pt_in": "", "pt_out": "", "pt_total": 0.0}
        self.days_data[4] = {"ft_in": "1100", "ft_type": "早退 (12:00前)", "ft_total": 1.0, "pt_in": "", "pt_out": "", "pt_total": 0.0}
        self.days_data[5] = {"ft_in": "1330", "ft_type": "加班 (12:00後)", "ft_total": 1.5, "pt_in": "600", "pt_out": "1200", "pt_total": 6.0}
        
        self.create_widgets()
        self.refresh_ui_display()

    def create_widgets(self):
        # 頂部快速編輯區塊
        frame_top = tk.LabelFrame(self.root, text=" 30天數據快速輸入 / 修改面板 ", font=("微軟正黑體", 11, "bold"), bg="#ffffff", padx=10, pady=10)
        frame_top.pack(padx=15, pady=10, fill="x")
        
        tk.Label(frame_top, text="選擇天數(1-30):", bg="#ffffff", font=("微軟正黑體", 10)).grid(row=0, column=0, padx=2, pady=5, sticky="e")
        self.spin_day = tk.Spinbox(frame_top, from_=1, to=30, width=5, font=("Arial", 10), command=self.on_day_spin_change)
        self.spin_day.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.spin_day.bind("<KeyRelease>", lambda e: self.on_day_spin_change())
        
        # 正職輸入組
        tk.Label(frame_top, text="【正職】key in 時間:", bg="#ffffff", font=("微軟正黑體", 10)).grid(row=0, column=2, padx=2, pady=5, sticky="e")
        self.ent_ft_in = tk.Entry(frame_top, width=8, font=("Arial", 10))
        self.ent_ft_in.grid(row=0, column=3, padx=5, pady=5)
        self.ent_ft_in.bind("<KeyRelease>", self.on_ft_keywrite)
        
        self.combo_ft_type = ttk.Combobox(frame_top, values=["遲到① (03:00後)", "遲到② (05:30後)", "早退 (12:00前)", "加班 (12:00後)"], state="readonly", width=15, font=("微軟正黑體", 9))
        self.combo_ft_type.grid(row=0, column=4, padx=5, pady=5)
        self.combo_ft_type.current(0)
        
        self.lbl_ft_preview = tk.Label(frame_top, text="轉時間: --:--", font=("微軟正黑體", 9), fg="#2563eb", bg="#eff6ff", width=12)
        self.lbl_ft_preview.grid(row=0, column=5, padx=5, pady=5)

        # 兼職 PT 輸入組
        tk.Label(frame_top, text="【兼職】上班快捷:", bg="#ffffff", font=("微軟正黑體", 10)).grid(row=1, column=2, padx=2, pady=5, sticky="e")
        self.ent_pt_in = tk.Entry(frame_top, width=8, font=("Arial", 10))
        self.ent_pt_in.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(frame_top, text="下班快捷:", bg="#ffffff", font=("微軟正黑體", 10)).grid(row=1, column=4, padx=2, pady=5, sticky="e")
        self.ent_pt_out = tk.Entry(frame_top, width=8, font=("Arial", 10))
        self.ent_pt_out.grid(row=1, column=5, padx=5, pady=5)
        
        btn_save = tk.Button(frame_top, text="確認更新此天數據", command=self.save_current_day, bg="#2563eb", fg="white", font=("微軟正黑體", 10, "bold"), padx=10)
        btn_save.grid(row=0, column=6, rowspan=2, padx=15, pady=5, sticky="ns")

        # 中間 30 天大矩陣表格區塊
        frame_table = tk.LabelFrame(self.root, text=" 30天全視覽工時數據矩陣 (雙擊任一行可重回上方修改) ", font=("微軟正黑體", 11, "bold"), bg="#ffffff", padx=10, pady=5)
        frame_table.pack(padx=15, pady=5, fill="both", expand=True)
        
        columns = ("day", "ft_in", "ft_type", "ft_hours", "pt_in", "pt_out", "pt_hours")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings")
        
        self.tree.heading("day", text="天數")
        self.tree.heading("ft_in", text="正職輸入")
        self.tree.heading("ft_type", text="正職項目")
        self.tree.heading("ft_hours", text="正職時數(Hr)")
        self.tree.heading("pt_in", text="兼職上班")
        self.tree.heading("pt_out", text="兼職下班")
        self.tree.heading("pt_hours", text="兼職工時(Hr)")
        
        self.tree.column("day", width=60, anchor="center")
        for col in columns[1:]:
            self.tree.column(col, width=120, anchor="center")
            
        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", self.on_table_double_click)

        # 底部大面積自動加總匯總面板
        self.frame_summary = tk.Frame(self.root, bg="#0f172a", bd=1, relief="solid")
        self.frame_summary.pack(padx=15, pady=15, fill="x")
        
        self.lbl_ft_summary = tk.Label(self.frame_summary, text="", bg="#0f172a", fg="#38bdf8", font=("微軟正黑體", 10, "bold"), justify="left")
        self.lbl_ft_summary.pack(side="left", padx=15, pady=10)
        
        self.lbl_pt_summary = tk.Label(self.frame_summary, text="", bg="#0f172a", fg="#34d399", font=("微軟正黑體", 11, "bold"), justify="right")
        self.lbl_pt_summary.pack(side="right", padx=15, pady=10)

    def on_ft_keywrite(self, event):
        val = self.ent_ft_in.get().strip()
        if val.isdigit():
            self.lbl_ft_preview.config(text=f"轉時間: {int_to_time_str(val)}")
        else:
            self.lbl_ft_preview.config(text="轉時間: --:--")

    def on_day_spin_change(self):
        try:
            day = int(self.spin_day.get())
            if 1 <= day <= 30:
                d = self.days_data[day]
                self.ent_ft_in.delete(0, tk.END)
                self.ent_ft_in.insert(0, d["ft_in"])
                self.on_ft_keywrite(None)
                
                idx = ["遲到①", "遲到②", "早退", "加班"].index(d["ft_type"].split()[0])
                self.combo_ft_type.current(idx)
                
                self.ent_pt_in.delete(0, tk.END)
                self.ent_pt_in.insert(0, d["pt_in"])
                self.ent_pt_out.delete(0, tk.END)
                self.ent_pt_out.insert(0, d["pt_out"])
        except: pass

    def save_current_day(self):
        try:
            day = int(self.spin_day.get())
            if not (1 <= day <= 30): return
                
            ft_in = self.ent_ft_in.get().strip()
            ft_type = self.combo_ft_type.get()
            pt_in = self.ent_pt_in.get().strip()
            pt_out = self.ent_pt_out.get().strip()
            
            ft_hours = judge_fulltime_attendance(ft_in, ft_type) if ft_in else 0.0
            pt_hours = calculate_pt_hours(pt_in, pt_out) if (pt_in and pt_out) else 0.0
            
            self.days_data[day] = {
                "ft_in": ft_in, "ft_type": ft_type if ft_in else "遲到① (03:00後)", "ft_total": ft_hours,
                "pt_in": pt_in, "pt_out": pt_out, "pt_total": pt_hours
            }
            self.refresh_ui_display()
            
            if day < 30:
                self.spin_day.delete(0, tk.END)
                self.spin_day.insert(0, str(day + 1))
                self.on_day_spin_change()
        except Exception as e:
            messagebox.showerror("錯誤", f"儲存失敗: {str(e)}")

    def refresh_ui_display(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        sum_late1, sum_late2, sum_early, sum_over, sum_pt = 0.0, 0.0, 0.0, 0.0, 0.0
        
        for i in range(1, 31):
            d = self.days_data[i]
            ft_show_type = d["ft_type"].split()[0] if d["ft_in"] else "-"
            ft_hours_str = f"{d['ft_total']:.2f}" if d["ft_total"] > 0 else "-"
            pt_hours_str = f"{d['pt_total']:.2f}" if d["pt_total"] > 0 else "-"
            
            self.tree.insert("", "end", values=(
                f"第 {i} 天",
                d["ft_in"] if d["ft_in"] else "-",
                ft_show_type,
                ft_hours_str,
                int_to_time_str(d["pt_in"]) if d["pt_in"] else "-",
                int_to_time_str(d["pt_out"]) if d["pt_out"] else "-",
                pt_hours_str
            ))
            
            if d["ft_in"]:
                if "遲到①" in d["ft_type"]: sum_late1 += d["ft_total"]
                elif "遲到②" in d["ft_type"]: sum_late2 += d["ft_total"]
                elif "早退" in d["ft_type"]: sum_early += d["ft_total"]
                elif "加班" in d["ft_type"]: sum_over += d["ft_total"]
            sum_pt += d["pt_total"]
            
        ft_text = (f" 📊 正職考勤累計統計 (本月)：\n"
                   f" ⊙ 遲到①總計: {sum_late1:.2f} 小時  |  ⊙ 遲到②總計: {sum_late2:.2f} 小時\n"
                   f" ⊙ 早退總計:  {sum_early:.2f} 小時  |  ⊙ 加班總計:  {sum_over:.2f} 小時")
        self.lbl_ft_summary.config(text=ft_text)
        
        pt_text = f"🟢 兼職 (PT) 累計總工時：\n{sum_pt:.2f} 小時"
        self.lbl_pt_summary.config(text=pt_text)

    def on_table_double_click(self, event):
        try:
            item = self.tree.selection()[0]
            values = self.tree.item(item, "values")
            day_num = int(values[0].replace("第 ", "").replace(" 天", ""))
            self.spin_day.delete(0, tk.END)
            self.spin_day.insert(0, str(day_num))
            self.on_day_spin_change()
        except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = PureAttendanceCalculator(root)
    root.mainloop()
