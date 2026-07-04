# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog
import json, os

cfg_path = os.path.expanduser('~/.moyu_reader_config')
THEMES = [('#191a1b','#d4d4d4'),('#191a1b','#abb2bf'),('#1e1e1e','#cccccc'),('#ffffff','#373737'),('#272822','#f8f8f2'),('#282a36','#f8f8f2'),('#191a1b','#E0E0E0'),('#16191d','#fffbff')]
THEME_NAMES = ['暗·灰白','暗·蓝灰','暗·浅灰','亮·深灰','Monokai','Dracula','暗·亮灰','深·暖白']
FONTS = ['Consolas','Microsoft YaHei','SimSun','SimHei','KaiTi','FangSong','Arial','Times New Roman','Courier New','NSimSun','DengXian','✏ 自定义...']

def darken_hex(h, amount=40):
    h = h.lstrip('#')
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        r, g, b = max(0, r-amount), max(0, g-amount), max(0, b-amount)
        return f'#{r:02x}{g:02x}{b:02x}'
    except:
        return '#333333'

def blend_hex(c1, c2, ratio=0.5):
    """混合两个颜色，ratio=0: 全c1, ratio=1: 全c2"""
    def _p(h):
        h = h.lstrip('#')
        if len(h) == 3:
            h = h[0]*2 + h[1]*2 + h[2]*2
        return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    try:
        r1,g1,b1 = _p(c1); r2,g2,b2 = _p(c2)
        r=int(r1+(r2-r1)*ratio); g=int(g1+(g2-g1)*ratio); b=int(b1+(b2-b1)*ratio)
        return f'#{r:02x}{g:02x}{b:02x}'
    except:
        return '#555555'

def load():
    try:
        if os.path.exists(cfg_path):
            return json.load(open(cfg_path))
    except:
        pass
    return {'x':400,'y':200,'w':800,'h':600,'fs':16,'a':0.85,'ti':0,'lf':'','lp':{},'last_f':'','ff':'Consolas','c_bg':'#1e1e1e','c_fg':'#d4d4d4'}

def save(d):
    with open(cfg_path,'w') as f:
        json.dump(d, f)

cfg = load()
w = txt = None
bg, fg = THEMES[cfg.get('ti',0)]
fs = cfg.get('fs',16)
total_chars = 0
hidden = False
borders = {}

resize = {'active': False, 'dir': '', 'sx': 0, 'sy': 0, 'sw': 0, 'sh': 0, 'sx2': 0, 'sy2': 0}

def sm(e):
    w._dx=e.x_root-w.winfo_x(); w._dy=e.y_root-w.winfo_y()

def mv(e):
    w.geometry(f'+{e.x_root-w._dx}+{e.y_root-w._dy}')

def rs_start(e, d):
    resize['active'] = True
    resize['dir'] = d
    resize['sx'], resize['sy'] = e.x_root, e.y_root
    resize['sx2'], resize['sy2'] = w.winfo_x(), w.winfo_y()
    resize['sw'], resize['sh'] = w.winfo_width(), w.winfo_height()
    return 'break'

def rs(e):
    if not resize['active']:
        return
    dx = e.x_root - resize['sx']
    dy = e.y_root - resize['sy']
    d = resize['dir']
    nx, ny, nw, nh = resize['sx2'], resize['sy2'], resize['sw'], resize['sh']
    if 'e' in d:
        nw = max(200, resize['sw'] + dx)
    if 'w' in d:
        nw = max(200, resize['sw'] - dx)
        if nw > 200:
            nx = resize['sx2'] + dx
    if 's' in d:
        nh = max(40, resize['sh'] + dy)
    if 'n' in d:
        nh = max(40, resize['sh'] - dy)
        if nh > 40:
            ny = resize['sy2'] + dy
    w.geometry(f'{nw}x{nh}+{nx}+{ny}')
    return 'break'

def rs_end(e):
    resize['active'] = False


# 自动保存位置相关（去抖 + 定时）
save_after_id = None

def schedule_save_pos(delay=1000):
    global save_after_id
    try:
        if save_after_id and w:
            w.after_cancel(save_after_id)
    except Exception:
        pass
    try:
        save_after_id = w.after(delay, do_save_pos)
    except Exception:
        # 如果窗口未就绪，则直接保存
        do_save_pos()

