import subprocess
import os
import tkinter as tk
import sys
import requests
from threading import Thread
from tkinter import messagebox

# ── 颜色与字体常量 ────────────────────────────────────────────
BG        = "#0D0F14"      # 主背景（深夜黑）
CARD      = "#13161E"      # 卡片背景
ACCENT    = "#FF4B4B"      # 龙虾红
ACCENT2   = "#FF8C42"      # 橙金（渐变辅色）
TEXT      = "#E8EAF0"      # 主文字
MUTED     = "#5A5F72"      # 次要文字
SUCCESS   = "#3DDC84"      # 绿色状态
BORDER    = "#1E2230"      # 边框色

FONT_TITLE  = ("Courier New", 22, "bold")
FONT_SUB    = ("Courier New", 10)
FONT_BTN    = ("Courier New", 11, "bold")
FONT_STATUS = ("Courier New", 9)

# ── 主窗口 ────────────────────────────────────────────────────
root = tk.Tk()
root.title("OpenClaw 一键部署")
root.geometry("520x760")
root.resizable(False, False)
root.configure(bg=BG)

# 状态变量
status_var = tk.StringVar(value="就绪 — 请按顺序点击下方按钮")

# ── 工具函数 ──────────────────────────────────────────────────
def download_file(url, dest_path, label="文件"):
    try:
        response = requests.get(url, stream=True, timeout=30)
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    pct = int(downloaded / total_size * 100)
                    root.after(0, lambda p=pct, l=label: status_var.set(f"下载 {l} … {p}%"))
        return True
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("下载失败", f"下载 {label} 时出错：{str(e)}"))
        return False

def threaded_task(func):
    def wrapper():
        Thread(target=func, daemon=True).start()
    return wrapper

def set_status(msg, color=TEXT):
    status_var.set(msg)
    status_label.config(fg=color)

# ── 按钮工厂 ─────────────────────────────────────────────────
def make_step_button(parent, step_num, step_title, step_desc, command, tag_color):
    frame = tk.Frame(parent, bg=CARD, bd=0, highlightthickness=1,
                     highlightbackground=BORDER)
    frame.pack(fill="x", padx=24, pady=8)

    # 左侧序号标签
    badge = tk.Label(frame, text=f"0{step_num}", bg=tag_color, fg=BG,
                     font=("Courier New", 13, "bold"), width=4, pady=14)
    badge.grid(row=0, column=0, rowspan=2, sticky="ns")

    # 标题
    tk.Label(frame, text=step_title, bg=CARD, fg=TEXT,
             font=FONT_BTN, anchor="w").grid(row=0, column=1, sticky="w", padx=14, pady=(10,2))

    # 描述
    tk.Label(frame, text=step_desc, bg=CARD, fg=MUTED,
             font=FONT_STATUS, anchor="w").grid(row=1, column=1, sticky="w", padx=14, pady=(0,10))

    # 按钮
    btn = tk.Button(frame, text="▶  执行", bg=tag_color, fg=BG,
                    font=FONT_BTN, bd=0, padx=18, pady=6,
                    activebackground=ACCENT2, activeforeground=BG,
                    cursor="hand2", command=command, relief="flat")
    btn.grid(row=0, column=2, rowspan=2, padx=14)

    frame.grid_columnconfigure(1, weight=1)
    return btn

# ── 业务逻辑 ─────────────────────────────────────────────────
def usermanual():
    messagebox.showinfo(title='📋 使用须知', message=
        "① 请确认 D 盘有足够的磁盘空间（至少 1 GB）\n"
        "② 请确保网络连接稳定\n"
        "③ 下载过程中程序会显示进度，请勿关闭\n"
        "④ 按顺序点击：先装 Node.js → 再装 Git → 最后装 OpenClaw")

@threaded_task
def download_node():
    set_status("正在下载 Node.js …", ACCENT2)
    os.makedirs(r"D:\openclawdownload", exist_ok=True)
    url  = "https://npmmirror.com/mirrors/node/v24.14.1/node-v24.14.1-x64.msi"
    dest = r"D:\openclawdownload\node.msi"
    if download_file(url, dest, "Node.js"):
        set_status("✔ Node.js 下载完成，安装程序已启动", SUCCESS)
        root.after(0, lambda: messagebox.showinfo("完成", "Node.js 下载完成，即将启动安装程序"))
        os.startfile(dest)
    else:
        set_status("✘ Node.js 下载失败", ACCENT)

