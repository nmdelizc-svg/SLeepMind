import json #For using json files
import os #For the json files
import webbrowser #Open links
import customtkinter as ctk #GUI library
import colors as cl #Colors file
from datetime import datetime as dt #Obtain actual date

# ==========================================================
# Class in charge of the data management
# ==========================================================
class DataManager:
    _instance = None
    _initialized = False

    # ==========================================================
    # Make sure the class can only have on object created
    # ==========================================================
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, filename="app_data.json"):
        if DataManager._initialized:
            return

        DataManager._initialized = True
        self.results = None
        self.window = None
        self.filename = filename
        self.date = dt.now().strftime("%Y-%m-%d")
        self.username = ""

        # self.tracks = None
        self.internetStatus = None

        self.users = {}

        # Create file if needed
        if not os.path.isfile(self.filename):
            with open(self.filename, "w") as f:
                json.dump({}, f, indent=4)

        self._load()

    # ==========================================================
    # Set the default values for the json file
    # ==========================================================
    def default(self):
        for username, user in self.users.items():

            # Ensure "dates" exists
            if "dates" not in user:
                user["dates"] = {}

            # Fix each date entry
            for date, entry in user["dates"].items():
                entry.setdefault("sleepHours", "1")
                entry.setdefault("sleepMinutes", "1")
                entry.setdefault("sleepPeriod", "AM")

                entry.setdefault("wakeHours", "1")
                entry.setdefault("wakeMinutes", "1")
                entry.setdefault("wakePeriod", "AM")

                entry.setdefault("sleep", "")

                entry.setdefault("exerciseLevel", "1")
                entry.setdefault("stressLevel", "1")
                entry.setdefault("caffeineLevel", "1")
                entry.setdefault("screenTime", "1")

                entry.setdefault("spotifyPlaylist", "")

    # ==================================================================
    # Function for going back to the main screen, aka, the instructions
    # ==================================================================
    def backToMain(self):
        contentFrame = ctk.CTkFrame(self.window, fg_color=cl.BG_CARD, corner_radius=0, border_width=2,
                                    border_color=cl.PURPLE_DEEP)
        contentFrame.grid(row=1, column=1, sticky="nsew")
        contentFrame.grid_propagate(False)

        # Title
        welcomeTitle = ctk.CTkLabel(contentFrame, text="WELCOME", font=("Segoe UI", 32, "bold"),
                                    text_color=cl.TEXT_WHITE)
        welcomeTitle.pack(pady=(45, 5))

        # Subtitle
        welcomeMessage = ctk.CTkLabel(contentFrame, text="Select an option above to get started.",
                                      font=("Segoe UI", 18), text_color=cl.TEXT_SOFT)
        welcomeMessage.pack(pady=(0, 20))

        # Divider line
        separator = ctk.CTkFrame(contentFrame, height=2, fg_color=cl.PURPLE_DEEP)
        separator.pack(fill="x", padx=60, pady=10)

        instructionsFrame = ctk.CTkFrame(contentFrame, fg_color="transparent")
        instructionsFrame.pack(fill="both", expand=True, padx=60, pady=10)

        centerMessage = ctk.CTkLabel(
            instructionsFrame,
            text=(
                "•  Question - Opens a questionnaire where you enter your sleep habits.\n"
                "   Your answers are analyzed to generate your sleep duration, efficiency,\n"
                "   Spotify playlist suggestions, and personalized recommendations.\n\n"
                "•  Graphs - Show the sleep amount across the last five days of information\n\n"
                "•  Data - You will be able to enter a date, so you can check and see the information\n"
                "   of that specific day, as well as any other!\n\n"
                "•  NetworkX - Show the graphs about the correlations in our machine learning program\n\n"
                "•  Instructions - It is where we are right now! Press it any time if you forget what are\n"
                "   purposes of the other buttons!"),
            font=("Segoe UI", 18),
            text_color="white",
            justify="left",
            wraplength=700
        )

        centerMessage.pack(anchor="center", pady=10)

        # Decorative glow shapes
        glowDot = ctk.CTkLabel(contentFrame, text="●", font=("Segoe UI", 50), text_color=cl.PURPLE_SOFT)
        glowDot.place(relx=0.1, rely=0.75)

        glowDot2 = ctk.CTkLabel(contentFrame, text="•••", font=("Segoe UI", 25), text_color=cl.PURPLE_DEEP)
        glowDot2.place(relx=0.83, rely=0.25)

    # ==========================================================
    # Function for clearing the screen
    # ==========================================================
    def clearScreen(self):
        # Destroy everything inside row=1 column=1
        for widget in self.window.grid_slaves(row=1, column=1):
            widget.destroy()

    # ==========================================================
    # Function for loading the information from the json file
    # ==========================================================
    def _load(self):
        with open(self.filename, "r") as f:
            self.users = json.load(f)
            self.default()

    # ==========================================================
    # Function for saving the information to the json file
    # ==========================================================
    def saveDaily(self, results, window):
        self.results = results
        self.window = window
        if not "dates" in self.users[self.username]:
            self.users[self.username]["dates"] = {}

        with open(self.filename, "w") as f:
            self.users[self.username]["dates"][self.date] = {}

            self.users[self.username]["dates"][self.date].update(self.results)
            json.dump(self.users, f, indent=4)

            self.clearScreen()
            self.createResultsScreen()

    # ==========================================================
    # Save the user to the json file
    # ==========================================================
    def saveUser(self):
        with open(self.filename, "w") as f:
            json.dump(self.users, f, indent=4)

    # ==========================================================
    # Create the result screen for the information
    # ==========================================================
    def createResultsScreen(self):

        def displayFirstPlay(event):
            webbrowser.open(self.results["spotifyPlayListOne"])
        def displaySecondPlay(event):
            webbrowser.open(self.results["spotifyPlayListTwo"])
        def displayThirdPlay(event):
            webbrowser.open(self.results["spotifyPlayListThree"])

        # Clear previous screen
        self.clearScreen()

        # OUTER FRAME (fills the right side)
        outer = ctk.CTkScrollableFrame(master=self.window, fg_color=cl.BG_DARK, corner_radius=0)
        outer.grid(row=1, column=1, sticky="nsew")

        # TITLE
        title = ctk.CTkLabel(outer, text="Your Results", font=("Segoe UI", 28, "bold"), text_color=cl.TRACK_FILL)
        title.pack(pady=(25, 10))

        # CARD FRAME with rounded corners
        card = ctk.CTkFrame(outer, fg_color=cl.BG_CARD, corner_radius=20, border_width=2, border_color=cl.PURPLE_DEEP)
        card.pack(pady=20, padx=40, fill="both", expand=True)

        # SUBTITLE
        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)
        card.grid_columnconfigure(2, weight=1)

        subtitle = ctk.CTkLabel(card, text="Sleep Quality Summary", font=("Segoe UI", 20, "bold"),
                                text_color="white")
        subtitle.grid(column= 0, row= 0, columnspan= 3, pady=(20, 10))

        resultingInfo = ctk.CTkFrame(card, fg_color=cl.PURPLE_DEEP, corner_radius=10, border_width=2, border_color="cyan")
        resultingInfo.grid(column = 0, row=1, pady=(20, 10), padx= (10,0), columnspan= 2, sticky="w")
        resultingInfo.grid_columnconfigure(0, weight=1)


        smallTitle = ctk.CTkLabel(resultingInfo, text="Generated Results", font=("Segoe UI", 18, "bold", "underline"),
                                  wraplength=150)
        smallTitle.pack(pady=(20, 10))

        sleepy = ctk.CTkLabel(resultingInfo, text=f"- Amount of Sleep: {self.results["sleep"]} hours", font=("Segoe UI", 16, "bold"))
        sleepy.pack(anchor="w", pady=(20, 10), padx=(10, 15))

        efficiencySleep = ctk.CTkLabel(resultingInfo, text=f"- Sleep Efficiency: {self.results["sleepEfficiency"]}",
                                       font=("Segoe UI", 16, "bold"))
        efficiencySleep.pack(anchor="w", pady=(20, 10), padx=(10, 15))

        spotyList = ctk.CTkLabel(resultingInfo, text=f"- Spotify Playlists:", font=("Segoe UI", 16, "bold"))
        spotyList.pack(anchor="w", pady=(20, 0), padx=(10, 15))

        spotyFirst = ctk.CTkLabel(resultingInfo, text_color= "cyan", text=f"> {self.results["spotifyFirstName"]}:",
                                  font=("Segoe UI", 14, "bold"), wraplength=400)
        spotyFirst.pack(anchor="w", padx=(20, 15))

        spotyViewFirst = ctk.CTkLabel(resultingInfo, text_color="gray", text=f"     * View Full playlist",
                                      font=("Segoe UI", 12, "bold"), cursor= "hand2")
        spotyViewFirst.pack(anchor="w", pady=(0, 2), padx=(20, 15))
        spotyViewFirst.bind("<Button-1>", displayFirstPlay)
        spotyViewFirst.bind("<Enter>", lambda e: spotyViewFirst.configure(text_color="cyan", font=("Segoe UI", 12, "underline")))
        spotyViewFirst.bind("<Leave>", lambda e: spotyViewFirst.configure(text_color="grey", font=("Segoe UI", 12, "bold")))

        spotySecond = ctk.CTkLabel(resultingInfo, text_color="cyan", text=f"> {self.results["spotifySecondName"]}:",
                                  font=("Segoe UI", 14, "bold"))
        spotySecond.pack(anchor="w", padx=(20, 15))

        spotyViewSecond = ctk.CTkLabel(resultingInfo, text_color="gray", text=f"     * View Full playlist",
                                       font=("Segoe UI", 12, "bold"), cursor= "hand2")
        spotyViewSecond.pack(anchor="w", pady=(0, 2), padx=(20, 15))
        spotyViewSecond.bind("<Button-1>", displaySecondPlay)
        spotyViewSecond.bind("<Enter>", lambda e: spotyViewSecond.configure(text_color="cyan", font=("Segoe UI", 12, "underline")))
        spotyViewSecond.bind("<Leave>", lambda e: spotyViewSecond.configure(text_color="grey", font=("Segoe UI", 12, "bold")))

        spotyThird = ctk.CTkLabel(resultingInfo, text_color="cyan", text=f"> {self.results["spotifyThirdName"]}:",
                                   font=("Segoe UI", 14, "bold"))
        spotyThird.pack(anchor="w", padx=(20, 15))

        spotyViewThird = ctk.CTkLabel(resultingInfo, text_color="gray", text=f"     * View Full playlist",
                                       font=("Segoe UI", 12, "bold"), cursor="hand2")
        spotyViewThird.pack(anchor="w", pady=(0, 2), padx=(20, 15))
        spotyViewThird.bind("<Button-1>", displayThirdPlay)
        spotyViewThird.bind("<Enter>", lambda e: spotyViewThird.configure(text_color="cyan", font=("Segoe UI", 12, "underline")))
        spotyViewThird.bind("<Leave>", lambda e: spotyViewThird.configure(text_color="grey", font=("Segoe UI", 12, "bold")))

        analysisInfo = ctk.CTkFrame(card, fg_color=cl.PURPLE_DEEP, corner_radius=10,
                                    border_width=2, border_color="cyan")
        analysisInfo.grid(column=2, row=1, padx=(20, 20), pady=(20, 10), sticky="n")
        analysisInfo.grid_propagate(False)  # allow fixed size

        # You can customize the size here
        analysisInfo.configure(width=380, height=450)

        infoTitle = ctk.CTkLabel(analysisInfo, text="Why Good Sleep Matters", font=("Segoe UI", 18, "bold", "underline"),
                                 text_color="white")
        infoTitle.pack(pady=(20, 10))

        sleepParagraph = ctk.CTkLabel(analysisInfo, text=self.results["recommendation"],
                                      font=("Segoe UI", 16), text_color="white", wraplength=500, justify="left")
        sleepParagraph.pack(padx=30, pady=10)

        # BUTTON TO GO BACK TO MENU
        backBtn = ctk.CTkButton(outer, text="Back to Menu", fg_color=cl.PURPLE_SOFT, hover_color=cl.PURPLE_DEEP,
                                text_color="white", corner_radius=12, width=200, height=45, command= self.backToMain)
        backBtn.pack(pady=(10, 30))