def do_save_pos():
    global save_after_id
    try:
        if txt and w:
            first = txt.yview()[0]
            # 根据当前打开的文件路径记录位置
            fp = cfg.get('lf', '')
            if fp:
                if 'lp' not in cfg or not isinstance(cfg['lp'], dict):
                    cfg['lp'] = {}
                cfg['lp'][fp] = round(first, 4)
                # 持久化保存进度到磁盘，防止异常退出丢失进度
                try:
                    save(cfg)
                except Exception:
                    pass
                print(f"更新并保存位置 [{os.path.basename(fp)}]: {cfg['lp'][fp]}")
    except Exception as e:
        print(f"更新位置出错: {e}")
    save_after_id = None

def sel():
    return filedialog.askopenfilename(filetypes=[('文本文件', '*.txt *.md'), ('EPUB电子书', '*.epub'), ('所有文件', '*.*')])

def set_t(i):
    global bg, fg
    if i == -1:
        bg, fg = cfg.get('c_bg','#1e1e1e'), cfg.get('c_fg','#d4d4d4')
    else:
        bg, fg = THEMES[i]
    cfg['ti'] = i
    if w: w.config(bg=bg)
    if txt: txt.config(bg=bg, fg=fg)
    for b in borders.values():
        b.config(bg=bg)

def nxt():
    ti = cfg.get('ti', 0)
    if ti == -1: ti = len(THEMES) - 1  # 从自定义跳出
    set_t((ti+1) % len(THEMES))

def prv():
    ti = cfg.get('ti', 0)
    if ti == -1: ti = 0  # 从自定义跳出
    set_t((ti-1) % len(THEMES))

def fsz(d):
    global fs
    fs = max(8, min(48, fs+d))
    cfg['fs'] = fs
    font_family = cfg.get('ff', 'Consolas')
    txt.config(font=(font_family, fs))

def alp(d):
    a = max(0.3, min(1, w.attributes('-alpha')+d))
    w.attributes('-alpha', a)
    cfg['a'] = a

def close():
    global txt, total_chars
    cfg['x'], cfg['y'] = w.winfo_x(), w.winfo_y()
    cfg['w'], cfg['h'] = w.winfo_width(), w.winfo_height()
    # 保存当前可见视图的垂直位置，便于下次恢复到相同阅读位置
    pct = 0
    try:
        if txt:
            first = txt.yview()[0]
            fp = cfg.get('lf', '')
            if fp:
                if 'lp' not in cfg or not isinstance(cfg['lp'], dict):
                    cfg['lp'] = {}
                cfg['lp'][fp] = round(first, 4)
                print(f"保存位置(视图) [{os.path.basename(fp)}]: {first} -> {cfg['lp'][fp]}")
            pct = min(99, int(first * 100))
    except Exception as e:
        print(f"保存位置出错: {e}")
        pct = 0

    # 保存配置并关闭窗口
    try:
        save(cfg)
        print(f"配置已保存到: {cfg_path}")
    except Exception:
        pass
    try:
        w.destroy()
    except Exception:
        pass

def scr(val):
    # 根据滑动条百分比直接移动视图
    try:
        if txt:
            txt.yview_moveto(float(val) / 100.0)
            prog()
    except Exception:
        pass

def prog(e=None):
    # 更新进度条和百分比显示
    try:
        if not txt or not w:
            return
        first = txt.yview()[0]
        pct = min(99, int(first * 100))
        if hasattr(w, '_float_bar') and w._float_bar:
            w._update_float_bar(pct)
    except Exception:
        pass

def page_scroll(direction):
    """翻页: direction=1 下一页, -1 上一页"""
    try:
        if txt:
            txt.yview_scroll(direction, 'pages')
            prog()
            schedule_save_pos(200)
    except Exception:
        pass

def read_epub(fp):
    import zipfile, re
    try:
        content_list = []
        with zipfile.ZipFile(fp, 'r') as zf:
            html_files = [f for f in zf.namelist() if f.endswith(('.html', '.xhtml')) and 'OEBPS/' in f]
            if not html_files:
                html_files = [f for f in zf.namelist() if f.endswith(('.html', '.xhtml'))]
            for html_file in html_files:
                try:
                    with zf.open(html_file) as f:
                        html_content = f.read().decode('utf-8', errors='ignore')
                        text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
                        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
                        text = re.sub(r'<[^>]+>', '\n', text)
                        text = re.sub(r'&nbsp;|\u00a0', ' ', text)
                        text = re.sub(r'&[a-zA-Z]+;', ' ', text)
                        text = re.sub(r'\n\s*\n', '\n\n', text)
                        text = text.strip()
                        if text and len(text) > 10:
                            content_list.append(text)
                except Exception as e:
                    print(f"Error reading {html_file}: {e}")
                    continue
            if content_list:
                return '\n\n' + '\n\n'.join(content_list)
            else:
                return "无法从EPUB文件中提取文本内容"
    except Exception as e:
        print(f"Error reading EPUB: {e}")
        return None

