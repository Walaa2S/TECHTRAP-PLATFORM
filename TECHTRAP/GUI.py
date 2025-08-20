# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageOps
import random, webbrowser, json, os

# ========= الصوت اختياري وآمن =========
SOUND_OK = False
try:
    import pygame
    try:
        pygame.mixer.init()
        bg_sound_path = r"Sound/sound.wav"
        if os.path.exists(bg_sound_path):
            bg = pygame.mixer.Sound(bg_sound_path)
            bg.play(loops=-1)
        SOUND_OK = True
    except Exception as e:
        print("Audio disabled:", e)
except Exception as e:
    print("pygame not available:", e)

# ========= أدوات شكلية =========
def style_button(btn, bg="#8A2BE2", fg="white", fsize=14, bold=True):
    btn.config(
        bg=bg, fg=fg, activebackground="#B266FF", activeforeground="white",
        bd=0, relief="ridge", highlightthickness=0, padx=12, pady=6,
        font=("Arial", fsize, "bold" if bold else "normal"), cursor="hand2"
    )
    btn.bind("<Enter>", lambda e: btn.config(bg="#B266FF"))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    btn.bind("<ButtonPress-1>", lambda e: btn.config(bg="#8A2BE2"))
    btn.bind("<ButtonRelease-1>", lambda e: btn.config(bg="#B266FF"))

def header_bar(parent, title_text, on_back=None, on_dashboard=None):
    """شريط علوي: زر رجوع يسار + عنوان بالمنتصف + زر يمين اختياري (Dashboard)"""
    bar = tk.Frame(parent, bg="#442a6e")
    bar.pack(fill="x", side="top")

    # زر الرجوع (يسار)
    if on_back:
        back_btn = tk.Button(bar, text="← Back", command=on_back)
        style_button(back_btn, bg="#6B3FB3", fsize=12)
        back_btn.pack(side="left", padx=10, pady=8)

    # حاوية يمين (لأزرار إضافية مثل Dashboard)
    right_box = tk.Frame(bar, bg="#442a6e")
    right_box.pack(side="right", padx=10)

    if on_dashboard:
        dash_btn = tk.Button(right_box, text="Dashboard", command=on_dashboard)
        style_button(dash_btn, bg="#1E90FF", fsize=12)
        dash_btn.pack(side="left", padx=6, pady=8)

    # العنوان (منتصف)
    title = tk.Label(bar, text=title_text, font=("Arial", 20, "bold"),
                     fg="#f6f5fd", bg="#442a6e")
    title.place(relx=0.5, rely=0.5, anchor="center")

    return bar