@threaded_task
def download_git():
    set_status("正在下载 Git …", ACCENT2)
    os.makedirs(r"D:\openclawdownload", exist_ok=True)
    url  = "https://registry.npmmirror.com/-/binary/git-for-windows/v2.54.0-rc2.windows.1/Git-2.54.0-rc2-64-bit.exe"
    dest = r"D:\openclawdownload\Git-2.54.0-rc2-64-bit.exe"
    if download_file(url, dest, "Git"):
        set_status("✔ Git 下载完成，安装程序已启动", SUCCESS)
        root.after(0, lambda: messagebox.showinfo("完成", "Git 下载完成，即将启动安装程序"))
        os.startfile(dest)
    else:
        set_status("✘ Git 下载失败", ACCENT)

def openclaw():
    subprocess.Popen(['powershell', '-NoExit', '-Command',
                      'iwr -useb https://openclaw.ai/install.ps1 | iex'])
    set_status("✔ OpenClaw 安装脚本已执行，请查看 PowerShell 窗口", SUCCESS)
    messagebox.showinfo("提示", "OpenClaw 安装脚本已执行，请查看弹出的 PowerShell 窗口。")

def start_gateway():
    try:
        subprocess.Popen(['powershell', '-NoExit', '-Command', 'openclaw gateway start'])
        set_status("✔ 网关已启动，请查看 PowerShell 窗口", SUCCESS)
        messagebox.showinfo("网关", "OpenClaw 网关已启动！\n\n访问地址：http://127.0.0.1:18789/chat\n\n请保持 PowerShell 窗口开启。")
    except Exception as e:
        set_status("✘ 网关启动失败", ACCENT)
        messagebox.showerror("错误", f"启动网关失败：{str(e)}")

# ── 界面布局 ─────────────────────────────────────────────────

# 顶部 Hero 区
hero = tk.Frame(root, bg=BG)
hero.pack(fill="x", pady=(28, 8))

tk.Label(hero, text="🦞", bg=BG, font=("Segoe UI Emoji", 32)).pack()

tk.Label(hero, text="O P E N C L A W", bg=BG, fg=ACCENT,
         font=("Courier New", 26, "bold")).pack()

tk.Label(hero, text="一  键  部  署  工  具", bg=BG, fg=MUTED,
         font=("Courier New", 11)).pack(pady=(2, 0))

# 分割线
sep = tk.Frame(root, bg=BORDER, height=1)
sep.pack(fill="x", padx=24, pady=16)

# 步骤卡片
make_step_button(root, 1, "安装 Node.js",
                 "从国内镜像下载 v24 LTS，自动启动安装向导",
                 download_node, ACCENT)

make_step_button(root, 2, "安装 Git",
                 "从国内镜像下载 Git 2.54，自动启动安装向导",
                 download_git, ACCENT2)

make_step_button(root, 3, "安装 OpenClaw",
                 "执行官方 PowerShell 安装脚本，完成部署",
                 openclaw, "#4B8EFF")

make_step_button(root, 4, "开启网关",
                 "启动 OpenClaw Gateway，访问 127.0.0.1:18789",
                 start_gateway, "#3DDC84")

# 分割线
sep2 = tk.Frame(root, bg=BORDER, height=1)
sep2.pack(fill="x", padx=24, pady=16)

# 状态栏
status_frame = tk.Frame(root, bg=CARD, bd=0, highlightthickness=1,
                         highlightbackground=BORDER)
status_frame.pack(fill="x", padx=24, pady=(0, 12))

tk.Label(status_frame, text="状态", bg=CARD, fg=MUTED,
         font=("Courier New", 8, "bold")).pack(side="left", padx=12, pady=8)

status_label = tk.Label(status_frame, textvariable=status_var, bg=CARD,
                         fg=TEXT, font=FONT_STATUS, anchor="w")
status_label.pack(side="left", padx=4, pady=8)

# 底部按钮区
bottom = tk.Frame(root, bg=BG)
bottom.pack(fill="x", padx=24, pady=(0, 20))

tk.Button(bottom, text="📋  使用须知", bg=BORDER, fg=MUTED,
          font=("Courier New", 9), bd=0, padx=12, pady=6,
          activebackground=CARD, activeforeground=TEXT,
          cursor="hand2", command=usermanual, relief="flat").pack(side="right")

# 版权
tk.Label(root, text="OpenClaw Installer  ·  仅供学习使用", bg=BG,
         fg=MUTED, font=("Courier New", 8)).pack(side="bottom", pady=8)

root.mainloop()