def read_docx(fp):
    try:
        import docx
        doc = docx.Document(fp)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return None

def key(e):
    try:
        c = (e.char or '').lower()
    except Exception:
        c = ''
    if c == 't':
        nxt()
    elif c == 'r':
        prv()
    elif c in ['+', '=']:
        fsz(1)
    elif c == '-':
        fsz(-1)
    elif e.keysym == 'Up':
        alp(0.05)
    elif e.keysym == 'Down':
        alp(-0.05)
    elif e.keysym == 'Page_Down':
        page_scroll(1)
    elif e.keysym == 'Page_Up':
        page_scroll(-1)
    elif c == ' ':
        page_scroll(1)
        return 'break'
    elif c in ['q', '\x1b'] or e.keysym == 'Escape':
        close()
    elif e.keysym == 'w' and (e.state & 4):
        close()

def on_enter(e):
    global hidden
    if hidden:
        w.attributes("-alpha", cfg.get('a', 0.85))
        hidden = False

def on_leave(e):
    global hidden
    w.attributes("-alpha", 0.02)
    hidden = True


# ──────────────────────────────────────────────
#  启动设置窗口（在进入阅读前进行个性化配置）
# ──────────────────────────────────────────────
def launcher():
    lbg = '#2b2b2b'
    lfg = '#e0e0e0'
    abg = '#3c3c3c'
    accent = '#0078d4'

    root = tk.Tk()
    root.title('Notepad -- Settings')
    root.geometry('520x700+500+250')
    root.resizable(False, False)
    root.config(bg=lbg)

    selected_file = tk.StringVar(value=cfg.get('lf', ''))
    raw_ti = cfg.get('ti', 0)
    selected_theme = tk.IntVar(value=raw_ti if raw_ti >= 0 else len(THEMES))  # -1 → 自定义索引
    selected_font = tk.StringVar(value=cfg.get('ff', 'Consolas'))
    selected_size = tk.IntVar(value=cfg.get('fs', 16))
    selected_alpha = tk.DoubleVar(value=cfg.get('a', 0.85))

    preview_bg = THEMES[selected_theme.get()][0]
    preview_fg = THEMES[selected_theme.get()][1]

    # ── 标题 ──
    title = tk.Label(root, text='📖 Zen Reader', font=('Microsoft YaHei', 18, 'bold'),
                     bg=lbg, fg='#ffffff')
    title.pack(pady=(20, 5))
    subtitle = tk.Label(root, text='阅读前，先调到你最舒服的样子', font=('Microsoft YaHei', 10),
                        bg=lbg, fg='#888888')
    subtitle.pack(pady=(0, 15))

    # ── 文件选择 ──
    file_frame = tk.LabelFrame(root, text='📁 选择文件', font=('Microsoft YaHei', 10),
                               bg=lbg, fg=lfg, padx=10, pady=8)
    file_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

    file_row = tk.Frame(file_frame, bg=lbg)
    file_row.pack(fill=tk.X)
    file_entry = tk.Entry(file_row, textvariable=selected_file, font=('Consolas', 9),
                          bg=abg, fg=lfg, insertbackground=lfg, relief='flat', bd=0)
    file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

    def pick_file():
        fp = filedialog.askopenfilename(filetypes=[('文本文件', '*.txt *.md'), ('EPUB电子书', '*.epub'),
                                                    ('Word文档', '*.docx'), ('所有文件', '*.*')])
        if fp:
            selected_file.set(fp)

    tk.Button(file_row, text='浏览', command=pick_file, font=('Microsoft YaHei', 9),
              bg=accent, fg='#ffffff', relief='flat', padx=14, pady=2,
              activebackground='#106ebe', cursor='hand2').pack(side=tk.LEFT, padx=(8, 0))

    # ── 主题配色 ──
    theme_frame = tk.LabelFrame(root, text='🎨 主题配色', font=('Microsoft YaHei', 10),
                                bg=lbg, fg=lfg, padx=10, pady=8)
    theme_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

    swatch_frames = []
    total_swatches = len(THEMES) + 1  # +1 for custom
    row_frames = [tk.Frame(theme_frame, bg=lbg) for _ in range((total_swatches + 3) // 4)]
    for rf in row_frames:
        rf.pack(fill=tk.X, pady=1)

    custom_bg_var = tk.StringVar(value=cfg.get('c_bg', '#1e1e1e'))
    custom_fg_var = tk.StringVar(value=cfg.get('c_fg', '#d4d4d4'))

    def on_theme_click(idx):
        selected_theme.set(idx)
        for i, sw in enumerate(swatch_frames):
            sw.config(highlightbackground=accent if i == idx else lbg,
                      highlightthickness=2 if i == idx else 1)
        custom_row.pack_forget() if idx != total_swatches - 1 else custom_row.pack(fill=tk.X, pady=(4, 0))
        update_preview()

    for i, (tbg, tfg) in enumerate(THEMES):
        row = i // 4
        swatch = tk.Frame(row_frames[row], bg=tbg, width=100, height=40, cursor='hand2',
                          highlightbackground=accent if i == selected_theme.get() else lbg,
                          highlightthickness=2 if i == selected_theme.get() else 1,
                          relief='flat')
        swatch.pack(side=tk.LEFT, padx=4, pady=2)
        swatch.pack_propagate(False)
        lbl = tk.Label(swatch, text=THEME_NAMES[i], bg=tbg, fg=tfg,
                       font=('Microsoft YaHei', 8))
        lbl.place(relx=0.5, rely=0.5, anchor='center')
        swatch.bind('<Button-1>', lambda e, idx=i: on_theme_click(idx))
        lbl.bind('<Button-1>', lambda e, idx=i: on_theme_click(idx))
        swatch_frames.append(swatch)

    # 自定义配色 swatch
    cst_row = (len(THEMES)) // 4
    cst_swatch = tk.Frame(row_frames[cst_row], bg='#3a3a3a', width=100, height=40, cursor='hand2',
                          highlightbackground=accent if total_swatches - 1 == selected_theme.get() else lbg,
                          highlightthickness=2 if total_swatches - 1 == selected_theme.get() else 1,
                          relief='flat')
    cst_swatch.pack(side=tk.LEFT, padx=4, pady=2)
    cst_swatch.pack_propagate(False)
    cst_lbl = tk.Label(cst_swatch, text='🎨 自定义', bg='#3a3a3a', fg='#ffffff',
                       font=('Microsoft YaHei', 8))
    cst_lbl.place(relx=0.5, rely=0.5, anchor='center')
    cst_swatch.bind('<Button-1>', lambda e: on_theme_click(total_swatches - 1))
    cst_lbl.bind('<Button-1>', lambda e: on_theme_click(total_swatches - 1))
    swatch_frames.append(cst_swatch)

    # 自定义颜色输入行（默认隐藏）
    custom_row = tk.Frame(theme_frame, bg=lbg)

    tk.Label(custom_row, text='背景色', font=('Microsoft YaHei', 9), bg=lbg, fg=lfg).pack(side=tk.LEFT)
    bg_entry = tk.Entry(custom_row, textvariable=custom_bg_var, font=('Consolas', 9),
                        bg=abg, fg=lfg, insertbackground=lfg, relief='flat', bd=0, width=9)
    bg_entry.pack(side=tk.LEFT, padx=(4, 2), ipady=2)

    tk.Label(custom_row, text='文字色', font=('Microsoft YaHei', 9), bg=lbg, fg=lfg).pack(side=tk.LEFT, padx=(8, 0))
    fg_entry = tk.Entry(custom_row, textvariable=custom_fg_var, font=('Consolas', 9),
                        bg=abg, fg=lfg, insertbackground=lfg, relief='flat', bd=0, width=9)
    fg_entry.pack(side=tk.LEFT, padx=(4, 2), ipady=2)

    # 颜色选择器按钮
    def pick_bg_color():
        from tkinter import colorchooser
        c = colorchooser.askcolor(color=custom_bg_var.get(), title='选择背景色')
        if c[1]:
            custom_bg_var.set(c[1])
            update_preview()

    def pick_fg_color():
        from tkinter import colorchooser
        c = colorchooser.askcolor(color=custom_fg_var.get(), title='选择文字色')
        if c[1]:
            custom_fg_var.set(c[1])
            update_preview()

    tk.Button(custom_row, text='🎨', command=pick_bg_color, font=('Microsoft YaHei', 9),
              bg=abg, fg=lfg, relief='flat', padx=6, pady=0, cursor='hand2',
              activebackground=accent).pack(side=tk.LEFT, padx=(2, 0))
    tk.Button(custom_row, text='🎨', command=pick_fg_color, font=('Microsoft YaHei', 9),
              bg=abg, fg=lfg, relief='flat', padx=6, pady=0, cursor='hand2',
              activebackground=accent).pack(side=tk.LEFT, padx=(2, 0))

    if selected_theme.get() == total_swatches - 1:
        custom_row.pack(fill=tk.X, pady=(4, 0))

    custom_bg_var.trace_add('write', lambda *_: update_preview())
    custom_fg_var.trace_add('write', lambda *_: update_preview())

    # ── 字体 & 字号 ──
    font_frame = tk.LabelFrame(root, text='🔤 字体 & 字号', font=('Microsoft YaHei', 10),
                               bg=lbg, fg=lfg, padx=10, pady=8)
    font_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

    font_row = tk.Frame(font_frame, bg=lbg)
    font_row.pack(fill=tk.X)

    tk.Label(font_row, text='字体', font=('Microsoft YaHei', 9), bg=lbg, fg=lfg).pack(side=tk.LEFT)

    def on_font_select(val):
        if val == '✏ 自定义...':
            custom_font_entry.config(state='normal')
            custom_font_entry.focus_set()
        else:
            custom_font_entry.config(state='disabled')

    font_opt = tk.OptionMenu(font_row, selected_font, *FONTS, command=on_font_select)
    font_opt.config(bg=abg, fg=lfg, font=('Microsoft YaHei', 9), relief='flat', bd=0,
                    activebackground=accent, activeforeground='#ffffff',
                    highlightthickness=0, width=16)
    font_opt['menu'].config(bg=abg, fg=lfg, font=('Microsoft YaHei', 9),
                            activebackground=accent, activeforeground='#ffffff',
                            relief='flat', bd=0)
    font_opt.pack(side=tk.LEFT, padx=(8, 4))

    # 自定义字体输入框
    custom_font_var = tk.StringVar(value='')
    custom_font_entry = tk.Entry(font_row, textvariable=custom_font_var, font=('Consolas', 9),
                                 bg=abg, fg=lfg, insertbackground=lfg, relief='flat', bd=0, width=14)
    custom_font_entry.pack(side=tk.LEFT, padx=(0, 10), ipady=2)
    if selected_font.get() != '✏ 自定义...':
        custom_font_entry.config(state='disabled')

    def on_custom_font_change(*_):
        val = custom_font_var.get().strip()
        if val:
            selected_font.set(val)
            update_preview()

    custom_font_var.trace_add('write', on_custom_font_change)

    tk.Label(font_row, text='字号', font=('Microsoft YaHei', 9), bg=lbg, fg=lfg).pack(side=tk.LEFT)

    size_lbl = tk.Label(font_row, text=str(selected_size.get()), font=('Consolas', 10, 'bold'),
                        bg=lbg, fg=accent, width=3)
    size_lbl.pack(side=tk.RIGHT, padx=(4, 0))

    def on_size_change(val):
        size_lbl.config(text=str(int(float(val))))
    size_scale = tk.Scale(font_row, from_=8, to=48, variable=selected_size,
                          orient=tk.HORIZONTAL, bg=lbg, fg=lfg, troughcolor=abg,
                          highlightthickness=0, bd=0, length=140,
                          activebackground=accent, command=on_size_change)
    size_scale.pack(side=tk.RIGHT, padx=(4, 0))

    # ── 预览 ──
    preview_frame = tk.LabelFrame(root, text='👁 预览效果', font=('Microsoft YaHei', 10),
                                  bg=lbg, fg=lfg, padx=10, pady=8)
    preview_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

    def update_preview(*_):
        ti = selected_theme.get()
        total_sw = len(THEMES) + 1
        if ti >= total_sw - 1:
            pbg = custom_bg_var.get().strip() or '#1e1e1e'
            pfg = custom_fg_var.get().strip() or '#d4d4d4'
        else:
            pbg = THEMES[ti][0]
            pfg = THEMES[ti][1]
        pff = selected_font.get()
        if pff == '✏ 自定义...':
            pff = custom_font_var.get().strip() or 'Consolas'
        pfs = selected_size.get()
        try:
            preview_text.config(bg=pbg, fg=pfg, font=(pff, pfs))
        except Exception:
            preview_text.config(bg=pbg, fg=pfg, font=('Consolas', pfs))

    preview_text = tk.Text(preview_frame, height=3, wrap=tk.WORD, bd=0, relief='flat',
                           highlightthickness=0, padx=8, pady=8)
    preview_text.pack(fill=tk.X)
    preview_text.insert('1.0', '永和九年，岁在癸丑，暮春之初，会于会稽山阴之兰亭……\nThe quick brown fox jumps over the lazy dog. 1234567890')
    preview_text.config(state='disabled')
    update_preview()

    selected_theme.trace_add('write', update_preview)
    selected_font.trace_add('write', update_preview)
    selected_size.trace_add('write', update_preview)

    # ── 透明度 ──
    alpha_frame = tk.LabelFrame(root, text='☁ 窗口透明度', font=('Microsoft YaHei', 10),
                                bg=lbg, fg=lfg, padx=10, pady=8)
    alpha_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

    alpha_row = tk.Frame(alpha_frame, bg=lbg)
    alpha_row.pack(fill=tk.X)

    alpha_lbl = tk.Label(alpha_row, text=f'{selected_alpha.get():.0%}', font=('Consolas', 10, 'bold'),
                         bg=lbg, fg=accent, width=5)
    alpha_lbl.pack(side=tk.RIGHT, padx=(4, 0))

    def on_alpha_change(val):
        alpha_lbl.config(text=f'{float(val):.0%}')

    alpha_scale = tk.Scale(alpha_row, from_=0.3, to=1.0, resolution=0.05,
                           variable=selected_alpha, orient=tk.HORIZONTAL,
                           bg=lbg, fg=lfg, troughcolor=abg, highlightthickness=0,
                           bd=0, length=300, activebackground=accent,
                           command=on_alpha_change)
    alpha_scale.pack(side=tk.RIGHT, padx=(0, 10))
    tk.Label(alpha_row, text='30%', font=('Consolas', 8), bg=lbg, fg='#666').pack(side=tk.LEFT)
    tk.Label(alpha_row, text='100%', font=('Consolas', 8), bg=lbg, fg='#666').pack(side=tk.LEFT, padx=(10, 0))

    # ── 按钮区 ──
    btn_frame = tk.Frame(root, bg=lbg)
    btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

    last_file_label = tk.Label(btn_frame, text='', font=('Microsoft YaHei', 8),
                               bg=lbg, fg='#666666')
    last_file_label.pack(side=tk.LEFT, pady=(4, 0))

    def on_start():
        fp = selected_file.get().strip()
        if not fp:
            return
        if not os.path.exists(fp):
            return

        cfg['lf'] = fp
        ti = selected_theme.get()
        total_sw = len(THEMES) + 1
        if ti >= total_sw - 1:
            cfg['ti'] = -1
            cfg['c_bg'] = custom_bg_var.get().strip() or '#1e1e1e'
            cfg['c_fg'] = custom_fg_var.get().strip() or '#d4d4d4'
        else:
            cfg['ti'] = ti

        ff = selected_font.get()
        if ff == '✏ 自定义...':
            ff = custom_font_var.get().strip() or 'Consolas'
        cfg['ff'] = ff
        cfg['fs'] = selected_size.get()
        cfg['a'] = round(selected_alpha.get(), 2)
        try:
            save(cfg)
        except Exception:
            pass
        root.destroy()

    def on_start_and_close():
        fp = selected_file.get().strip()
        if not fp or not os.path.exists(fp):
            return
        on_start()

    tk.Button(btn_frame, text='开始阅读 ▶', command=on_start_and_close,
              font=('Microsoft YaHei', 12, 'bold'), bg=accent, fg='#ffffff',
              relief='flat', padx=30, pady=8, activebackground='#106ebe',
              cursor='hand2').pack(side=tk.RIGHT)

    # 如果有最近文件，显示提示
    if cfg.get('lf') and os.path.exists(cfg['lf']):
        last_file_label.config(text=f'上次: {os.path.basename(cfg["lf"])}')

    root.bind('<Escape>', lambda e: root.destroy())
    root.bind('<Return>', lambda e: on_start_and_close())
    root.mainloop()
    # launcher 关闭后，如果已设置文件则进入阅读
    if cfg.get('lf') and os.path.exists(cfg['lf']):
        return cfg['lf']
    return None


def run(fp):
    global w, txt, bg, fg, fs, total_chars, hidden, borders
    if not fp:
        return
    # 如果切换了要打开的文件，立即写入配置（记录最近打开的文件），以减少频繁磁盘写入
    prev_fp = cfg.get('lf')
    cfg['lf'] = fp
    try:
        if prev_fp != fp:
            save(cfg)
            print(f"切换文件，已保存配置: {fp}")
    except Exception:
        pass
    hidden = False
    w = tk.Tk()
    # 全局绑定 Esc 键以便关闭窗口（确保无论焦点在哪都可响应）
    w.bind('<Escape>', lambda e: close())
    w.overrideredirect(True)
    w.attributes('-topmost', True)
    ti = cfg.get('ti', 0)
    if ti == -1:
        bg, fg = cfg.get('c_bg', '#1e1e1e'), cfg.get('c_fg', '#d4d4d4')
    else:
        bg, fg = THEMES[ti]
    fs = cfg.get('fs', 16)
    w.geometry(f'{cfg.get("w", 800)}x{cfg.get("h", 600)}+{cfg.get("x", 400)}+{cfg.get("y", 200)}')
    w.attributes('-alpha', cfg.get('a', 0.85))
    w.config(bg=bg)

    font_family = cfg.get('ff', 'Consolas')
    txt = tk.Text(w, wrap=tk.WORD, bg=bg, fg=fg, font=(font_family, fs), bd=0, highlightthickness=0, insertwidth=0, selectborderwidth=0, spacing2=6)
    txt.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

    if fp.lower().endswith('.epub'):
        content = read_epub(fp)
        if content is None:
            content = "无法读取EPUB文件，请安装ebooklib库：\npip install ebooklib"
    elif fp.lower().endswith('.docx'):
        content = read_docx(fp)
        if content is None:
            content = "无法读取DOCX文件，请安装python-docx库：\npip install python-docx"
    else:
        try:
            content = open(fp, encoding='utf-8').read()
        except UnicodeDecodeError:
            content = open(fp, encoding='gbk').read()
    total_chars = len(content)
    txt.insert(tk.END, content)
    txt.config(state='disabled')

    # 恢复之前保存的视图位置
    try:
        lp_data = cfg.get('lp', {})
        pos = 0.0
        if isinstance(lp_data, dict) and fp in lp_data:
            pos = float(lp_data[fp])
        elif isinstance(lp_data, (int, float)):
            # 兼容旧版本配置
            v = float(lp_data)
            if v > 1.0:
                pos = max(0.0, min(0.99, v / 100.0))
            else:
                pos = max(0.0, min(0.99, v))
        
        if pos > 0:
            txt.yview_moveto(pos)
    except Exception:
        pass

    txt.bind('<Enter>', on_enter)
    txt.bind('<Leave>', on_leave)

    bdr = 2
    cursors = {
        'n': 'sb_v_double_arrow',
        's': 'sb_v_double_arrow',
        'e': 'sb_h_double_arrow',
        'w': 'sb_h_double_arrow',
        'ne': 'size_ne_sw',
        'nw': 'size_nw_se',
        'se': 'size_nw_se',
        'sw': 'size_ne_sw'
    }
    for d in cursors:
        borders[d] = tk.Frame(w, bg=bg, cursor=cursors[d])
        borders[d].bind('<Button-1>', lambda e, dir=d: rs_start(e, dir))
        borders[d].bind('<B1-Motion>', rs)
        borders[d].bind('<ButtonRelease-1>', rs_end)
        borders[d].bind('<Enter>', on_enter)
        borders[d].bind('<Leave>', on_leave)

    borders['n'].place(x=0, y=0, relwidth=1, height=bdr)
    borders['s'].place(x=0, rely=1, y=-bdr, relwidth=1, height=bdr)
    borders['e'].place(relx=1, x=-bdr, y=0, width=bdr, relheight=1)
    borders['w'].place(x=0, y=0, width=bdr, relheight=1)
    borders['ne'].place(relx=1, x=-bdr, y=0, width=bdr, height=bdr)
    borders['nw'].place(x=0, y=0, width=bdr, height=bdr)
    borders['se'].place(relx=1, x=-bdr, rely=1, y=-bdr, width=bdr, height=bdr)
    borders['sw'].place(x=0, rely=1, y=-bdr, width=bdr, height=bdr)
    
    w.bind('<Button-1>', sm)
    w.bind('<B1-Motion>', mv)
    txt.bind('<Button-1>', sm)
    txt.bind('<B1-Motion>', mv)
    txt.bind('<Key>', key)
    def _on_key_release(e):
        try:
            prog(e)
        except Exception:
            pass
        schedule_save_pos(500)
    txt.bind('<KeyRelease>', _on_key_release)
    txt.bind('<ButtonRelease-1>', lambda e: schedule_save_pos(200))
    txt.bind('<MouseWheel>', lambda e: schedule_save_pos(200))
    txt.bind('<Button-4>', lambda e: schedule_save_pos(200))
    txt.bind('<Button-5>', lambda e: schedule_save_pos(200))
    w.protocol('WM_DELETE_WINDOW', close)

    # ── 底部悬浮进度条（鼠标移到窗口底部边缘才显示） ──
    # 颜色：使用 bg/fg 的混合色，融入主题，不抢眼
    bar_track = blend_hex(bg, fg, 0.18)
    bar_fill = blend_hex(bg, fg, 0.55)
    bar_pct_text = blend_hex(bg, fg, 0.50)

    float_bar = tk.Canvas(w, height=24, bg=bg, highlightthickness=0, bd=0, cursor='hand2')
    float_bar._hover = False

    def _draw_thin():
        float_bar.delete('all')
        ww = max(1, w.winfo_width())
        float_bar.create_line(16, 22, ww - 8, 22, fill=bar_track, width=1, tags='line')

    def _draw_full():
        float_bar.delete('all')
        ww = max(1, w.winfo_width())
        pct = 0
        try:
            if txt:
                pct = min(99, int(txt.yview()[0] * 100))
        except Exception:
            pass
        float_bar.create_rectangle(16, 19, ww - 8, 23, fill=bar_track, outline='', tags='track')
        pw = max(1, int(pct / 100.0 * (ww - 24)))
        float_bar.create_rectangle(16, 19, 16 + pw, 23, fill=bar_fill, outline='', tags='prog')
        float_bar.create_text(10, 8, text=f'{pct}%', fill=bar_pct_text,
                              font=('Consolas', 8), anchor='w', tags='pct')

    _draw_thin()
    float_bar.place(relx=0, rely=1.0, anchor='sw', y=0, relwidth=1.0, height=24)

    def _on_bar_enter(e):
        float_bar._hover = True
        on_enter(e)  # 防止鼠标从文本区移入时触发 on_leave 导致窗口透明
        _draw_full()

    def _on_bar_leave(e):
        float_bar._hover = False
        on_leave(e)  # 离开进度条→离开窗口时恢复透明
        w.after(500, lambda: _draw_thin() if not float_bar._hover else None)

    float_bar.bind('<Enter>', _on_bar_enter)
    float_bar.bind('<Leave>', _on_bar_leave)

    def _resize_track(e=None):
        try:
            if float_bar._hover:
                _draw_full()
            else:
                _draw_thin()
            prog()
        except Exception:
            pass
    w.bind('<Configure>', _resize_track)

    def _bar_jump(e):
        ww = max(1, w.winfo_width())
        r = max(0, min(1, (e.x - 16) / max(1, ww - 24)))
        txt.yview_moveto(r)
        prog()

    def _bar_drag(e):
        ww = max(1, w.winfo_width())
        r = max(0, min(1, (e.x - 16) / max(1, ww - 24)))
        txt.yview_moveto(r)
        prog()

    float_bar.bind('<Button-1>', _bar_jump)
    float_bar.bind('<B1-Motion>', _bar_drag)

    w._float_bar = float_bar

    def update_float_bar(pct):
        try:
            if not float_bar._hover:
                return
            ww = max(1, w.winfo_width())
            pw = max(1, int(pct / 100.0 * (ww - 24)))
            float_bar.coords('prog', 16, 19, 16 + pw, 23)
            float_bar.itemconfig('pct', text=f'{pct}%')
        except Exception:
            pass

    w._update_float_bar = update_float_bar

    # ── 快捷键提示（底部淡入 3 秒后消失） ──
    hint_text = 'Space/PgDn 翻页 | PgUp 回翻 | t/r 主题 | +/- 字号 | ↑↓ 透明度 | Esc 退出'
    w._hint = tk.Label(w, text=hint_text, bg=bg, fg=fg, font=('Microsoft YaHei', 9), pady=4)
    w._hint.place(relx=0.5, rely=1.0, anchor='s', y=-20)
    w.after(4000, lambda: w._hint.place_forget() if hasattr(w, '_hint') else None)

    prog()
    w.deiconify()
    w.lift()
    w.attributes('-alpha', 1.0)
    w.mainloop()

if __name__ == '__main__':
    fp = launcher()
    if fp:
        run(fp)