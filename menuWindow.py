import customtkinter as ctk #GUI library
import tkinter as tk #GUI library
import webbrowser #Open links
import colors as cl #Colors file
import questions as aq #Import Questions file
import controlClass as cc #Import class with data control
import matplotlib.pyplot as plt #For graphs
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #For graphs
import requests #Internet Check
from PIL import Image #For spotify functions
from io import BytesIO #For spotify functions
import spotipy #For spotify functions
from spotipy.oauth2 import SpotifyClientCredentials #For spotify functions
import networkXGraphs as vg #NetworkX graphs

# ==========================================================
# Class that will initialize the different windows
# ==========================================================
class menu:
    def __init__(self, window):
        self.secondResultLabel = None
        self.firstResultLabel = None
        self.firstResultFrame = None
        self.secondResultFrame = None
        self.resultsContainer = None
        self.sp = None
        self.comparison = None
        self.sleepHoursLabel = None
        self.sleep_bar = None
        self.last_hours = None
        self.last_date = None
        self.last_spotify = None
        self.coverData = None
        self.errorMessage = None
        self.bottomRightEmoji = None
        self.spotifyFrame = None
        self.coverFrame = None
        self.dayWheel = None
        self.monthWheel = None
        self.yearWheel = None
        self.dayIndex = 0
        self.monthIndex = 0
        self.yearIndex = 0
        self.dayList = list(f"{m:02d}" for m in range(1, 32))
        self.monthList = [f"{m:02d}" for m in range(1, 13)]
        self.yearList = list(range(2000, 2031))
        self.window = window
        self.running = True
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.internetStatus = True
        self.cc = cc.DataManager()
        self.aq = aq.questionScreen(window)
        self.spotifyObtain()
        self.initializeCoverScreen()
        self.autoUpdate()

    # ==========================================================
    # Make sure the program closes correctly
    # ==========================================================
    def on_close(self):
        self.running = False
        self.window.destroy()

    # ==========================================================
    # Obtain the credentials of spotify
    # ==========================================================
    def spotifyObtain(self):

        CLIENT_ID = "1"
        CLIENT_SECRET = "1"

        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        )

    # =================================================================
    # 1.Load the playlist and the image of the playlist to the program
    # =================================================================
    def load_image_from_url(self, url, size=(70, 70)):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = img.resize(size, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)

    # ================================================================
    # Get the playlist image from the URL
    # ================================================================
    def get_playlist_image(self, playlist_url):

        image_url = None
        try:
            playlist_id = playlist_url.split("/")[-1].split("?")[0]
            data = self.sp.playlist(playlist_id)

            if data.get("images"):
                image_url = data["images"][0]["url"]

        except Exception:
            image_url = None

        return image_url

    # ========================================================================
    # Display the playlist in a row, including the image, title, and the link
    # ========================================================================
    def display_playlist_row(self, container, title, url, text_color):
        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(anchor="w", pady=8, padx=10, fill="x")

        # Playlist image
        img_url = self.get_playlist_image(url)

        if img_url:
            img = self.load_image_from_url(img_url, size=(70, 70))
            row.img_keep_alive = img
            ctk.CTkLabel(row, image=img, text="", fg_color="transparent").pack(side="left", padx=(0, 12))
        else:
            ctk.CTkLabel(row, text="No image", text_color=text_color).pack(side="left", padx=(0, 12))

        # Playlist title
        ctk.CTkLabel(row, text=title, font=("Segoe UI", 14, "bold"), text_color=text_color,
                     fg_color="transparent", wraplength=300,).pack(anchor="w")

        # Clickable link
        link = ctk.CTkLabel(row, text="Open Playlist", font=("Segoe UI", 12, "underline"),
                            text_color="gray", fg_color="transparent", cursor="hand2")
        link.pack(anchor="w")

        link.bind("<Button-1>", lambda e: webbrowser.open(url))
        link.bind("<Enter>", lambda e: link.configure(text_color=cl.TEAL_NEON))
        link.bind("<Leave>", lambda e: link.configure(text_color="gray"))

    # ======================================================================
    # Will create the section for the spotify playlist with the three parts
    # ======================================================================
    def spotifyCreate(self):

        dates = self.cc.users[self.cc.username].get("dates", {})

        if len(dates) == 0:
            return  # Nothing to show

        # Clear old UI
        for item in self.spotifyFrame.winfo_children():
            item.destroy()

        # Get latest date
        latestDate = list(dates.keys())[-1]
        dayData = dates[latestDate]

        # Read playlists from JSON
        p1_url = dayData.get("spotifyPlayListOne", "")
        p2_url = dayData.get("spotifyPlayListTwo", "")
        p3_url = dayData.get("spotifyPlayListThree", "")

        p1_title = dayData.get("spotifyFirstName", "")
        p2_title = dayData.get("spotifySecondName", "")
        p3_title = dayData.get("spotifyThirdName", "")

        playlists = [
            (p1_title, p1_url),
            (p2_title, p2_url),
            (p3_title, p3_url)
        ]

        # Filter out playlists with no URL
        playlists = [(title, url) for title, url in playlists if url]

        if not playlists:
            # No playlists saved
            notComplete = ctk.CTkFrame(self.spotifyFrame, fg_color="transparent")
            notComplete.pack(anchor="w", pady=8, padx=10, fill="x")
            ctk.CTkLabel(notComplete, text="No playlists yet.\nComplete your sleep test to unlock recommendations!",
                         font=("Segoe UI", 12), text_color=cl.TEXT_SOFT, fg_color="transparent", justify="left").pack(anchor="w", padx=25)
        else:
            # Display each playlist row
            for title, url in playlists:
                self.display_playlist_row(self.spotifyFrame, title, url, text_color=cl.TEXT_SOFT)

    # ================================================================
    # Auto update for the left frame
    # ================================================================
    def autoUpdate(self):

        dates = self.cc.users[self.cc.username].get("dates", {})

        if len(dates) == 0:
            latest_date = None
            sleep_str = 0
        else:
            latest_date = list(dates.keys())[-1]
            sleep_str = int(dates[latest_date].get("sleep", 0))

        try:
            hours = int(sleep_str)
        except:
            hours = 0

        age = int(self.cc.users[self.cc.username]["age"])

        # Compute recommended sleep
        if 10 <= age < 13:
            recommended = 9
        elif 13 <= age <= 18:
            recommended = 8
        else:
            recommended = 7

        # ========= CHANGE DETECTION ==========
        changed = (hours != self.last_hours or latest_date != self.last_date)


        if not changed:
            # Schedule next check without rerendering UI
            self.window.after(2000, self.autoUpdate)
            return
        # ======================================

        # Store new state
        self.last_hours = hours
        self.last_date = latest_date

        # --- Color logic ---
        if hours < recommended * 0.5:
            color = "#FF4B4B"
        elif hours < recommended:
            color = "#F5C542"
        else:
            color = "#2ECC71"

        percentage = min(hours / recommended, 1)

        self.sleep_bar.configure(progress_color=color)
        self.sleep_bar.set(percentage)

        self.sleepHoursLabel.configure(text=f"{hours} hrs last night")

        # --- Comparison ---
        if latest_date is None:
            self.comparison.configure(text="No data available", text_color=cl.TEXT_SOFT)

        elif hours < recommended:
            self.comparison.configure(text="⬅️ Below recommended", text_color="#FF4B4B")

        elif hours == recommended:
            self.comparison.configure(text="➡️ Same as recommended", text_color="#3498DB")

        else:
            self.comparison.configure(text="➡️ Above recommended", text_color="#2ECC71")

        # ===== UPDATE SPOTIFY only if song changed =====
        self.spotifyCreate()

        # Schedule next update
        self.window.after(2000, self.autoUpdate)

    # ================================================================
    # Output the selected data by the user
    # ================================================================
    def connectDataButton(self):

        date = f"{self.yearWheel.cget("text")}-{self.monthWheel.cget("text")}-{self.dayWheel.cget("text")}"
        if date in self.cc.users[self.cc.username]["dates"]:


            sleep = self.cc.users[self.cc.username]["dates"][date]["sleep"]
            hourSleep = self.cc.users[self.cc.username]["dates"][date]["sleepHours"]
            minuteSleep = self.cc.users[self.cc.username]["dates"][date]["sleepMinutes"]
            periodSleep = self.cc.users[self.cc.username]["dates"][date]["sleepPeriod"]
            hourWake = self.cc.users[self.cc.username]["dates"][date]["wakeHours"]
            minuteWake = self.cc.users[self.cc.username]["dates"][date]["wakeMinutes"]
            periodWake = self.cc.users[self.cc.username]["dates"][date]["wakePeriod"]
            exercise = self.cc.users[self.cc.username]["dates"][date]["exerciseLevel"]
            stress = self.cc.users[self.cc.username]["dates"][date]["stressLevel"]
            caffeine = self.cc.users[self.cc.username]["dates"][date]["caffeineLevel"]
            screen = self.cc.users[self.cc.username]["dates"][date]["screenTime"]
            sleepEfficiency = self.cc.users[self.cc.username]["dates"][date]["sleepEfficiency"]
            spotifyFirst = self.cc.users[self.cc.username]["dates"][date]["spotifyFirstName"]
            spotifyPlaylistFirst = self.cc.users[self.cc.username]["dates"][date]["spotifyPlayListOne"]
            spotifySecond = self.cc.users[self.cc.username]["dates"][date]["spotifySecondName"]
            spotifyPlaylistSecond = self.cc.users[self.cc.username]["dates"][date]["spotifyPlayListTwo"]
            spotifyThird = self.cc.users[self.cc.username]["dates"][date]["spotifyThirdName"]
            spotifyPlaylistThird = self.cc.users[self.cc.username]["dates"][date]["spotifyPlayListThree"]
            recommendations = self.cc.users[self.cc.username]["dates"][date]["recommendation"]
            self.resultsContainer.tkraise()
            self.firstResultLabel.configure(

                text=
                "- Sleep Summary\n"
                "---------------------------------------------\n"
                "{:<16}: {}\n".format("Slept Hours", sleep) +
                "{:<16}: {}:{}{}\n".format("Went to Sleep", hourSleep, minuteSleep, periodSleep) +
                "{:<16}: {}:{}{}\n".format("Woke Up", hourWake, minuteWake, periodWake) +
                "\n"

                "- Health Inputs\n"
                "---------------------------------------------\n"
                "{:<16}: {}\n".format("Exercise", exercise) +
                "{:<16}: {}\n".format("Stress", stress) +
                "{:<16}: {}\n".format("Caffeine", caffeine) +
                "{:<16}: {}\n".format("Screen Time", screen) +
                "{:<16}: {}\n".format("Sleep Efficiency", sleepEfficiency) +
                "\n"

                "- Spotify Recommendations\n"
                "---------------------------------------------\n"
                " Title 1       : {}\n"
                " Playlist 1    : {}\n\n"
                " Title 2       : {}\n"
                " Playlist 2    : {}\n\n"
                " Title 3       : {}\n"
                " Playlist 3    : {}\n"
                .format(
                    spotifyFirst,
                    spotifyPlaylistFirst,
                    spotifySecond,
                    spotifyPlaylistSecond,
                    spotifyThird,
                    spotifyPlaylistThird
                ),

                anchor="w",
                justify="left",
                wraplength=320
            )

            self.secondResultLabel.configure(text=f"{recommendations}", justify="center",
                                             anchor= "center")

        else:
            self.coverData.tkraise()
            errorLabel = ctk.CTkLabel(self.coverData, text="DATA NOT AVAILABLE", font=("Segoe UI", 20, "bold"),
                                      text_color="red")
            errorLabel.place(relx=0.5, rely=0.5, anchor="center")
            self.errorMessage.after(1200, errorLabel.destroy)

    # ================================================================
    # Check for internet connection
    # ================================================================
    def internetCheck(self):

        if self.running:
            try:
                requests.get("https://www.google.com", timeout=3)
                self.bottomRightEmoji.configure(text="🌐")
                self.aq.internetStatus = True

                # online
            except requests.exceptions.ConnectionError:
                self.bottomRightEmoji.configure(text="❌")
                self.aq.internetStatus = False
            self.window.after(2000, self.internetCheck)

    # ================================================================
    # Function for clearing the screen
    # ================================================================
    def clearScreen(self):
        # Destroy everything inside row=1 column=1
        for widget in self.window.grid_slaves(row=1, column=1):
            widget.destroy()

    # =====================================================================
    # Three functions for the scrolling labels used for selecting the date
    # =====================================================================
    def dayScroll(self, event):
        if event.delta > 0:
            self.dayIndex = (self.dayIndex + 1) % len(self.dayList)
        else:
            self.dayIndex = (self.dayIndex - 1) % len(self.dayList)

        self.dayWheel.configure(text=str(self.dayList[self.dayIndex]))

    def monthScroll(self, event):
        if event.delta > 0:
            self.monthIndex = (self.monthIndex + 1) % len(self.monthList)
        else:
            self.monthIndex = (self.monthIndex - 1) % len(self.monthList)

        self.monthWheel.configure(text=str(self.monthList[self.monthIndex]))

    def yearScroll(self, event):
        if event.delta > 0:
            self.yearIndex = (self.yearIndex + 1) % len(self.yearList)
        else:
            self.yearIndex = (self.yearIndex - 1) % len(self.yearList)

        self.yearWheel.configure(text=str(self.yearList[self.yearIndex]))

    # ================================================================
    # Function for clearing the screen
    # ================================================================
    def sleepHours(self):

        dates = self.cc.users[self.cc.username].get("dates", {})

        if len(dates) == 0:
            # no sleep data yet
            latest_date = None
            hours = 0
        else:
            latest_date = list(dates.keys())[-1]
            hours = int(dates[latest_date].get("sleepHours", 0))
        return hours

