import tkinter as tk
from tkinter import simpledialog, messagebox
import webbrowser
from data_loader import load_artwork_data
from game import ArtQuizGame
from questions import (
    YearExactCheck,
    ArtistAuthorshipCheck,
    OldestArtworkCheck,
    FaceOrBodyPresenceCheck,
)

# Patch in the question classes for GUI logic
QUESTION_CLASSES = [
    YearExactCheck,
    ArtistAuthorshipCheck,
    OldestArtworkCheck,
    FaceOrBodyPresenceCheck,
]

class ArtQuizGUI:
    def __init__(self, root, game):
        self.root = root
        self.game = game
        self.max_consecutive_passes = 3

        # PLAYER NAME
        self.player_name = simpledialog.askstring("Welcome!", "Enter your name:") or "Player"
        self.root.title(f"Art Quiz for {self.player_name}")

        # --- HEADER COUNTERS ---
        counter_frame = tk.Frame(root)
        counter_frame.pack(pady=4)
        self.score_var = tk.StringVar(value=f"Score: {self.game.score}")
        self.lives_var = tk.StringVar(value=f"Lives: {self.game.lives}")
        self.passes_var = tk.StringVar(value=f"Passes: {self.game.consecutive_passes}")
        for var in (self.score_var, self.lives_var, self.passes_var):
            tk.Label(counter_frame, textvariable=var, font=("Arial", 12, "bold")).pack(side="left", padx=12)

        # --- QUESTION TEXT ---
        self.question_text = tk.Label(root, text="Welcome to the Art Quiz!", font=("Arial", 15), wraplength=430, justify="left")
        self.question_text.pack(pady=10)

        # --- BUTTONS ---
        # Yes/No
        self.frame_yesno = tk.Frame(root, bg="#cde0fa", padx=8, pady=3)
        self.frame_yesno.pack(pady=2)
        self.btn_yes = tk.Button(self.frame_yesno, text="Yes", width=9, font=("Arial", 11), command=lambda: self.on_answer("yes"))
        self.btn_no = tk.Button(self.frame_yesno, text="No", width=9, font=("Arial", 11), command=lambda: self.on_answer("no"))
        self.btn_yes.pack(side="left", padx=8)
        self.btn_no.pack(side="left", padx=8)

        # 1/2/Same
        self.frame_12same = tk.Frame(root, bg="#f8c4cb", padx=8, pady=3)
        self.frame_12same.pack(pady=2)
        self.btn_1 = tk.Button(self.frame_12same, text="1", width=8, font=("Arial", 11), command=lambda: self.on_answer("1"))
        self.btn_2 = tk.Button(self.frame_12same, text="2", width=8, font=("Arial", 11), command=lambda: self.on_answer("2"))
        self.btn_same = tk.Button(self.frame_12same, text="Same", width=8, font=("Arial", 11), command=lambda: self.on_answer("s"))
        self.btn_1.pack(side="left", padx=8)
        self.btn_2.pack(side="left", padx=8)
        self.btn_same.pack(side="left", padx=8)

        # Pass/Quit
        self.frame_passquit = tk.Frame(root, bg="#ffe28a", padx=8, pady=3)
        self.frame_passquit.pack(pady=2)
        self.btn_pass = tk.Button(self.frame_passquit, text="Pass", width=9, font=("Arial", 11), command=lambda: self.on_answer("pass"))
        self.btn_quit = tk.Button(self.frame_passquit, text="Quit", width=9, font=("Arial", 11), command=lambda: self.on_answer("quit"))
        self.btn_pass.pack(side="left", padx=8)
        self.btn_quit.pack(side="left", padx=8)

        # --- RESULT FEEDBACK ---
        self.result_label = tk.Label(root, text="", font=("Arial", 13, "bold"))
        self.result_label.pack(pady=6)
        self.extra_label = tk.Label(root, text="", font=("Arial", 11))
        self.extra_label.pack(pady=2)
        self.links_frame = tk.Frame(root)
        self.links_frame.pack()

        # --- NEXT & RESTART BUTTONS ---
        self.next_button = tk.Button(root, text="Next", width=12, font=("Arial", 11), command=self.next_question, state="disabled")
        self.next_button.pack(pady=8)
        self.restart_button = tk.Button(root, text="Start New Game", width=14, font=("Arial", 11, "bold"), command=self.restart_game)
        self.restart_button.pack_forget()

        # State vars
        self.awaiting_answer = False
        self.last_artwork = None

        # Start game
        self.next_question()

    def update_counters(self):
        self.score_var.set(f"Score: {self.game.score}")
        self.lives_var.set(f"Lives: {self.game.lives}")
        self.passes_var.set(f"Passes: {self.game.consecutive_passes}")

    def clear_links(self):
        for widget in self.links_frame.winfo_children():
            widget.destroy()

    def on_answer(self, answer):
        if not self.awaiting_answer:
            return

        # Handle "Pass" (enforce max 3 passes)
        if answer == "pass":
            if self.game.consecutive_passes >= self.max_consecutive_passes:
                self.result_label.config(
                    text=f"You've reached the maximum of {self.max_consecutive_passes} consecutive passes!\nPlease answer this question or quit.",
                    fg="orange"
                )
                self.btn_pass.config(state="disabled")
                self.next_button.config(state="disabled")
                # Make sure all answer and quit buttons are enabled
                self.btn_yes.config(state="normal")
                self.btn_no.config(state="normal")
                self.btn_1.config(state="normal")
                self.btn_2.config(state="normal")
                self.btn_same.config(state="normal")
                self.btn_quit.config(state="normal")
                self.awaiting_answer = True  # Still waiting for a valid answer
                return
            self.game.consecutive_passes += 1
            self.update_counters()
            self.result_label.config(text="You passed. No penalty. Click Next to read another question.", fg="black")
            self.awaiting_answer = False
            self.next_button.config(state="normal")
            self.btn_pass.config(state="normal" if self.game.consecutive_passes < self.max_consecutive_passes else "disabled")
            return

        # Handle "Quit"
        if answer == "quit":
            self.end_game("Game ended by player. Thanks for playing!")
            return

        # Attempt to process answer; check for invalid inputs
        result = self.game.current_question.ask_with_preset_answer(answer)
        if result is None:
            # Figure out allowed answers for this question
            q = self.game.current_question
            if isinstance(q, YearExactCheck) or isinstance(q, ArtistAuthorshipCheck) or isinstance(q, FaceOrBodyPresenceCheck):
                valid = "Yes or No"
            elif isinstance(q, OldestArtworkCheck):
                valid = "1, 2, or Same"
            else:
                valid = "a valid option"
            self.result_label.config(
                text=f"Invalid input! Please answer with {valid}.",
                fg="red"
            )
            # Re-enable only answer and quit buttons. Keep Pass and Next disabled.
            self.btn_yes.config(state="normal")
            self.btn_no.config(state="normal")
            self.btn_1.config(state="normal")
            self.btn_2.config(state="normal")
            self.btn_same.config(state="normal")
            self.btn_quit.config(state="normal")
            self.btn_pass.config(state="disabled")
            self.next_button.config(state="disabled")
            self.awaiting_answer = True  # Wait for valid answer again
            return

        # If input was valid, process normally
        self.awaiting_answer = False
        keep_playing, points, artwork, correct = self.game.check_answer_gui(answer)
        self.update_counters()
        self.clear_links()

        if not keep_playing or self.game.lives <= 0:
            self.end_game(f"Game over, {self.player_name}! You lost! Final Score: {self.game.score}")
            return

        # Process valid answer, reset passes
        self.game.consecutive_passes = 0
        self.passes_var.set("Passes: 0")
        self.btn_pass.config(state="normal")
        self.next_button.config(state="disabled")

        if correct is not None:
            if correct:
                self.result_label.config(text="Correct!", fg="green")
                if self.game.consecutive_correct % 10 == 0 and self.game.consecutive_correct > 0:
                    self.game.lives += 1
                    self.update_counters()
                    self.extra_label.config(
                        text="Congrats! You earned an extra life for 10 consecutive correct answers!", fg="blue"
                    )
                else:
                    self.extra_label.config(text="", fg="black")
            else:
                self.result_label.config(text="Wrong.", fg="#b71c1c")
                self.extra_label.config(text="", fg="black")

        # Show artwork/info links, if present
        if artwork:
            if isinstance(artwork, (list, tuple)):
                for idx, art in enumerate(artwork, 1):
                    self.add_links(art, idx)
            else:
                self.add_links(artwork, 1)

        # Allow Next to be clicked for proceeding
        self.next_button.config(state="normal")



    def next_question(self):
        self.result_label.config(text="", fg="black")
        self.extra_label.config(text="", fg="black")
        self.clear_links()
        self.awaiting_answer = True
        self.btn_pass.config(state="normal")
        # Get new question
        keep_playing, _, artwork, _ = self.game.play_round_gui()
        if not keep_playing or self.game.lives <= 0:
            self.end_game(f"Game over, {self.player_name}! You lost! Final Score: {self.game.score}")
            return
        self.show_question_text()
        self.update_counters()
        self.next_button.config(state="disabled")

    def show_question_text(self):
        question = self.game.current_question
        # Prepare dynamic question prompt using descriptors as in previous cell
        if isinstance(question, YearExactCheck):
            t = f"Is the artwork titled '{question.artwork['Title']}' by '{question.artwork['Artist']}' from the year {question.proposed_year}?"
        elif isinstance(question, ArtistAuthorshipCheck):
            t = f"Did the artist '{question.proposed_artist}' create the artwork titled '{question.artwork['Title']}'?"
        elif isinstance(question, OldestArtworkCheck):
            t = (
                f"1) '{question.art1['Title']}' by {question.art1['Artist']}\n"
                f"2) '{question.art2['Title']}' by {question.art2['Artist']}\n"
                "Which artwork is older or are they the same age?\n(1 = first older, 2 = second older, Same = same age)"
            )
        elif isinstance(question, FaceOrBodyPresenceCheck):
            t = f"Does the artwork '{question.artwork['Title']}' depict a human face or body?"
        else:
            t = "Please answer the question."
        self.question_text.config(text=t)

    def add_links(self, art, idx):
        title = art.get('Title', f'Artwork {idx}')
        tk.Label(self.links_frame, text=f"{idx}. {title}", font=("Arial", 10, "bold")).pack(anchor="w")
        for label, key in [
                ("Image URL", "Image URL"),
                ("Painting Info", "Painting Info URL"),
                ("Artist Info", "Artist Info URL"),
            ]:
            url = art.get(key, "")
            if url:
                link = tk.Label(self.links_frame, text=f"{label}", fg="blue", cursor="hand2", font=("Arial", 10, "underline"))
                link.pack(anchor="w")
                link.bind("<Button-1>", lambda e, url=url: webbrowser.open(url))

    def end_game(self, message):
        self.awaiting_answer = False
        self.question_text.config(text=message)
        self.result_label.config(text="")
        self.extra_label.config(text="")
        for btn in (self.btn_yes, self.btn_no, self.btn_1, self.btn_2, self.btn_same, self.btn_pass, self.btn_quit):
            btn.config(state="disabled")
        self.next_button.config(state="disabled")
        self.restart_button.pack(pady=12)

    def restart_game(self):
        self.game.__init__(self.game.data)
        self.update_counters()
        self.result_label.config(text="")
        self.extra_label.config(text="")
        self.restart_button.pack_forget()
        self.awaiting_answer = True
        # RE-ENABLE ALL interactive buttons
        for btn in (self.btn_yes, self.btn_no, self.btn_1, self.btn_2, self.btn_same, self.btn_pass, self.btn_quit):
            btn.config(state="normal")
        self.next_button.config(state="disabled")
        self.game.consecutive_passes = 0
        self.passes_var.set("Passes: 0")
        self.next_question()


