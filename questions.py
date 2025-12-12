from tkinter import ttk #GUI library
import customtkinter as ctk #GUI library
import colors as cl #Colors file
import controlClass as cc #Data control class
import All_in_one as ao #Machine learning program
import tkinter.messagebox as mb #tkinter message box

# ================================================================
# Class for declaring the screens of the questions
# ================================================================
class questionScreen:

    def __init__(self, window):
        self.sleepAmPmBox = None
        self.sleepMinuteBox = None
        self.sleepHourBox = None
        self.window = window
        self.cc = cc.DataManager()
        self.internetStatus = None

        self.sleepHour = ""
        self.sleepMinutes = ""
        self.sleepPeriod = ""

        self.wakeHour = ""
        self.wakeMinutes = ""
        self.wakePeriod = ""

        self.exercise = ""
        self.stress = ""
        self.caffeine = ""

        self.minutes = [f"{n:02d}" for n in range(00, 60)]
        self.hours = [f"{n:02d}" for n in range(1, 13)]
        self.amPm = ["AM", "PM"]
        self.counts = [str(n) for n in range(1, 11)]

    # ================================================================
    # Function for creating the question screen
    # ================================================================
    def allQuestions(self, window):

        allQuestionFrame = ctk.CTkScrollableFrame(window, fg_color=cl.BG_DARK)
        allQuestionFrame.grid(row=1, column=1, sticky="nsew")

        allQuestionFrame.grid_columnconfigure((0, 1, 2), weight=1)

        # MAIN CARD
        mainCard = ctk.CTkFrame(allQuestionFrame, fg_color=cl.BG_CARD, corner_radius=25,
                                border_width=2, border_color=cl.PURPLE_DEEP)
        mainCard.grid(row=0, column=1, padx=40, pady=(20,40), sticky="n")

        # TITLE
        instructionLabel = ctk.CTkLabel(mainCard, text="Sleep Questionnaire", font=("Segoe UI", 28, "bold"),
                                        text_color=cl.TRACK_FILL)
        instructionLabel.pack(pady=(25, 10))

        # SUB TITLE
        subLabel = ctk.CTkLabel(mainCard, text="Please enter the following information.\nBe as accurate as possible!",
                                font=("Segoe UI", 16), text_color=cl.TEXT_SOFT)
        subLabel.pack(pady=(0, 25))
        # ---------------------------------------------------------
        # TOP INSTRUCTION FRAME (NEW)
        # ---------------------------------------------------------
        instructionCard = ctk.CTkFrame(mainCard, fg_color=cl.BG_DARK, corner_radius=15, border_width=1,
                                       border_color=cl.PURPLE_SOFT)
        instructionCard.pack(pady=(0, 30), padx=20, fill="x")

        instructionTitle = ctk.CTkLabel(instructionCard, text="Instructions", font=("Segoe UI", 20, "bold"),
                                        text_color=cl.TEAL_NEON)
        instructionTitle.pack(pady=(15, 5))

        instructionText = ctk.CTkLabel(
            instructionCard,
            text=(
                "Sleep Hour- Input the time you went to sleep (Hour, minute, day period).\n"
                "Wake Hour- Input the time you woke up (Hour, minute, day period).\n"
                "Exercise- Input the amount of exercise in a scale from 1(low amount of exercise) to 10 (high amount of exercise).\n"
                "Stress Level- Input the amount of stress you feel in a scale from 1(low stress) to 10 (high stress).\n"
                "Caffeine Beverages- Input the amount of beverages with caffeine that you drank.\n"
                "Screen Time- Enter the amount of hours that you used a screen before going to skeep."
            ), font=("Segoe UI", 14), text_color=cl.TEXT_SOFT, justify="left", wraplength= 700)
        instructionText.pack(pady=10, padx=5)

        # 2-COLUMN LAYOUT
        tripleContainer = ctk.CTkFrame(mainCard, fg_color=cl.BG_CARD)
        tripleContainer.pack(pady=(10, 10))

        self.sleepWakeExercise(tripleContainer)
        self.caffeineStressScreen(tripleContainer)

        # SUBMIT BUTTON
        calculateButton = ctk.CTkButton(mainCard, text="Submit Answers", font=("Segoe UI", 18, "bold"), fg_color=cl.PINK_HOT,
                                        hover_color=cl.PURPLE_DEEP, text_color="white", corner_radius=12, width=150,
                                        height=35, command=self.sendInfo)
        calculateButton.pack(pady=5)

        allQuestionFrame.tkraise()

    # =============================================================================
    # Function for creating the boxes in which the user will input the information
    # =============================================================================
    def sleepWakeExercise(self, tripleContainer):

        tripleContainer.columnconfigure(0, weight=1)

        card = ctk.CTkFrame(tripleContainer, fg_color=cl.BG_DARK, corner_radius=20, border_width=1,
                            border_color=cl.PURPLE_SOFT)
        card.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")

        header = ctk.CTkLabel(card, text="Sleep - Wake Times",  font=("Segoe UI", 22, "bold"),
                              text_color=cl.TEAL_NEON)
        header.pack(pady=(25, 10))

        inner = ctk.CTkFrame(card, fg_color=cl.BG_DARK)
        inner.pack(padx=25, pady=20, fill="both")

        # ----------- SLEEP -----------
        sleepFrame = ctk.CTkFrame(inner, fg_color=cl.BG_DARK)
        sleepFrame.pack(pady=20, anchor="w")

        sleepRow = ctk.CTkFrame(sleepFrame, fg_color=cl.BG_DARK)
        sleepRow.pack(anchor="w")

        sleepLabel = ctk.CTkLabel(sleepRow, text="Sleep Hour:",font=("Segoe UI", 16, "bold"),
                                  text_color=cl.TEXT_SOFT)
        sleepLabel.pack(side="left", padx=(0, 15))

        self.sleepHourBox = ttk.Combobox(sleepRow, values=self.hours, state="readonly",
                                         width=5, font=("Segoe UI", 14))
        self.sleepHourBox.set(self.hours[0])
        self.sleepHourBox.pack(side="left", padx=6)

        self.sleepMinuteBox = ttk.Combobox(sleepRow, values=self.minutes, state="readonly",
                                           width=5, font=("Segoe UI", 14))
        self.sleepMinuteBox.set(self.minutes[0])
        self.sleepMinuteBox.pack(side="left", padx=6)

        self.sleepAmPmBox = ttk.Combobox(sleepRow, values=self.amPm, state="readonly",
                                         width=5, font=("Segoe UI", 14))
        self.sleepAmPmBox.set(self.amPm[0])
        self.sleepAmPmBox.pack(side="left", padx=6)

        # ----------- WAKE -----------
        wakeFrame = ctk.CTkFrame(inner, fg_color=cl.BG_DARK)
        wakeFrame.pack(pady=20, anchor="w")

        wakeRow = ctk.CTkFrame(wakeFrame, fg_color=cl.BG_DARK)
        wakeRow.pack(anchor="w")

        wakeLabel = ctk.CTkLabel(wakeRow, text="Wake Hour:", font=("Segoe UI", 16, "bold"),
                                 text_color=cl.TEXT_SOFT)
        wakeLabel.pack(side="left", padx=(0, 15))

        self.wakeHourBox = ttk.Combobox(wakeRow, values=self.hours, state="readonly", width=5,
                                        font=("Segoe UI", 14))
        self.wakeHourBox.set(self.hours[0])
        self.wakeHourBox.pack(side="left", padx=6)

        self.wakeMinuteBox = ttk.Combobox(wakeRow, values=self.minutes, state="readonly",width=5,
                                          font=("Segoe UI", 14))
        self.wakeMinuteBox.set(self.minutes[0])
        self.wakeMinuteBox.pack(side="left", padx=6)

        self.wakeAmPmBox = ttk.Combobox(wakeRow, values=self.amPm, state="readonly", width=5,
                                        font=("Segoe UI", 14))
        self.wakeAmPmBox.set(self.amPm[0])
        self.wakeAmPmBox.pack(side="left", padx=6)

        # ----------- EXERCISE -----------
        exerciseRow = ctk.CTkFrame(inner, fg_color=cl.BG_DARK)
        exerciseRow.pack(pady=20, anchor="w")

        exerciseLabel = ctk.CTkLabel(exerciseRow, text="Exercise:", font=("Segoe UI", 16, "bold"),
                                     text_color=cl.TEXT_SOFT)
        exerciseLabel.pack(side="left", padx=(0, 15))

        self.exerciseBox = ttk.Combobox(exerciseRow, values=self.counts, state="readonly", width=5,
                                        font=("Segoe UI", 14))
        self.exerciseBox.set(self.counts[0])
        self.exerciseBox.pack(side="left", padx=6)

    # =============================================================================
    # More boxes for inputting information
    # =============================================================================
    def caffeineStressScreen(self, tripleContainer):
        tripleContainer.columnconfigure(1, weight=1)

        card = ctk.CTkFrame(tripleContainer, fg_color=cl.BG_DARK, corner_radius=20, border_width=1,
                            border_color=cl.PURPLE_SOFT)
        card.grid(row=0, column=1, padx=15, pady=10, sticky="nsew")

        header = ctk.CTkLabel(card, text="Stress - Caffeine - Screen", font=("Segoe UI", 22, "bold"),
                              text_color=cl.PINK_HOT)
        header.pack(pady=(25, 10))

        # INNER WRAPPER — Adds BIGGER space inside the card
        inner = ctk.CTkFrame(card, fg_color=cl.BG_DARK)
        inner.pack(padx=25, pady=20, fill="both")

        # ----------- STRESS -----------
        stressFrame = ctk.CTkFrame(inner, fg_color=cl.BG_DARK)
        stressFrame.pack(anchor="w", pady=20)

        stressLabel = ctk.CTkLabel(stressFrame, text="Stress Level:", font=("Segoe UI", 16, "bold"),
                                   text_color=cl.TEXT_SOFT)
        stressLabel.pack(side="left", padx=(0, 15))

        self.stressBox = ttk.Combobox(stressFrame, values=self.counts, state="readonly",
                                      width=5, font=("Segoe UI", 14))
        self.stressBox.set(self.counts[0])
        self.stressBox.pack(side="left", padx=8)

        # ----------- CAFFEINE -----------
        caffeineFrame = ctk.CTkFrame(inner, fg_color=cl.BG_DARK)
        caffeineFrame.pack(anchor="w", pady=20)

        caffeineLabel = ctk.CTkLabel(caffeineFrame, text="Caffeine Beverages:", font=("Segoe UI", 16, "bold"),
                                     text_color=cl.TEXT_SOFT)
        caffeineLabel.pack(side="left", padx=(0, 20))

        self.caffeineBox = ttk.Combobox(caffeineFrame, values=self.counts, state="readonly",
                                        width=5, font=("Segoe UI", 14))
        self.caffeineBox.set(self.counts[0])
        self.caffeineBox.pack(side="left", padx=8)

        # ----------- SCREEN TIME -----------
        screenFrame = ctk.CTkFrame(inner, fg_color=cl.BG_DARK)
        screenFrame.pack(anchor="w", pady=20)

        screenLabel = ctk.CTkLabel(screenFrame, text="Screen Time:", font=("Segoe UI", 16, "bold"),
                                   text_color=cl.TEXT_SOFT)
        screenLabel.pack(side="left", padx=(0, 20))

        self.screenBox = ttk.Combobox(screenFrame, values=self.counts, state="readonly", width=5,
                                      font=("Segoe UI", 14))
        self.screenBox.set(self.counts[0])
        self.screenBox.pack(side="left", padx=8)

    # =============================================================================
    # Function for sending all the info that was gathered from the user
    # =============================================================================
    def sendInfo(self):

        sh = self.sleepHourBox.get()
        sm = self.sleepMinuteBox.get()
        sp = self.sleepAmPmBox.get()

        wh = self.wakeHourBox.get()
        wm = self.wakeMinuteBox.get()
        wp = self.wakeAmPmBox.get()


        if sh == wh and sm == wm and sp == wp:
            mb.showerror(
                "Invalid Input",
                "Sleep time and wake time cannot be the same.")
            continueCheck = False

        elif not self.internetStatus:
            mb.showerror(
                "No internet",
                "Check your internet connection or pay our monthly\n"
                "subscription for just $15.99 and unlock offline mode!")
            continueCheck = False

        elif self.cc.date in self.cc.users[self.cc.username]["dates"]:
            answer = mb.askyesno(
                "Overwrite Data?",
                "You already submitted your results today.\n\n"
                "Do you want to generate and overwrite today's data?")
            if answer:
                continueCheck = True
            else:
                continueCheck = False
        else:
            continueCheck = True
        if continueCheck:
            results = {
                "sleepHours": self.sleepHourBox.get(),
                "sleepMinutes": self.sleepMinuteBox.get(),
                "sleepPeriod": self.sleepAmPmBox.get(),
                "wakeHours": self.wakeHourBox.get(),
                "wakeMinutes": self.wakeMinuteBox.get(),
                "wakePeriod": self.wakeAmPmBox.get(),
                "sleep": "",
                "exerciseLevel": self.exerciseBox.get(),
                "stressLevel": self.stressBox.get(),
                "caffeineLevel": self.caffeineBox.get(),
                "screenTime": self.screenBox.get(),
                "sleepEfficiency": "",
                "spotifyFirstName": "",
                "spotifyPlayListOne": "",
                "spotifySecondName": "",
                "spotifyPlayListTwo": "",
                "spotifyThirdName": "",
                "spotifyPlayListThree": "",
                "recommendation": "",
            }

            age = int(self.cc.users[self.cc.username]["age"])

            results = ao.start(results, age)


            self.cc.saveDaily(results, self.window)