# =====================================================================================
# Create the new screen that includes information to the left and buttons to the right
# =====================================================================================
    def initializeCoverScreen(self):
        self.coverFrame = ctk.CTkScrollableFrame(self.window, fg_color=cl.BG_NAVY, corner_radius=0, border_color="white", border_width=2)
        self.coverFrame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.coverFrame.grid_rowconfigure(0, weight=1)
        self.coverFrame.grid_columnconfigure(0, weight=1)

        # ======= Modern Card: User Info =======
        userCard = ctk.CTkFrame(self.coverFrame, fg_color=cl.BG_CARD, corner_radius=20, border_width=2,
                                border_color=cl.PURPLE_SOFT)
        userCard.pack(pady=(30, 20), padx=20, fill="both", expand=True)

        avatar = ctk.CTkLabel( userCard, text="👤", font=("Segoe UI Emoji", 70), text_color=cl.TEAL_NEON)
        avatar.pack(pady=(15, 5))

        nameLabel = ctk.CTkLabel(userCard, text=self.cc.users[self.cc.username]["name"], font=("Segoe UI", 20, "bold"),
                                 text_color="white")
        nameLabel.pack()

        ageLabel = ctk.CTkLabel(userCard, text=f"Age: {self.cc.users[self.cc.username]['age']}", font=("Segoe UI", 15),
                                text_color=cl.TEXT_SOFT)
        ageLabel.pack(pady=(0, 15))

        # ======= Sleep Card =======
        sleepCard = ctk.CTkFrame(self.coverFrame, fg_color=cl.BG_CARD, corner_radius=20, border_width=2,
                                 border_color=cl.PURPLE_DEEP)
        sleepCard.pack(pady=(0, 20), padx=20, fill="both", expand=True)

        ctk.CTkLabel(sleepCard, text="Sleep Progress", font=("Segoe UI", 17, "bold"), text_color="white").pack(pady=(12, 8))

        self.sleep_bar = ctk.CTkProgressBar(master=sleepCard, width=250, height=12, corner_radius=8, fg_color="#1A1B33")
        self.sleep_bar.pack(pady=(0, 12), padx=20, fill="x")

        self.sleepHoursLabel = ctk.CTkLabel(sleepCard, text=f"{self.sleepHours} hrs last night", font=("Segoe UI", 14), text_color=cl.TEXT_SOFT)
        self.sleepHoursLabel.pack(pady=(0, 12))

        # ======= Spotify Card =======
        spotifyCard = ctk.CTkFrame(self.coverFrame, fg_color=cl.BG_CARD, corner_radius=20, border_width=2, border_color=cl.PURPLE_SOFT)
        spotifyCard.pack(pady=(0,20), padx=20, fill="both", expand=True)
        spotifyCard.pack_propagate(True)
        self.spotifyFrame = spotifyCard
        self.spotifyCreate()

        # ========= Sleep Comparison Card (UI Only) ========= #
        compareCard = ctk.CTkFrame(self.coverFrame, fg_color=cl.BG_CARD, corner_radius=20, border_width=2, border_color=cl.PURPLE_SOFT)
        compareCard.pack(pady=(0, 20), padx=20, fill="x")

        # Title
        ctk.CTkLabel(compareCard, text="Sleep Comparison", font=("Segoe UI", 17, "bold"), text_color="white").pack(pady=(12, 4))

        # Subtitle (use this for context like "Recommended: 7 hrs")
        compareLabel = ctk.CTkLabel(compareCard, text="Recommended: 7 hrs", font=("Segoe UI", 13), text_color=cl.TEXT_SOFT)
        compareLabel.pack(pady=(0, 8))

        # Comparison line placeholder (you will change this)
        self.comparison = ctk.CTkLabel(compareCard, text="➡️  Same as recommended", font=("Segoe UI", 14, "bold"), text_color="#3498DB")
        self.comparison.pack(pady=(4, 12))

        # ===== Emoji bottom =====
        self.bottomRightEmoji = ctk.CTkLabel(self.coverFrame, text="🌐", font=("Segoe UI Emoji", 30), text_color=cl.TEAL_NEON)
        self.bottomRightEmoji.pack(side="right", padx=(10,0))

        self.internetCheck()
        # Start hidden (send to back)
        #self.coverFrame.tkraise()
        self.window.rowconfigure(0, weight=0)  # menu row
        self.window.rowconfigure(1, weight=1)  # main content row

        self.window.columnconfigure(0, weight=0)  # left panel
        self.window.columnconfigure(1, weight=1)  # right content area

        contentFrame = ctk.CTkFrame(self.window, fg_color=cl.BG_CARD, corner_radius=0, border_width=2,
                                    border_color=cl.PURPLE_DEEP)
        contentFrame.grid(row=1, column=1, sticky="nsew", padx=25, pady=25)
        contentFrame.grid_propagate(False)
        contentFrame.grid_rowconfigure(0, weight=1)
        contentFrame.grid_columnconfigure(0, weight=1)

        # Title
        welcomeTitle = ctk.CTkLabel(contentFrame, text="WELCOME", font=("Segoe UI", 32, "bold"), text_color=cl.TEXT_WHITE )
        welcomeTitle.pack(pady=(45, 5))

        # Subtitle
        welcomeMessage = ctk.CTkLabel(contentFrame, text="Select an option above to get started.",
                                      font=("Segoe UI", 18), text_color=cl.TEXT_SOFT)
        welcomeMessage.pack(pady=(0, 20))

        # Divider line
        separator = ctk.CTkFrame(contentFrame, height=2, fg_color=cl.PURPLE_DEEP)
        separator.pack(fill="x", padx=60, pady=10)

        self.cc.backToMain()

        # Decorative glow shapes
        glowDot = ctk.CTkLabel(contentFrame, text="●", font=("Segoe UI", 50), text_color=cl.PURPLE_SOFT)
        glowDot.place(relx=0.1, rely=0.75)

        glowDot2 = ctk.CTkLabel(contentFrame, text="•••", font=("Segoe UI", 25),text_color=cl.PURPLE_DEEP)
        glowDot2.place(relx=0.83, rely=0.25)


        # ====================MenuFrame=====================#

        menuFrame = tk.Frame(self.window, bg=cl.BG_DARK, height=60)
        menuFrame.grid(row=0, column=1, columnspan=2, sticky="new")
        menuFrame.grid_columnconfigure(0, weight=1)
        menuFrame.grid_propagate(False)

        # inner container to center + evenly space the buttons
        menuInner = tk.Frame(menuFrame, bg=cl.BG_DARK)
        menuInner.pack(expand=True, fill="both")

        menuButtons = ["Question", "Graphs", "Data", "NetworkX", "Instructions"]
        commands = [self.questions, self.graphs, self.userData, self.network, self.cc.backToMain]

        for i, name in enumerate(menuButtons):
            btn = ctk.CTkButton(menuInner, text=name, font=("CHARLESWORTH", 18, "bold"), width=180,
                                height=45, corner_radius=12, fg_color=cl.PURPLE_SOFT, hover_color=cl.PURPLE_DEEP,
                                text_color="white", border_width=2, border_color=cl.PURPLE_DEEP, command=commands[i])
            btn.pack(side="left", expand=True, fill="x", padx=10, pady=10)

        menuFrame.tkraise()
        self.coverFrame.tkraise()

    # =================================================================
    # Function for creating the screen with the questions for the user
    # =================================================================
    def questions(self):
        self.clearScreen()
        self.window.rowconfigure(1, weight=1)
        self.window.columnconfigure(1, weight=1)

        # OUTER FRAME (full right side)
        questionMainFrame = ctk.CTkFrame(self.window, fg_color=cl.BG_DARK, corner_radius=0)
        questionMainFrame.grid(row=1, column=1, sticky="nsew")

        # TITLE
        title_label = ctk.CTkLabel(questionMainFrame, text="Sleep Input", font=("Segoe UI", 30, "bold"),
                                   text_color=cl.TRACK_FILL)
        title_label.pack(pady=(35, 10))

        # MAIN CONTAINER
        questions = ctk.CTkFrame(questionMainFrame, fg_color=cl.BG_CARD, corner_radius=20,
                                 border_width=2, border_color=cl.PURPLE_DEEP)
        questions.pack(pady=30, padx=40, fill="both", expand=True)
        questions.grid_propagate(False)

        # INSTRUCTIONS
        instructions = ctk.CTkLabel(questions, text="Before we begin, please answer the following questions.\nClick Start when you're ready.",
                                    font=("Segoe UI", 16), text_color=cl.TEXT_SOFT, justify="center")
        instructions.pack(pady=(30, 25))

        # START BUTTON
        start_button = ctk.CTkButton(questions, text="Start", font=("Segoe UI", 18, "bold"), fg_color=cl.PURPLE_DEEP,
                                     hover_color=cl.PINK_HOT, text_color="white", width=180, height=50,
                                     corner_radius=12, command=lambda: self.aq.allQuestions(self.window))
        start_button.pack(pady=(0, 30))

    # ================================================================
    # Function for creating the graphs
    # ================================================================
    def graphs(self):


        self.clearScreen()

        self.window.rowconfigure(1, weight=1)
        self.window.columnconfigure(1, weight=1)

        graphFrame = tk.Frame(self.window, bg=cl.BG_DARK)
        graphFrame.grid(row=1, column=1, sticky="nsew")

        graphTitle = tk.Label(graphFrame, text="Sleep Behavior", font=("Segoe UI", 20, "bold"), fg=cl.TRACK_FILL, bg=cl.BG_DARK)
        graphTitle.pack(pady=(25, 5))

        if "dates" in self.cc.users[self.cc.username]:

            # --- Create graph ---
            fig, ax = plt.subplots(figsize=(6, 4))

            dates = self.cc.users[self.cc.username]["dates"]
            fiveDates = dict(list(dates.items())[-5:])

            # Only 1 value for now (same logic)
            x_points = [date for date in fiveDates.keys()]
            y_points = [int(data['sleep']) for data in fiveDates.values()]

            # Draw a line graph (same data, just nicer style)
            ax.plot(x_points, y_points, marker="o", linewidth=2.5, markersize=8)

            # ===== STYLE SECTION (only visuals) =====

            # Backgrounds
            ax.set_facecolor("#0F1024")  # dark inner
            fig.patch.set_facecolor(cl.BG_DARK)  # match outer frame

            # Grid
            ax.grid(True, linestyle="--", alpha=0.3)

            # Title
            ax.set_title("", color="white", fontsize=16, pad=12)

            # Axis labels (optional but pretty)
            ax.set_xlabel("Dates", color=cl.TEXT_SOFT, fontsize=11)
            ax.set_ylabel("Sleep Hours", color=cl.TEXT_SOFT, fontsize=11)

            # Tick styling
            ax.tick_params(axis="x", colors=cl.TEXT_SOFT, labelsize=9)
            ax.tick_params(axis="y", colors=cl.TEXT_SOFT, labelsize=9)

            # Rotate x labels so they don't overlap
            plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

            # Spine colors
            for spine in ax.spines.values():
                spine.set_color(cl.PURPLE_SOFT)

            # Tight layout so everything fits nicely
            fig.tight_layout()

            # --- Embed in Tkinter (same logic) ---
            canvas = FigureCanvasTkAgg(fig, master=graphFrame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=(0,30))

        else:
            errorFrame = tk.Frame(graphFrame, bg="white")
            errorFrame.pack(expand=True, pady=40)

            errorLabel= tk.Label(errorFrame, text="⚠️ Graph Data not available.\n\nComplete your sleep test to see your graphs!",
                     font=("Segoe UI", 16, "bold"), fg="red", bg="white", justify="center" )
            errorLabel.pack()

    # ================================================================
    # Function for the selection of data
    # ================================================================
    def userData(self):

        self.clearScreen()

        userDataFrame = ctk.CTkFrame(self.window, fg_color=cl.BG_DARK, corner_radius=0)
        userDataFrame.grid(row=1, column=1, sticky="nsew")

        # Make the entire window expandable
        self.window.rowconfigure(1, weight=1)
        self.window.columnconfigure(1, weight=1)

        # UserDataFrame rows need weights
        userDataFrame.grid_rowconfigure(0, weight=0)  # title
        userDataFrame.grid_rowconfigure(1, weight=0)  # instructions
        userDataFrame.grid_rowconfigure(2, weight=0)  # date selector
        userDataFrame.grid_rowconfigure(3, weight=0)  # search button
        userDataFrame.grid_rowconfigure(4, weight=1)  # RESIZABLE container area

        userDataFrame.grid_columnconfigure(0, weight=1)

        # ------- MAIN TITLE -------
        titleLabel = ctk.CTkLabel(userDataFrame, text="USER DATA",
                                  text_color=cl.TEXT_WHITE,
                                  font=("Segoe UI", 36, "bold"))
        titleLabel.grid(row=0, column=0, pady=(10, 5))

        # ------- INSTRUCTIONS -------
        instrLabel = ctk.CTkLabel(userDataFrame, text="Scroll the wheels to choose a date.\nThen press the button to search for data.\n"
                                                      "Scrolling upwards will increase the number and scrolling downwards will decrease\n"
                                                      "the number.",
                                  text_color=cl.TEXT_SOFT, font=("Segoe UI", 16), justify="center")
        instrLabel.grid(row=1, column=0, pady=(0, 20))

        # ============================
        # DATE SELECTOR
        # ============================

        dateContainer = ctk.CTkFrame(userDataFrame, fg_color=cl.BG_DARK)
        dateContainer.grid(row=2, column=0, pady=10)

        titles = ["DAY", "MONTH", "YEAR"]
        scrollCommands = [self.dayScroll, self.monthScroll, self.yearScroll]

        for i, name in enumerate(titles):
            block = ctk.CTkFrame(dateContainer, fg_color=cl.BG_CARD, corner_radius=12, border_width=2,
                                 border_color=cl.PURPLE_SOFT, height=140, width=120)
            block.grid(row=0, column=i, padx=30)
            block.grid_propagate(False)

            title = ctk.CTkLabel(block, text=name, text_color=cl.TEXT_SOFT, font=("Segoe UI", 14, "bold"))
            title.pack(pady=(10, 5))

            # wheel labels
            if i == 0:
                self.dayWheel = ctk.CTkLabel(block, text="--", text_color=cl.TEXT_WHITE, font=("Segoe UI", 28, "bold"),
                                             height=50, width=60)
                self.dayWheel.pack(pady=(0, 10))
                self.dayWheel.bind("<MouseWheel>", scrollCommands[i])

            if i == 1:
                self.monthWheel = ctk.CTkLabel(block, text="--",
                                               text_color=cl.TEXT_WHITE,
                                               font=("Segoe UI", 28, "bold"), height=50, width=60)
                self.monthWheel.pack(pady=(0, 10))
                self.monthWheel.bind("<MouseWheel>", scrollCommands[i])

            if i == 2:
                self.yearWheel = ctk.CTkLabel(block, text="--",
                                              text_color=cl.TEXT_WHITE,
                                              font=("Segoe UI", 28, "bold"), height=50, width=60)
                self.yearWheel.pack(pady=(0, 10))
                self.yearWheel.bind("<MouseWheel>", scrollCommands[i])


        #====================SEARCH BUTTON========================#

        searchButton = ctk.CTkButton(userDataFrame, text="SEARCH DATE DATA", fg_color=cl.PINK_HOT, hover_color=cl.PURPLE_DEEP,
                                     text_color="white", font=("Segoe UI", 18, "bold"), command=self.connectDataButton,
                                     height=45, width=220)
        searchButton.grid(row=3, column=0, pady=(20, 10))

        self.errorMessage = ctk.CTkFrame(userDataFrame, fg_color="black", corner_radius=12,
                                         border_width=4, border_color="cyan")
        self.errorMessage.grid(row=4, column=0, padx=30, pady=15)

        #====================CONTAINER AREA=======================#

        contentsFrame = ctk.CTkFrame(userDataFrame, fg_color=cl.PURPLE_DEEP)
        contentsFrame.grid(row=4, column=0, sticky="nsew", padx=10, pady=15)
        contentsFrame.grid_columnconfigure(0, weight=1)

        # container expandable
        contentsFrame.grid_rowconfigure(0, weight=1)
        contentsFrame.grid_columnconfigure(0, weight=1)

        # ====================RESULT FRAMES========================#
        # ------- COVER DATA -------
        self.coverData = ctk.CTkFrame(contentsFrame, fg_color=cl.BG_DARK, corner_radius=12,
                                      border_width=4, border_color="cyan")
        self.coverData.grid(row=0, column=0, sticky="nsew", padx=30, pady=15)

        # This container will hold ALL result screens
        self.resultsContainer = ctk.CTkFrame(contentsFrame, fg_color="transparent")
        self.resultsContainer.grid(row=0, column=0, sticky="nsew",padx=30, pady=15)

        self.resultsContainer.grid_rowconfigure(0, weight=1)
        self.resultsContainer.grid_columnconfigure(0, weight=1)
        self.resultsContainer.grid_columnconfigure(1, weight=1)


        # ------- FIRST RESULT -------
        self.firstResultFrame = ctk.CTkScrollableFrame(self.resultsContainer, fg_color="white", corner_radius=12,
                                                       border_width=4, border_color="cyan")
        self.firstResultFrame.grid(row=0, column=0, sticky="nsew")

        self.firstResultLabel = ctk.CTkLabel(self.firstResultFrame, font=("Segoe UI", 12, "bold"),
                                             fg_color=cl.BG_DARK, text="", text_color="white",
                                             corner_radius=10)
        self.firstResultLabel.pack(fill="both", expand=True, padx=15, pady=15)

        # ------- SECOND RESULT -------
        self.secondResultFrame = ctk.CTkScrollableFrame(self.resultsContainer, fg_color="white", corner_radius=12,
                                                        border_width=4, border_color="cyan")
        self.secondResultFrame.grid(row=0, column=1, sticky="nsew")

        self.secondResultLabel = ctk.CTkLabel(self.secondResultFrame, font=("Segoe UI", 14, "bold"),
                                              fg_color=cl.BG_DARK, text="", text_color="white",
                                              corner_radius=10, wraplength= 350)
        self.secondResultLabel.pack(fill="both", expand=True, padx=15, pady=15)

        # Show cover first
        self.coverData.tkraise()

    # ================================================================
    # Function for displaying the networkX graphs
    # ================================================================
    def network(self):

        # Clear right side
        self.clearScreen()

        # ============================
        # MAIN SINGLE WRAPPER FRAME
        # ============================
        mainFrame = ctk.CTkFrame(self.window, fg_color=cl.BG_CARD, corner_radius=0, border_width=2,
                                 border_color=cl.PURPLE_DEEP)
        mainFrame.grid(row=1, column=1, sticky="nsew")

        # Make the grid expand
        mainFrame.grid_columnconfigure((0, 1), weight=1)
        mainFrame.grid_rowconfigure(1, weight=1)

        # ============================
        # TITLE (inside mainFrame)
        # ============================
        title = ctk.CTkLabel(mainFrame, text="SleepMind ML Networks", font=("Segoe UI", 28, "bold"),
                             text_color="white")
        title.grid(row=0, column=0, columnspan=2, pady=15)

        # ============================
        # LEFT GRAPH AREA
        # ============================
        leftFrame = ctk.CTkFrame(mainFrame, fg_color=cl.BG_DARK, corner_radius=10,
                                 border_width=2, border_color="cyan")
        leftFrame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        leftFrame.grid_columnconfigure(0, weight=1)
        leftFrame.grid_rowconfigure(1, weight=1)

        leftTitle = ctk.CTkLabel(leftFrame, text="Correlation Network", font=("Segoe UI", 20, "bold"),
                                 text_color="white")
        leftTitle.grid(row=0, column=0, pady=10)

        graphFrameLeft = ctk.CTkFrame(leftFrame, fg_color="transparent")
        graphFrameLeft.grid(row=1, column=0, sticky="nsew")
        graphFrameLeft.grid_rowconfigure(0, weight=1)
        graphFrameLeft.grid_columnconfigure(0, weight=1)

        # ============================
        # RIGHT GRAPH AREA
        # ============================
        rightFrame = ctk.CTkFrame(mainFrame, fg_color=cl.BG_DARK, corner_radius=10,
                                  border_width=2, border_color="cyan")
        rightFrame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        rightFrame.grid_columnconfigure(0, weight=1)
        rightFrame.grid_rowconfigure(1, weight=1)

        rightTitle = ctk.CTkLabel(rightFrame, text="Model Feature Importance",
                                  font=("Segoe UI", 20, "bold"), text_color="white")
        rightTitle.grid(row=0, column=0, pady=10)

        graphFrameRight = ctk.CTkFrame(rightFrame, fg_color="transparent")
        graphFrameRight.grid(row=1, column=0, sticky="nsew")
        graphFrameRight.grid_rowconfigure(0, weight=1)
        graphFrameRight.grid_columnconfigure(0, weight=1)

        # ============================
        # GENERATE GRAPHS
        # ============================
        fig1 = vg.grafo_correlaciones_radial(vg.df)
        fig2 = vg.grafo_importancia_radial(vg.model)

        # ============================
        # EMBED GRAPH 1 (FIXED)
        # ============================
        canvas1 = FigureCanvasTkAgg(fig1, master=graphFrameLeft)
        canvas1.draw()
        widget1 = canvas1.get_tk_widget()
        widget1.configure(bg=cl.BG_DARK, highlightthickness=0, borderwidth=0)
        widget1.pack(fill="both", expand=True)

        # ============================
        # EMBED GRAPH 2 (FIXED)
        # ============================
        canvas2 = FigureCanvasTkAgg(fig2, master=graphFrameRight)
        canvas2.draw()
        widget2 = canvas2.get_tk_widget()
        widget2.configure(bg=cl.BG_DARK, highlightthickness=0, borderwidth=0)
        widget2.pack(fill="both", expand=True)