# ------------- ArtQuizGame GUI EXTENSIONS ---------------

def play_round_gui(self):
    # Prepare a question and store it for the GUI's turn
    for _ in range(20):
        question_class = self.QUESTION_CLASSES[self.round_number % len(self.QUESTION_CLASSES)]
        question = question_class(self.data)
        if question.prepare_question():
            self.current_question = question
            self.round_number += 1
            return True, 0, getattr(question, 'artwork', None), None
    return False, 0, None, None

def check_answer_gui(self, user_input):
    # Process user answer for this question (should always be called once per question)
    question = self.current_question
    # reset consecutive_passes if not a pass
    if user_input in {'p', 'pass'}:
        return True, 0, getattr(question, 'artwork', None), None
    if user_input in {'q', 'quit'}:
        self.lives = 0
        return False, 0, None, None
    result = question.ask_with_preset_answer(user_input)
    if result is None:
        return True, 0, getattr(question, 'artwork', None), None
    is_correct, points, artwork = result
    if is_correct:
        self.score += points
        self.consecutive_correct += 1
    else:
        self.lives -= 1
        self.consecutive_correct = 0
    return True, points if is_correct else 0, artwork, is_correct

# Attach new methods and set QUESTION_CLASSES attribute
ArtQuizGame.QUESTION_CLASSES = QUESTION_CLASSES
ArtQuizGame.play_round_gui = play_round_gui
ArtQuizGame.check_answer_gui = check_answer_gui

# ------------- RUN -----------------
if __name__ == "__main__":
    import sys
    from pathlib import Path

    quiz_path = Path("clean_quiz_core_metadata.tsv")
    urls_path = Path("WikiArt-info.tsv")
    try:
        data = load_artwork_data(quiz_path, urls_path)
    except Exception as e:
        messagebox.showerror("File Error", str(e))
        sys.exit()

    game = ArtQuizGame(data)
    root = tk.Tk()
    gui = ArtQuizGUI(root, game)
    root.mainloop()
