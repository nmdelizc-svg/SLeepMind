import tkinter as tk #GUI library
import customtkinter as ctk #GUI library
import re #Search for patters
import math #Values for logo creation
import colors as cl #Import colors file
import menuWindow as mw #Import the next class for screens
import controlClass as cc #Class with the data control

# ==========================================================
# Class that will initialize the program
# ==========================================================
class sleepyMind:
    def __init__(self):


        # Data Manager
        self.cc = cc.DataManager()

        # ===== MAIN WINDOW =====
        self.window = ctk.CTk()
        self.window.title("Sign Up")
        self.window.geometry("1400x850")
        self.window.minsize(900, 600)


        # Layout
        self.window.grid_columnconfigure(0, weight=0)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)

        # Auto scaling
        self.auto_scale()
        self.window.after(300, self.auto_scale)

        # Start in Sign In
        self.signInCreate()

        self.window.mainloop()

    # ==========================================================
    # Scale the window according to the size
    # ==========================================================
    def auto_scale(self, event=None):
        screen_width = self.window.winfo_width()

        # New scaling formula:
        scale = screen_width / 1400
        scale = max(1.1, min(scale, 1.35))

        ctk.set_widget_scaling(scale)
        ctk.set_window_scaling(scale)

    # ==========================================================
    # Warning labels for wrong input
    # ==========================================================
    def warnings(self, text, frame):
        warningLabel = tk.Label(frame, text=text, bg=cl.BG_NAVY, fg="red",
                                font=("Segoe UI", 10, "bold"))
        warningLabel.grid(row=12, column=0, pady=(5, 0))
        self.window.after(2000, warningLabel.config, {"text": ""})

    # ==========================================================
    # Logo of out program
    # ==========================================================
    def sleepmindIntroFrame(self, parent):
        frame = tk.Frame(parent, bg=cl.BG_NAVY)
        frame.grid(row=0, column=1, rowspan=2, sticky="nsew")

        # Layout
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        canvas = tk.Canvas(frame, bg=cl.BG_NAVY, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        def redraw(event=None):
            canvas.delete("all")
            w = canvas.winfo_width()
            cx = w // 2
            cy = 300

            # SleepMind Title
            canvas.create_text(cx, cy - 10, text="S L E E P M I N D", font=("Segoe UI", 48, "bold"),
                               fill=cl.PINK_HOT)

            canvas.create_text(cx, cy + 35, text="Optimize Your Rest", font=("Segoe UI", 18),
                               fill=cl.TEXT_SOFT)

            # LEFT ARC
            canvas.create_arc(cx - 310, cy - 80, cx - 60, cy + 60, start=120, extent=120,
                              style="arc", width=6, outline=cl.PURPLE_DEEP)

            # RIGHT ARC
            canvas.create_arc(cx + 60, cy - 80, cx + 310, cy + 60, start=300, extent=120,
                              style="arc", width=6, outline=cl.PURPLE_DEEP)

            # Wave
            length = 500
            amp = 10
            y = cy + 130
            for i in range(length - 1):
                x1 = cx - length // 2 + i
                x2 = x1 + 1
                y1 = y + amp * math.sin(i / 20)
                y2 = y + amp * math.sin((i + 1) / 20)
                canvas.create_line(x1, y1, x2, y2, fill=cl.TEAL_NEON, width=2)

        canvas.bind("<Configure>", redraw)
        return frame

    # ==========================================================
    # Validation for the password inputted
    # ==========================================================
    def regex(self, password, checkLabels):
        conditionStatus = { "Number": True, "Capital": True,
                            "LowerCase": True, "Symbol": True,
                            "WordLength": True }

        checks = [
            (re.search(r"\d+", password), "Contains a Number ✓",  "Contains a Number ✗",  checkLabels[0], "Number"),
            (re.search(r"[a-z]", password), "Contains a Lowercase Letter ✓", "Contains a Lowercase Letter ✗", checkLabels[1], "LowerCase"),
            (re.search(r"[A-Z]", password), "Contains a Capital Letter ✓",   "Contains a Capital Letter ✗",   checkLabels[2], "Capital"),
            (re.search(r"\W", password), "Contains a Symbol ✓",  "Contains a Symbol ✗", checkLabels[3], "Symbol"),
            (len(password) >= 10, "Contains at least 10 characters ✓", "Contains at least 10 characters ✗", checkLabels[4], "WordLength")
        ]

        for result, okMsg, noMsg, label, key in checks:
            if result:
                label.config(text=okMsg, fg="green")
                conditionStatus[key] = True
            else:
                label.config(text=noMsg, fg="red")
                conditionStatus[key] = False

        return conditionStatus

    # ==========================================================
    # Check for the sign up screen
    # ==========================================================
    def signUpChecker(self, frame, username, password, labels, age, profession):
        if username not in self.cc.users:
            if username:
                chk = self.regex(password, labels)
                if all(chk.values()):
                    self.cc.username = username
                    self.cc.users[username] = {
                        "name": username,
                        "password": password,
                        "age": str(int(age)),
                        "profession": profession
                    }
                    self.cc.saveUser()
                    mw.menu(self.window)
            else:
                self.warnings("Create a username!", frame)
        else:
            self.warnings("That username already exists!", frame)

    # ==========================================================
    # Check for the sign in screen
    # ==========================================================
    def signInChecker(self, username, password, frame):
        if username == "":
            self.warnings("Enter a Username", frame)

        elif username not in self.cc.users or password != self.cc.users[username]["password"]:
            self.warnings("Wrong username or password", frame)

        else:
            self.cc.username = username
            mw.menu(self.window)

    # ==========================================================
    # Update the slider label
    # ==========================================================
    def update_age(self, val):
        self.ageLabel.configure(text=f"Age: {int(float(val))}")

    # ==========================================================
    # Sign Up Screen
    # ==========================================================
    def signUpCreate(self):

        # LEFT PANEL
        frame = ctk.CTkFrame(self.window, fg_color=cl.BG_NAVY)
        frame.grid(row=0, column=0, rowspan=2, sticky="nsw")
        frame.grid_propagate(False)
        frame.configure(width=420)
        frame.columnconfigure(0, weight=1)

        # RIGHT PANEL
        self.sleepmindIntroFrame(self.window)

        # TITLE
        logo = ctk.CTkLabel(frame, text="● SIGN UP", text_color=cl.TEXT_WHITE,
                            font=("Segoe UI", 20, "bold"))
        logo.grid(row=0, column=0, pady=10)

        # ICON
        ctk.CTkLabel(frame, text="👤", text_color=cl.TEAL_NEON,
                     font=("Segoe UI Emoji", 60)).grid(row=1, column=0, pady=20)

        # USERNAME
        ctk.CTkLabel(frame, text="USERNAME", text_color=cl.TEXT_SOFT,
                     font=("Segoe UI", 12, "bold")).grid(row=2, column=0,
                                                          sticky="w", padx=60)

        userEntry = ctk.CTkEntry(frame, fg_color=cl.BG_CARD,
                                 text_color=cl.TEXT_WHITE,
                                 font=("Segoe UI", 14))
        userEntry.grid(row=3, column=0, padx=60, pady=(0, 20), sticky="ew")

        # AGE SLIDER
        self.ageLabel = ctk.CTkLabel(frame, text="AGE: 10", text_color=cl.TEXT_SOFT,
                                font=("Segoe UI", 12, "bold"))
        self.ageLabel.grid(row=4, column=0, padx=60, sticky="w")

        slider = ctk.CTkSlider(frame, from_=10, to=100, command=self.update_age)
        slider.grid(row=5, column=0, padx=60, pady=(0, 30), sticky="ew")
        slider.set(slider._from_)

        # PROFESSION
        ctk.CTkLabel(frame, text="ENTER PROFESSION",
                     text_color=cl.TEXT_SOFT,
                     font=("Segoe UI", 12, "bold")).grid(row=6, column=0,
                                                         sticky="w", padx=60)

        profEntry = ctk.CTkEntry(frame, fg_color=cl.BG_CARD,
                                 text_color=cl.TEXT_WHITE,
                                 font=("Segoe UI", 14))
        profEntry.grid(row=7, column=0, padx=60, pady=(0, 20), sticky="ew")

        # PASSWORD
        ctk.CTkLabel(frame, text="PASSWORD", text_color=cl.TEXT_SOFT,
                     font=("Segoe UI", 12, "bold")).grid(row=8, column=0,
                     sticky="w", padx=60)

        passEntry = ctk.CTkEntry(frame, fg_color=cl.BG_CARD, text_color=cl.TEXT_WHITE,
                                 font=("Segoe UI", 14), show="*")
        passEntry.grid(row=9, column=0, padx=60, sticky="ew")

        # PASSWORD CHECKS
        validateFrame = tk.Frame(frame, bg=cl.BG_NAVY)
        validateFrame.grid(row=10, column=0, sticky="w", padx=60)

        checkTexts = [
            "Contains a Number ✗",
            "Contains a Lowercase Letter ✗",
            "Contains a Capital Letter ✗",
            "Contains a Symbol ✗",
            "Contains at least 10 characters ✗"
        ]

        checkLabels = []
        for t in checkTexts:
            lab = tk.Label(validateFrame, text=t, fg="red", bg=cl.BG_NAVY,
                           font=("Segoe UI", 10, "bold"))
            lab.pack(anchor="w")
            checkLabels.append(lab)

        passEntry.bind("<KeyRelease>", lambda e:
                       self.regex(passEntry.get(), checkLabels))

        # SUBMIT
        ctk.CTkButton(frame, text="Sign Up to Account", fg_color=cl.PINK_HOT,
                      text_color="white", command=lambda: self.signUpChecker(
                          frame,
                          userEntry.get(),
                          passEntry.get(),
                          checkLabels,
                          slider.get(),
                          profEntry.get()
                      )).grid(row=11, column=0, pady=40)

        # SIGN IN LINK
        link = ctk.CTkLabel(frame, text="Already Have an Account? Sign In",
                            text_color="grey", cursor="hand2",
                            font=("Segoe UI", 9))
        link.grid(row=12, column=0)
        link.bind("<Enter>", lambda e: link.configure(text_color=cl.PURPLE_MEDIUM, font=("Segoe UI", 9, "underline")))
        link.bind("<Leave>", lambda e: link.configure(text_color="gray", font=("Segoe UI", 9)))
        link.bind("<Button-1>", lambda e: self.signInCreate())

    # ==========================================================
    # Sign In Screen
    # ==========================================================
    def signInCreate(self):
        # LEFT PANEL
        frame = ctk.CTkFrame(self.window, fg_color=cl.BG_NAVY)
        frame.grid(row=0, column=0, rowspan=2, sticky="nsw")
        frame.grid_propagate(False)
        frame.configure(width=420)
        frame.columnconfigure(0, weight=1)

        # RIGHT PANEL
        self.sleepmindIntroFrame(self.window)

        # TITLE
        ctk.CTkLabel(frame, text="● SIGN IN", text_color=cl.TEXT_WHITE,
                     font=("Segoe UI", 20, "bold")).grid(row=0, column=0, pady=30)

        # ICON
        ctk.CTkLabel(frame, text="👤", text_color=cl.TEAL_NEON,
                     font=("Segoe UI Emoji", 60)).grid(row=1, column=0, pady=20)

        # USERNAME
        ctk.CTkLabel(frame, text="USERNAME", text_color=cl.TEXT_SOFT,
                     font=("Segoe UI", 12, "bold")).grid(row=2, column=0,
                                                         sticky="w", padx=40)

        userEntry = ctk.CTkEntry(frame, fg_color=cl.BG_CARD, text_color=cl.TEXT_WHITE,
                                 font=("Segoe UI", 14))
        userEntry.grid(row=3, column=0, padx=40, pady=(0, 40), sticky="ew")

        # PASSWORD
        ctk.CTkLabel(frame, text="PASSWORD", text_color=cl.TEXT_SOFT,
                     font=("Segoe UI", 12, "bold")).grid(row=4, column=0, sticky="w", padx=40)

        passEntry = ctk.CTkEntry(frame, fg_color=cl.BG_CARD,  text_color=cl.TEXT_WHITE,
                                 font=("Segoe UI", 14), show="*")
        passEntry.grid(row=5, column=0, padx=40, sticky="ew")

        # LOGIN BUTTON
        ctk.CTkButton(frame, text="Sign in to Account", fg_color=cl.PINK_HOT, text_color="white",
                      command=lambda: self.signInChecker(
                          userEntry.get(),
                          passEntry.get(),
                          frame
                      )).grid(row=6, column=0, pady=40)

        # SWITCH TO SIGN UP
        link = ctk.CTkLabel(frame, text="Don't Have an Account? Sign Up", text_color="grey", cursor="hand2",
                            font=("Segoe UI", 9))
        link.grid(row=7, column=0, sticky="w", padx=40)
        link.bind("<Enter>", lambda e: link.configure(text_color=cl.PURPLE_MEDIUM, font=("Segoe UI", 9, "underline")))
        link.bind("<Leave>", lambda e: link.configure(text_color="gray", font=("Segoe UI", 9)))
        link.bind("<Button-1>", lambda e: self.signUpCreate())


# Start Program
sleepyMind()