def safe_load_image(path, size):
    """يحمل صورة ويعيد Placeholder آمن إذا لم توجد"""
    w, h = size
    try:
        print(f"🔍 محاولة تحميل الصورة: {path}")  # ← السطر الجديد
        if os.path.exists(path):
            print("✅ الصورة موجودة.")  # ← السطر الجديد
            img = Image.open(path).convert("RGBA")
            img = ImageOps.contain(img, (w, h), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        else:
            print("❌ الصورة غير موجودة.")
    except Exception as e:
        print("❌ خطأ أثناء تحميل الصورة:", e)

    # Placeholder
    img = Image.new("RGBA", (w, h), (138, 43, 226, 255))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w-1, h-1), outline=(255, 255, 255, 200), width=2)
    txt = "No Image"
    d.text((10, h//2-8), txt, fill=(255, 255, 255, 230))
    return ImageTk.PhotoImage(img)


# ========= واجهة التطبيق =========
def build_ui(root, on_game1, on_game2, on_game3, on_game4):
    root.title("Techtrap Platform")
    root.geometry("980x640")
    root.configure(bg="#40246c")
    root.resizable(True, True)

    # إطارات الصفحات
    welcome_frame = tk.Frame(root, bg="#38216a")
    character_frame = tk.Frame(root, bg="#38216a")
    games_frame = tk.Frame(root, bg="#38216a")

    # ======================================================================
    # ===================== الصفحة الأولى (معدّلة فقط) =====================
    # ======================================================================
    header_bar(welcome_frame, "Welcome to Fun Games! 🎉")
    welcome_frame.pack(fill="both", expand=True)

    # أعلام التحكم بالأنيميشن
    anim_running = {"on": True}
    gif_running = {"on": True}

    # تحميل GIF متحرك (مسار افتراضي: img_re/gg.gif)
    def load_gif_frames(path):
        frames = []
        try:
            if os.path.exists(path):
                im = Image.open(path)
                # استخراج كل الإطارات
                try:
                    while True:
                        frm = im.copy()
                        frames.append(ImageTk.PhotoImage(frm))
                        im.seek(len(frames))
                except EOFError:
                    pass
        except Exception as e:
            print("GIF load error:", e)
        return frames

    gif_path = "img_re/gg.gif"
    gif_frames = load_gif_frames(gif_path)
    gif_label = tk.Label(welcome_frame, bg="#38216a")
    gif_label.place(relx=0.5, rely=0.5, anchor="center")  # وسط الصفحة تقريبًا

    def animate_gif(i=0):
        try:
            if not gif_label.winfo_exists() or not gif_running["on"] or not gif_frames:
                return
            gif_label.config(image=gif_frames[i])
            ni = (i + 1) % len(gif_frames)
            gif_label.after(50, animate_gif, ni)  # سرعة ~20FPS
        except Exception as e:
            print("GIF animate error:", e)

    # عنوان فوق الـ GIF دائمًا
    title_label = tk.Label(welcome_frame, text="Let's Play & Learn! 🎈",
                           font=("Arial", 26, "bold"), bg="#38216a", fg="#f6f5fd")
    title_label.place(relx=0.5, rely=0.1, anchor="center")  # أعلى منتصف الصفحة

    if gif_frames:
        animate_gif()

                

    # أنيميشن الإيموجيز (نجوم/رموز)
    emoji_chars = ["⭐", "✨", "🎮", "🎈", "🏓", "🧩", "🚀"]
    emoji_labels = []
    EMOJI_COUNT = 26
    resize_job = {"id": None}

    def create_emojis(container):
        for lbl in emoji_labels:
            try: lbl.destroy()
            except: pass
        emoji_labels.clear()
        try:
            width = max(container.winfo_width(), 300)
            height = max(container.winfo_height(), 300)
            for _ in range(EMOJI_COUNT):
                emoji = tk.Label(container, text=random.choice(emoji_chars),
                                 font=("Arial", random.randint(16, 24)),
                                 bg="#40246c", fg="#f6f5fd")
                emoji.place(x=random.randint(0, width-20), y = random.randint(70, height - 20))

                emoji_labels.append(emoji)
        except Exception as e:
            print("create_emojis error:", e)

    def animate_emojis(container):
        try:
            if not container.winfo_exists() or not anim_running["on"]:
                return
            width = max(container.winfo_width(), 300)
            height = max(container.winfo_height(), 300)
            for lbl in list(emoji_labels):
                if not lbl.winfo_exists():
                    continue
                x, y = lbl.winfo_x(), lbl.winfo_y()
                y += 1
                if y > height:
                    y = 70
                    x = random.randint(0, width-20)
                lbl.place(x=x, y=y)
        except Exception as e:
            print("animate_emojis error:", e)
        finally:
            if container.winfo_exists():
                container.after(45, lambda: animate_emojis(container))

    # زر Start
    btn_start = tk.Button(welcome_frame, text="Start 🚀", width=16, height=2)
    style_button(btn_start, bg="#8A2BE2")
    btn_start.place(relx=0.5, rely=0.85, anchor="center")

    # تشغيل الأنيميشن
    welcome_frame.update_idletasks()
    create_emojis(welcome_frame)
    animate_emojis(welcome_frame)

    def on_root_resize(_):
        if not welcome_frame.winfo_exists():
            return
        if resize_job["id"]:
            try: root.after_cancel(resize_job["id"])
            except: pass
        resize_job["id"] = root.after(180, lambda: create_emojis(welcome_frame))
    root.bind("<Configure>", on_root_resize)

    # =================== نهاية تعديل الصفحة الأولى فقط ====================

    # ===== صفحة اختيار الشخصية =====
    def go_welcome():
        anim_running["on"] = True
        gif_running["on"] = True
        for w in root.pack_slaves():
            w.forget()
        welcome_frame.pack(fill="both", expand=True)
        create_emojis(welcome_frame)
        if gif_frames:
            animate_gif()

    header_bar(character_frame, "Create Your Hero ✨", on_back=go_welcome)

    top_row = tk.Frame(character_frame, bg="#533082")
    top_row.pack(pady=10)

    preview_card = tk.Frame(top_row, bg="#6C3BAE", padx=16, pady=16)
    preview_card.grid(row=0, column=0, padx=(0, 16), sticky="n")

    preview_w, preview_h = 180, 180
    preview_canvas = tk.Canvas(preview_card, width=preview_w, height=preview_h,
                               bg="#A77BFF", highlightthickness=0)
    preview_canvas.grid(row=0, column=0, rowspan=3, padx=(0, 16))

    saved_card = tk.Frame(top_row, bg="#6C3BAE", padx=16, pady=16)
    saved_card.grid(row=0, column=1, sticky="n")
    tk.Label(saved_card, text="Saved Character", font=("Arial", 12, "bold"),
             bg="#6C3BAE", fg="white").grid(row=0, column=0, columnspan=2, pady=(0, 6))

    slot_w, slot_h = 180, 180
    saved_canvas = tk.Canvas(saved_card, width=slot_w, height=slot_h,
                             bg="#A77BFF", highlightthickness=0)
    saved_canvas.grid(row=1, column=0, columnspan=2)
    saved_canvas.create_text(slot_w//2, slot_h//2, text="(No saved image)",
                             fill="white", font=("Arial", 10, "bold"), tags="hint")

    def fit_image_to_canvas(pil_img, tw, th):
        img = ImageOps.contain(pil_img, (tw, th), Image.Resampling.LANCZOS)
        pad_x = (tw - img.width)//2
        pad_y = (th - img.height)//2
        return img, pad_x, pad_y

    saved_img_ref = {"tk": None}

    def draw_on_saved_canvas(path):
        try:
            pil = Image.open(path).convert("RGBA")
            img, px, py = fit_image_to_canvas(pil, slot_w, slot_h)
            tk_img = ImageTk.PhotoImage(img)
            saved_img_ref["tk"] = tk_img
            saved_canvas.delete("all")
            saved_canvas.create_rectangle(0, 0, slot_w, slot_h, fill="#A77BFF", width=0)
            saved_canvas.create_image(px + img.width//2, py + img.height//2, image=tk_img)
        except Exception as e:
            messagebox.showerror("Load error", f"Failed to load image:\n{e}")

    selected_character_path = {"path": None}
    selected_bg_color = tk.StringVar(value="#A77BFF")
    selected_sticker = tk.StringVar(value="")
    current_img_tk = {"img": None}

    def redraw_preview():
        try:
            preview_canvas.delete("all")
            preview_canvas.configure(bg=selected_bg_color.get())
            if selected_character_path["path"]:
                pil = Image.open(selected_character_path["path"]).convert("RGBA")
                img = ImageOps.contain(pil, (preview_w-20, preview_h-20), Image.Resampling.LANCZOS)
                w, h = img.size
                px = (preview_w - w)//2
                py = (preview_h - h)//2
                img_tk = ImageTk.PhotoImage(img)
                current_img_tk["img"] = img_tk
                preview_canvas.create_image(px + w//2, py + h//2, image=img_tk)
            if selected_sticker.get():
                preview_canvas.create_text(preview_w-18, 18, text=selected_sticker.get(),
                                           font=("Arial", 24, "bold"), fill="white")
        except Exception as e:
            print("preview error:", e)

    # نموذج مختصر
    form = tk.Frame(preview_card, bg="#6C3BAE"); form.grid(row=0, column=1, sticky="w")
    tk.Label(form, text="Name", font=("Arial", 12, "bold"), bg="#6C3BAE", fg="white").grid(row=0, column=0, sticky="w")
    entry_name = tk.Entry(form, font=("Arial", 12), width=22); entry_name.grid(row=1, column=0, pady=(0, 6))
    tk.Label(form, text="Age", font=("Arial", 12, "bold"), bg="#6C3BAE", fg="white").grid(row=2, column=0, sticky="w")
    age_frame = tk.Frame(form, bg="#6C3BAE"); age_frame.grid(row=3, column=0, sticky="w", pady=(0, 6))
    age_var = tk.IntVar(value=7)
    tk.Scale(age_frame, from_=4, to=12, orient="horizontal", variable=age_var,
             length=160, bg="#6C3BAE", troughcolor="#E3D1FF",
             highlightthickness=0, fg="white").pack(side="left")
    tk.Label(age_frame, textvariable=age_var, font=("Arial", 12, "bold"),
             bg="#6C3BAE", fg="white").pack(side="left", padx=8)
    tk.Label(form, text="Parent Email", font=("Arial", 12, "bold"), bg="#6C3BAE", fg="white").grid(row=4, column=0, sticky="w")
    entry_email = tk.Entry(form, font=("Arial", 12), width=22); entry_email.grid(row=5, column=0, pady=(0, 6))

    # ألوان وملصقات
    controls = tk.Frame(preview_card, bg="#6C3BAE"); controls.grid(row=1, column=1, sticky="w", pady=(8, 0))
    tk.Label(controls, text="Background", font=("Arial", 12, "bold"), bg="#6C3BAE", fg="white").grid(row=0, column=0, sticky="w")
    color_row = tk.Frame(controls, bg="#6C3BAE"); color_row.grid(row=1, column=0, sticky="w", pady=(2, 8))
    for c in ["#A77BFF", "#FF9CEE", "#8CF6FF", "#FFD37A", "#B2FF9E"]:
        b = tk.Button(color_row, width=2, height=1, bg=c, bd=0,
                      command=lambda x=c: [selected_bg_color.set(x), redraw_preview()])
        b.pack(side="left", padx=4)
    tk.Label(controls, text="Sticker", font=("Arial", 12, "bold"), bg="#6C3BAE", fg="white").grid(row=2, column=0, sticky="w")
    sticker_row = tk.Frame(controls, bg="#6C3BAE"); sticker_row.grid(row=3, column=0, sticky="w")
    for s in ["", "⭐", "🕶️", "🎩", "🚀"]:
        text = "None" if s == "" else s
        bb = tk.Button(sticker_row, text=text, width=5,
                       command=lambda x=s: [selected_sticker.set(x), redraw_preview()])
        style_button(bb, fsize=12); bb.pack(side="left", padx=4, pady=2)

    # شبكة أفاتارات مرحة (بدون عنوان Pick an Avatar)
    avatar_box = tk.Frame(character_frame, bg="#533082"); avatar_box.pack(pady=(8, 0))
    grid_frame = tk.Frame(avatar_box, bg="#533082"); grid_frame.pack(pady=6)

    def gen_avatar(color="#FFD37A"):
        img = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse((10, 10, 110, 110), fill=color)
        d.ellipse((38, 48, 50, 60), fill="black")
        d.ellipse((70, 48, 82, 60), fill="black")
        d.arc((40, 60, 80, 95), start=200, end=340, fill="black", width=3)
        return img

    avatar_colors = ["#FFD37A", "#B2FF9E", "#8CF6FF", "#FF9CEE", "#FFF599", "#C0B7FF"]
    for i, col in enumerate(avatar_colors):
        im = gen_avatar(col).resize((84, 84), Image.Resampling.LANCZOS)
        tk_im = ImageTk.PhotoImage(im)
        def choose(idx=i, img_ref=im):
            pth = f"__builtin_avatar_{idx}.png"
            img_ref.save(pth)
            selected_character_path["path"] = pth
            redraw_preview()
        b = tk.Button(grid_frame, image=tk_im, command=choose, bd=0, highlightthickness=2, cursor="hand2")
        b.image = tk_im
        b.grid(row=i//8, column=i%8, padx=6, pady=6)
        b.configure(highlightbackground="#533082")

    # تحميل شخصية محفوظة
    def load_saved_from_json_or_file():
        candidate, jp = None, "selected_character.json"
        try:
            if os.path.exists(jp):
                with open(jp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    candidate = data.get("path")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read JSON:\n{e}")
        if not candidate or not os.path.exists(candidate):
            candidate = filedialog.askopenfilename(
                title="Select saved character image",
                filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.webp"), ("All files", "*.*")]
            )
        if candidate:
            selected_character_path["path"] = candidate
            draw_on_saved_canvas(candidate)
            redraw_preview()
        else:
            messagebox.showinfo("Info", "No image selected.")

    btn_load_saved = tk.Button(saved_card, text="Load Saved", command=load_saved_from_json_or_file)
    style_button(btn_load_saved, fsize=12)
    btn_load_saved.grid(row=2, column=0, pady=(8, 0), sticky="ew")

    character_img_label = tk.Label(character_frame, text="", bg="#533082")
    character_img_label.pack(pady=6)

    def save_character():
        name = entry_name.get().strip()
        age = str(age_var.get())
        email = entry_email.get().strip()
        if not name or not age or not email:
            messagebox.showwarning("Incomplete", "Please fill all fields!")
            return
        jp = "selected_character.json"
        try:
            if os.path.exists(jp):
                with open(jp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    selected_character_path["path"] = data.get("path") or selected_character_path["path"]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read character JSON.\n{e}")
            return
        if not selected_character_path["path"]:
            messagebox.showwarning("No character", "Please pick an avatar first!")
            return
        try:
            with open(jp, "w", encoding="utf-8") as f:
                json.dump({"path": selected_character_path["path"]}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write JSON.\n{e}")
            return
        try:
            img = Image.open(selected_character_path["path"]).resize((120, 120), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            character_img_label.config(image=img_tk, text="")
            character_img_label.image = img_tk
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load selected character image.\n{e}")
            return
        draw_on_saved_canvas(selected_character_path["path"])
        def pulse(widget, times=4):
            base, alt = widget.cget("bg"), "#533082"
            def step(i=0):
                if not widget.winfo_exists(): return
                widget.configure(bg=alt if i % 2 == 0 else base)
                if i < times * 2: widget.after(80, step, i + 1)
                else: widget.configure(bg=base)
            step()
        pulse(preview_card)
        messagebox.showinfo("Saved", f"Yay! {name}'s hero is ready 🎉")
        btn_play.config(state="normal")
        open_games_page()


    # === صف الأزرار السفلية في شاشة الكاركتر + زر فتح character.html ===
    actions = tk.Frame(character_frame, bg="#533082"); actions.pack(pady=8)

    btn_save = tk.Button(actions, text="Save ✅", command=save_character)
    style_button(btn_save, bg="#32CD32"); btn_save.pack(side="left", padx=6)

    btn_play = tk.Button(actions, text="Let’s Play 🎮", state="disabled")
    style_button(btn_play, bg="#8A2BE2"); btn_play.pack(side="left", padx=6)

    btn_skip = tk.Button(actions, text="Skip ⏭️")
    style_button(btn_skip, bg="#FFA500"); btn_skip.pack(side="left", padx=6)

    

    # زر فتح character.html
    def open_character_html():
        html_path = "character.html"
        try:
            if os.path.exists(html_path):
                webbrowser.open_new(html_path)
            else:
                messagebox.showwarning("Not Found", f"{html_path} not found!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    btn_open_html = tk.Button(actions, text="Desing your custom hero 🤩", command=open_character_html)
    style_button(btn_open_html, bg="#1E90FF"); btn_open_html.pack(side="left", padx=6)

    # ===== صفحة الألعاب (كتالوج) =====
    def go_character():
        for w in root.pack_slaves():
            w.forget()
        character_frame.pack(fill="both", expand=True)

    catalog_pages = [
          # الصفحة الأولى
    [
    {"name": "Tower Building", "img": "img_re/game1.png", "action": on_game1},
    {"name": "Racing", "img": "img_re/game2.png", "action": on_game2},
    {"name": "Dino", "img": "img_re/game3.png", "action": on_game3},
    {"name": "Tennis", "img": "img_re/game4.png", "action": on_game4},
    ]
,
        [
            {"name": "Watani Magazine", "img": "img_re/WataniMagazine.png",
             "action": lambda: open_magazine()},
            {"name": "MOUSE ", "img": "img_re/MOUSE.png",
             "action": lambda: messagebox.showinfo("Coming soon", "MOUSE  coming soon!")},
            {"name": "ART ", "img": "img_re/ART.png", "action": start_game_art},
            {"name": "BodyTrack", "img": "img_re/bodytrack.png",
             "action": lambda: messagebox.showinfo("Coming soon", "BodyTrack coming soon!")},
        ],
    ]
    current_page = {"idx": 0}
    thumbs = []  # نحفظ مراجع الصور حتى لا تُجمّع من الذاكرة


    def open_magazine():
        pdf_path = "magazine.pdf"
        try:
            if os.path.exists(pdf_path):
                webbrowser.open_new(pdf_path)
            else:
                messagebox.showinfo("Read Catalog", "Place your magazine file as 'magazine.pdf' next to the app.")
        except Exception as e:
            messagebox.showerror("Open error", str(e))
    def open_dashboard():
        win = tk.Toplevel(root)
        win.title("Dashboard")
        win.geometry("600x400")
        win.configure(bg="#38216a")
        header_bar(win, "📊 Dashboard")
        
    
    def build_games_page():
        nonlocal thumbs
        thumbs = []  # نعيد تهيئة المراجع كل مرة

        # نظّف الصفحة قبل إعادة البناء
        for w in games_frame.pack_slaves():
            w.forget()

        header_bar(games_frame, "Games Catalog 🎮", on_back=go_character, on_dashboard=open_dashboard)
        

        container = tk.Frame(games_frame, bg="#40246c")
        container.pack(fill="both", expand=True, padx=24, pady=18)

        grid = tk.Frame(container, bg="#40246c")
        grid.pack(expand=True)

        cards = catalog_pages[current_page["idx"]]

        r = c = 0
        for item in cards:
            card = tk.Frame(grid, bg="#4b2f77", padx=10, pady=10)
            card.grid(row=r, column=c, padx=14, pady=14, sticky="nsew")

            img_tk = safe_load_image(item["img"], (220, 160))
            thumbs.append(img_tk)  # مهم: احتفظ بالمرجع
            img_lbl = tk.Label(card, image=img_tk, bg="#4b2f77", cursor="hand2")
            img_lbl.image = img_tk
            img_lbl.pack()

            title = tk.Label(card, text=item["name"], font=("Arial", 14, "bold"),
                             fg="#f6f5fd", bg="#4b2f77")
            title.pack(pady=(8, 0))

            play_btn = tk.Button(card, text="Open" if "Read" in item["name"] else "Play")
            style_button(play_btn, fsize=12)
            play_btn.pack(pady=8)

            if "action" in item and callable(item["action"]):
                img_lbl.bind("<Button-1>", lambda e, fn=item["action"]: fn())
                play_btn.config(command=item["action"])

            c += 1
            if c >= 2:
                c = 0
                r += 1

        # شريط التنقل
        nav_bar = tk.Frame(container, bg="#40246c")
        nav_bar.pack(fill="x", pady=(10, 0))

        page_indicator = tk.Label(
            nav_bar,
            text=f"Page {current_page['idx']+1} / {len(catalog_pages)}",
            font=("Arial", 12, "bold"),
            fg="#f6f5fd", bg="#40246c"
        )
        page_indicator.pack(side="left")

        def next_page():
            current_page["idx"] = (current_page["idx"] + 1) % len(catalog_pages)
            build_games_page()

            

        def prev_page():
            current_page["idx"] = (current_page["idx"] - 1) % len(catalog_pages)
            build_games_page()

        prev_btn = tk.Button(nav_bar, text="← Prev", command=prev_page)
        style_button(prev_btn, bg="#6B3FB3", fsize=12)
        prev_btn.pack(side="right", padx=(0, 8))

        next_btn = tk.Button(nav_bar, text="Next →", command=next_page)
        style_button(next_btn, bg="#6B3FB3", fsize=12)
        next_btn.pack(side="right")
    
        def open_settings_window():
            win = tk.Toplevel(root)
            win.title("Settings")
            win.geometry("600x400")
            win.configure(bg="#38216a")

        # هيدر شكله نفس باقي الصفحات (اختياري)
            header_bar(win, "الإعدادات ⚙️")

        # صفحة فاضية: لا عناصر إضافية
        # (لو حبيت لاحقاً تضيف خيارات، أضفها هنا)

    def build_dashboard_page():
    # تنظيف محتوى صفحة الألعاب
        for w in games_frame.pack_slaves():
            w.forget()

    # رأس الصفحة
    header_bar(games_frame, "📊 Dashboard", on_back=build_games_page)

    # جسم الصفحة
    body = tk.Frame(games_frame, bg="#40246c")
    body.pack(fill="both", expand=True, padx=24, pady=18)

    # تحميل الصورة من img_re/Dashboard0.jpg
    img_path = os.path.join("img_re", "Dashboard0.jpg")
    print("المسار:", img_path, "موجود؟", os.path.exists(img_path))
    if os.path.exists(img_path):
        img = Image.open(img_path)
        img = img.resize((300, 300))  # عدّل الحجم حسب الحاجة
        photo = ImageTk.PhotoImage(img)

        img_label = tk.Label(body, image=photo, bg="#40246c")
        img_label.image = photo  # مهم حتى لا تختفي الصورة
        img_label.pack(pady=50)
    else:
        tk.Label(body, text="❌ الصورة غير موجودة", fg="white", bg="#40246c").pack()

    def open_games_page():
        # إيقاف أنيميشن الصفحة الأولى عند الانتقال
        anim_running["on"] = False
        gif_running["on"] = False
        for w in root.pack_slaves():
            w.forget()
        games_frame.pack(fill="both", expand=True)
        build_games_page()

    # ربط الأزرار والتنقّل
    btn_play.config(command=lambda: open_games_page() if selected_character_path["path"]
                else messagebox.showwarning("No character", "Please save a character first!"))

    btn_skip.config(command=open_games_page)
    btn_start.config(command=lambda: [welcome_frame.pack_forget(),
                                      character_frame.pack(fill="both", expand=True)])

    # تحميل تلقائي لو وُجد اختيار سابق
    try:
        if os.path.exists("selected_character.json"):
            with open("selected_character.json", "r", encoding="utf-8") as f:
                p = json.load(f).get("path")
                if p and os.path.exists(p):
                    selected_character_path["path"] = p
                    draw_on_saved_canvas(p)
    except Exception as e:
        print("Auto-load error:", e)

    redraw_preview()

# ========= أمثلة لدوال الألعاب =========
def start_game1(): messagebox.showinfo("Tower Building", "Starting Tower Building...")
def start_game2(): messagebox.showinfo("Game 2", "Starting Game 2...")
def start_game3(): messagebox.showinfo("Game 3", "Starting Game 3...")
def start_game4(): messagebox.showinfo("Game 4", "Starting Game 4...")

def start_game_art():
    import cv2, numpy as np, os
    from cvzone.HandTrackingModule import HandDetector

    # إعدادات الفرشاة والممحاة
    brushThickness = 25
    eraserThickness = 100

    # --- تحميل صور الترويسة بالترتيب الذي تريده
    header_dir = os.path.join("Resources", "Header")
    order = [
        ("RE.jpg",  (0,   0, 255), "RED"),    # أحمر
        ("BL.jpg",  (255, 0,   0), "BLUE"),   # أزرق
        ("GR1.jpg", (0, 255,   0), "GREEN"),  # أخضر
        ("DE.jpg",  (0,   0,   0), "ERASER")  # ممحاة
    ]

    overlays, colors, names = [], [], []
    for fname, col, name in order:
        path = os.path.join(header_dir, fname)
        img = cv2.imread(path)
        if img is None:
            # ترويسة بديلة لو الصورة ناقصة
            hdr = np.full((125, 1280, 3), (40, 25, 70), np.uint8)
            cv2.putText(hdr, name, (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 2, (230, 230, 255), 3)
            overlays.append(hdr)
            print(f"⚠️ لم يتم العثور على {path} — تم إنشاء بديل")
        else:
            overlays.append(img)
        colors.append(col)
        names.append(name)

    header = overlays[0]
    drawColor = (255, 0, 255)  # MAGENTA كبداية مرئية
    current_tool = "MAGENTA"

    # --- الكاميرا
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
    cap.set(3, 1280); cap.set(4, 720)
    if not cap.isOpened():
        print("[ART] Camera not available")
        return

    detector = HandDetector(detectionCon=0.65, maxHands=1)
    xp = yp = 0
    imgCanvas = np.zeros((720, 1280, 3), np.uint8)

    while True:
        ok, img = cap.read()
        if not ok: break
        img = cv2.flip(img, 1)

        # كشف اليد
        hands, img = detector.findHands(img, flipType=False)
        if hands:
            hand = hands[0]
            lmList = hand["lmList"]
            fingers = detector.fingersUp(hand)

            # سبابة ووسطى
            x1, y1 = lmList[8][:2]
            x2, y2 = lmList[12][:2]

            # حدود الهيدر + تقسيم العرض لأربع خانات
            hH, wH = header.shape[:2]
            fh, fw = img.shape[:2]
            bins = np.linspace(0, fw, len(overlays) + 1).astype(int)

            # وضع الاختيار: سبابة + وسطى
            if fingers[1] and fingers[2]:
                cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)
                if y1 < hH:
                    for i in range(len(overlays)):
                        if bins[i] < x1 < bins[i + 1]:
                            header = overlays[i]
                            drawColor = colors[i]
                            current_tool = names[i]
                            break
                xp = yp = 0  # ابدأ خط جديد

            # وضع الرسم: سبابة فقط
            elif fingers[1] and not fingers[2]:
                cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1
                thickness = eraserThickness if drawColor == (0, 0, 0) else brushThickness
                cv2.line(img, (xp, yp), (x1, y1), drawColor, thickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, thickness)
                xp, yp = x1, y1
            else:
                xp = yp = 0

        # دمج اللوحة مع الصورة
        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)

        # وضع الهيدر
        hH, wH = header.shape[:2]
        if wH != img.shape[1]:
            header_resized = cv2.resize(header, (img.shape[1], hH))
            img[0:hH, 0:img.shape[1]] = header_resized
        else:
            img[0:hH, 0:wH] = header

        # اسم الأداة الحالية + زر مسح سريع
        cv2.putText(img, f"Tool: {current_tool}  (press 'c' to clear, 'q' to quit)",
                    (20, hH + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (230, 230, 230), 2)

        cv2.imshow("ART ", img)
        key = cv2.waitKey(1) & 0xFF
        if key in [ord('q'), 27]:  # ESC أو q
            break
        if key == ord('c'):
            imgCanvas[:] = 0  # مسح اللوحة

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    build_ui(root, start_game1, start_game2, start_game3, start_game4)
    root.mainloop()