# Import required libraries

import tkinter as tk # tkinter - for creating the GUI
from tkinter import ttk, messagebox, filedialog, simpledialog # Create GUI components
import datetime # datetime - for handling dates and times
import json # json - for storing data in JSON format
import os # os - for file operations
from threading import Thread # Thread - for running background tasks
import time # time - for time-related functions
import csv # csv - for exporting data to CSV files
from collections import defaultdict # defaultdict - for creating dictionaries with default values

class TimeClockGUI: # Main application class
    def __init__(self, root):
        # Initialize the main window
        self.root = root
        self.root.title("Time Clock Application - Enhanced")
        self.root.geometry("600x700")  # Default size that shows all content
        self.root.resizable(True, True)  # Allow window resizing
        self.root.minsize(400, 500)  # Smaller minimum size to allow more flexible resizing

        # Define paths for data storage files
        self.data_file = 'timeclock_data.json'        # Stores current session data
        self.history_file = 'timeclock_history.json'  # Stores all time entries
        self.users_file = 'timeclock_users.json'      # Stores user information

        # Initialize application state variables
        self.current_user = None              # Currently active user can set default user here
        self.current_status = None            # Current clock status (in/out)
        self.clock_in_time = None            # Time when user clocked in
        self.clock_in_note = None            # Note added during clock in
        self.total_time_today = datetime.timedelta()  # Total time for today
        self.history = []                    # List of all time entries
        self.users = {}                      # Dictionary of all users

        # Load existing data from files
        self.load_users()      # Load user information
        self.load_history()    # Load time entry history

        # Set up the visual appearance
        self.setup_styles()

        # Start the application
        # If no users exist, create first user
        # Otherwise, show user selection screen
        if not self.users:
            self.create_first_user()
        else:
            self.show_user_selection()

    def setup_styles(self):
        """Configure custom styles for the application"""
        # Create a style manager for custom widget appearance
        style = ttk.Style()
        # Print available themes
        print("Available themes:", style.theme_names())
        style.theme_use('clam')  # Use the 'clam' theme for modern look
        
        
        # Set the background color for the main window
        bg_color = "#f0f0f0"  # Light gray background
        self.root.configure(bg=bg_color)

        # Configure the Clock In button style
        # Green background with white text and bold font
        style.configure("ClockIn.TButton", 
                       background="#27ae60",
                       foreground="white",
                       font=("Arial", 12, "bold"),
                       padding=15)

        style.configure("ClockOut.TButton",
                       background="#e74c3c",
                       foreground="white",
                       font=("Arial", 12, "bold"),
                       padding=15)

        style.configure("Action.TButton",
                       background="#3498db",
                       foreground="white",
                       font=("Arial", 10),
                       padding=10)

        style.configure("Reset.TButton",
                       background="#95a5a6",
                       foreground="white",
                       font=("Arial", 10),
                       padding=10)

        style.map("ClockIn.TButton", background=[("active", "#229954")])
        style.map("ClockOut.TButton", background=[("active", "#c0392b")])
        style.map("Action.TButton", background=[("active", "#2980b9")])
        style.map("Reset.TButton", background=[("active", "#7f8c8d")])

    def create_first_user(self):
        """Create the first user when the application is run for the first time"""
        # Show dialog to get username
        username = simpledialog.askstring("Create User", "Enter your name:")
        
        if username:
            # Create new user record with timestamp
            self.users[username] = {
                'created': datetime.datetime.now().isoformat(),
                'total_hours': 0
            }
            self.save_users()              # Save to file
            self.current_user = username   # Set as current user
            self.load_user_data()          # Load any existing data
            self.create_widgets()          # Create main interface
        else:
            # Exit if no username provided
            self.show_message("Error", "Username is required!", "error")
            self.root.destroy()

    def show_user_selection(self):
        """Show user selection dialog"""
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select User")
        selection_window.geometry("400x300")
        selection_window.transient(self.root)
        selection_window.grab_set()
        
        # Center the window relative to the main window
        def center_window():
            # Wait for the window to be ready
            selection_window.update()
            
            # Get main window position and dimensions
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()
            main_width = self.root.winfo_width()
            main_height = self.root.winfo_height()
            
            # Calculate center position
            window_width = selection_window.winfo_width()
            window_height = selection_window.winfo_height()
            position_x = main_x + (main_width - window_width) // 2
            position_y = main_y + (main_height - window_height) // 2
            
            # Set the position
            selection_window.geometry(f"+{position_x}+{position_y}")
            
        # Call after a short delay to ensure window is fully created
        selection_window.after(10, center_window)

        tk.Label(selection_window, text="Select User", 
                font=("Arial", 16, "bold")).pack(pady=20)

        listbox = tk.Listbox(selection_window, font=("Arial", 12), height=8)
        listbox.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        for username in self.users.keys():
            listbox.insert(tk.END, username)

        def select_user():
            selection = listbox.curselection()
            if selection:
                self.current_user = listbox.get(selection[0])
                self.load_user_data()
                selection_window.destroy()
                self.create_widgets()
            else:
                self.show_message("Warning", "Please select a user!", "warning")

        def new_user():
            username = simpledialog.askstring("New User", "Enter new username:")
            if username:
                if username in self.users:
                    self.show_message("Error", "User already exists!", "error")
                else:
                    self.users[username] = {
                        'created': datetime.datetime.now().isoformat(),
                        'total_hours': 0
                    }
                    self.save_users()
                    listbox.insert(tk.END, username)

        btn_frame = tk.Frame(selection_window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Select", command=select_user,
                 bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="New User", command=new_user,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)

    def load_users(self):
        """Load users from file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            except Exception:
                self.users = {}

    def save_users(self):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)

    def load_user_data(self):
        """Load current user's data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    user_data = data.get(self.current_user, {})

                    if user_data.get('status') == 'clocked_in':
                        self.current_status = 'clocked_in'
                        self.clock_in_time = datetime.datetime.fromisoformat(
                            user_data['clock_in_time'])
                        self.clock_in_note = user_data.get('clock_in_note')
                    else:
                        self.current_status = 'clocked_out'
                        self.clock_in_note = None

                    if 'total_time_seconds' in user_data:
                        self.total_time_today = datetime.timedelta(
                            seconds=user_data['total_time_seconds'])
            except Exception:
                self.current_status = 'clocked_out'
        else:
            self.current_status = 'clocked_out'

    def save_user_data(self):
        """Save current user's data"""
        all_data = {}
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    all_data = json.load(f)
            except Exception:
                pass

        user_data = {
            'status': self.current_status,
            'total_time_seconds': self.total_time_today.total_seconds()
        }
        if self.current_status == 'clocked_in':
            user_data['clock_in_time'] = self.clock_in_time.isoformat()
            if self.clock_in_note:
                user_data['clock_in_note'] = self.clock_in_note

        all_data[self.current_user] = user_data

        with open(self.data_file, 'w') as f:
            json.dump(all_data, f, indent=2)

    def load_history(self):
        """Load history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    all_history = json.load(f)
                    self.history = all_history.get(self.current_user, []) if self.current_user else []
            except Exception:
                self.history = []
        else:
            self.history = []

    def save_history(self):
        """Save history to file"""
        all_history = {}
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    all_history = json.load(f)
            except Exception:
                pass

        all_history[self.current_user] = self.history

        with open(self.history_file, 'w') as f:
            json.dump(all_history, f, indent=2)

    def add_history_entry(self, clock_in, clock_out, duration, note=""):
        """Add entry to history with optional note"""
        # Enforce 20 word limit on notes
        if note:
            words = note.split()
            if len(words) > 20:
                note = " ".join(words[:20])
            
        entry = {
            'clock_in': clock_in.isoformat(),
            'clock_out': clock_out.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'date': clock_in.strftime('%Y-%m-%d'),
            'note': note,
            'id': len(self.history)
        }
        self.history.append(entry)
        self.save_history()
        
    def edit_note(self, event, tree):
        """Handle note editing in history view"""
        if not tree.selection():
            return
            
        item = tree.selection()[0]
        col = tree.identify_column(event.x)
        col_name = tree.column(col)['id']
        
        # Only allow editing the Notes column
        if col_name != 'Notes':
            return
            
        # Get the current values
        values = tree.item(item)['values']
        date = values[0]
        clock_in_time = values[1]
        
        # Find the corresponding history entry
        for entry in self.history:
            entry_date = datetime.datetime.fromisoformat(entry['clock_in']).strftime('%Y-%m-%d')
            entry_time = datetime.datetime.fromisoformat(entry['clock_in']).strftime('%I:%M:%S %p')
            
            if entry_date == date and entry_time == clock_in_time:
                # Create edit dialog
                dialog = tk.Toplevel(self.root)
                dialog.title("Edit Note")
                dialog.geometry("400x300")
                dialog.transient(self.root)
                dialog.grab_set()
                
                tk.Label(dialog, text="Edit Note", font=("Arial", 14, "bold")).pack(pady=10)
                
                note_text = tk.Text(dialog, height=5, width=40, font=("Arial", 12),
                                  wrap=tk.WORD)
                note_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
                note_text.insert("1.0", entry.get('note', ''))
                
                char_count = tk.Label(dialog, text=f"{len(entry.get('note', ''))}/500 characters",
                                    font=("Arial", 10))
                char_count.pack(pady=5)
                
                def update_count(e=None):
                    count = len(note_text.get("1.0", "end-1c"))
                    char_count.config(text=f"{count}/500 characters")
                    if count >= 500 and e and e.keysym not in ('BackSpace', 'Delete'):
                        return "break"
                        
                note_text.bind("<KeyPress>", update_count)
                note_text.bind("<KeyRelease>", update_count)
                
                def save_note():
                    new_note = note_text.get("1.0", "end-1c").strip()
                    entry['note'] = new_note
                    self.save_history()
                    tree.set(item, 'Notes', new_note)
                    dialog.destroy()
                    
                tk.Button(dialog, text="Save", command=save_note,
                         bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                         padx=20, pady=5).pack(pady=10)
                break

    def create_widgets(self):
        """Create all GUI widgets"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, 
                              text=f"⏰ TIME CLOCK - {self.current_user}",
                              font=("Arial", 20, "bold"),
                              bg="#2c3e50",
                              fg="white")
        title_label.pack(pady=20)

        # Main content frame with scrollbar
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

        def on_frame_configure(event=None):
            # Update the scroll region when the frame changes size
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Ensure frame fills vertical space
            if scrollable_frame.winfo_reqheight() < canvas.winfo_height():
                scrollable_frame.configure(height=canvas.winfo_height())

        scrollable_frame.bind("<Configure>", on_frame_configure)

        # Create window inside canvas that fills the space
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=main_frame.winfo_width()-40)
        
        # Make the content resize with the window
        def configure_frame(event):
            # Get the current window width
            window_width = main_frame.winfo_width()
            # Set the canvas width to fill the window
            canvas_width = window_width - 40  # 40 for padding and scrollbar
            canvas.configure(width=canvas_width)
            canvas.itemconfig(canvas_frame, width=canvas_width)
            # Update scroll region after window resize
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        main_frame.bind('<Configure>', configure_frame)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind mouse wheel to the canvas
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind the mousewheel to the canvas and all its children
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        for child in scrollable_frame.winfo_children():
            child.bind("<MouseWheel>", _on_mousewheel)

        # Pack scrollbar first so it's always visible
        scrollbar.pack(side="right", fill="y", pady=20)
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 5), pady=20)
        
        # Update scroll region after initial packing
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        content_frame = scrollable_frame

        # Current time display
        time_frame = tk.LabelFrame(content_frame,
                                  text="Current Time",
                                  font=("Arial", 10, "bold"),
                                  bg="#f0f0f0",
                                  fg="#2c3e50",
                                  padx=10,
                                  pady=10)
        time_frame.pack(fill=tk.X, pady=(0, 15))

        self.current_time_label = tk.Label(time_frame,
                                          text="",
                                          font=("Arial", 14),
                                          bg="#f0f0f0",
                                          fg="#2c3e50")
        self.current_time_label.pack()

        # Status display
        status_frame = tk.LabelFrame(content_frame,
                                    text="Status",
                                    font=("Arial", 10, "bold"),
                                    bg="#f0f0f0",
                                    fg="#2c3e50",
                                    padx=10,
                                    pady=10)
        status_frame.pack(fill=tk.X, pady=(0, 15))

        self.status_label = tk.Label(status_frame,
                                    text="",
                                    font=("Arial", 14, "bold"),
                                    bg="#f0f0f0")
        self.status_label.pack()

        # Time information display
        info_frame = tk.LabelFrame(content_frame,
                                  text="Time Information",
                                  font=("Arial", 10, "bold"),
                                  bg="#f0f0f0",
                                  fg="#2c3e50",
                                  padx=10,
                                  pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Add Notes section
        notes_frame = tk.LabelFrame(content_frame,
                                  text="Notes",
                                  font=("Arial", 10, "bold"),
                                  bg="#f0f0f0",
                                  fg="#2c3e50",
                                  padx=10,
                                  pady=10)
        notes_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.notes_entry = tk.Text(notes_frame,
                                 height=5,
                                 width=40,
                                 font=("Arial", 12),
                                 bg="white",
                                 fg="gray",  # Set initial color to gray for placeholder
                                 wrap=tk.WORD)
        self.notes_entry.pack(fill=tk.X, pady=5)
        
        # Add default text
        self.notes_entry.insert("1.0", "Write note here before clock in")
        
        # Add word counter
        self.word_count_label = tk.Label(notes_frame,
                                       text="0/20 words",
                                       font=("Arial", 10),
                                       bg="#f0f0f0",
                                       fg="#666666")
        self.word_count_label.pack(anchor=tk.E, pady=(0, 5))
        
        # Handle placeholder text focus events
        def on_focus_in(event):
            text = self.notes_entry.get("1.0", "end-1c").strip()
            if text == "Write note here before clock in":
                self.notes_entry.delete("1.0", tk.END)
                self.notes_entry.config(fg="#34495e")
                self.word_count_label.config(text="0/20 words")
        
        def on_focus_out(event):
            text = self.notes_entry.get("1.0", "end-1c").strip()
            if not text:
                self.notes_entry.delete("1.0", tk.END)
                self.notes_entry.insert("1.0", "Write note here before clock in")
                self.notes_entry.config(fg="gray")
                self.word_count_label.config(text="0/20 words")
        
        self.notes_entry.bind("<FocusIn>", on_focus_in)
        self.notes_entry.bind("<FocusOut>", on_focus_out)
        
        # Bind word counting
        self.notes_entry.bind("<KeyPress>", self.update_word_count)
        self.notes_entry.bind("<KeyRelease>", self.update_word_count)

        self.clock_in_label = tk.Label(info_frame,
                                      text="",
                                      font=("Arial", 11),
                                      bg="#f0f0f0",
                                      fg="#34495e",
                                      justify=tk.LEFT)
        self.clock_in_label.pack(anchor=tk.W, pady=2)

        self.session_label = tk.Label(info_frame,
                                     text="",
                                     font=("Arial", 11),
                                     bg="#f0f0f0",
                                     fg="#34495e",
                                     justify=tk.LEFT)
        self.session_label.pack(anchor=tk.W, pady=2)

        self.total_label = tk.Label(info_frame,
                                   text="",
                                   font=("Arial", 11, "bold"),
                                   bg="#f0f0f0",
                                   fg="#2c3e50",
                                   justify=tk.LEFT)
        self.total_label.pack(anchor=tk.W, pady=2)

        # Clock In/Out buttons
        button_frame = tk.Frame(content_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=(0, 10))

        self.clock_in_btn = ttk.Button(button_frame,
                                      text="CLOCK IN",
                                      style="ClockIn.TButton",
                                      command=self.clock_in)
        self.clock_in_btn.pack(fill=tk.X, pady=5)

        self.clock_out_btn = ttk.Button(button_frame,
                                       text="CLOCK OUT",
                                       style="ClockOut.TButton",
                                       command=self.clock_out)
        self.clock_out_btn.pack(fill=tk.X, pady=5)

        # Action buttons
        action_frame = tk.Frame(content_frame, bg="#f0f0f0")
        action_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(action_frame,
                  text="Add Missed Entry",
                  style="Action.TButton",
                  command=self.add_missed_entry).pack(fill=tk.X, pady=2)

        ttk.Button(action_frame,
                  text="View History",
                  style="Action.TButton",
                  command=self.show_history).pack(fill=tk.X, pady=2)

        ttk.Button(action_frame,
                  text="Weekly Summary",
                  style="Action.TButton",
                  command=self.show_weekly_summary).pack(fill=tk.X, pady=2)

        ttk.Button(action_frame,
                  text="Monthly Summary",
                  style="Action.TButton",
                  command=self.show_monthly_summary).pack(fill=tk.X, pady=2)

        ttk.Button(action_frame,
                  text="Export to CSV",
                  style="Action.TButton",
                  command=self.export_to_csv).pack(fill=tk.X, pady=2)

        ttk.Button(action_frame,
                  text="Switch User",
                  style="Action.TButton",
                  command=self.switch_user).pack(fill=tk.X, pady=2)

        # Reset button
        reset_frame = tk.Frame(content_frame, bg="#f0f0f0")
        reset_frame.pack(fill=tk.X)

        ttk.Button(reset_frame,
                  text="Reset Daily Time",
                  style="Reset.TButton",
                  command=self.reset_day).pack(fill=tk.X)

        # Start time update thread
        self.running = True
        self.update_thread = Thread(target=self.update_time_display, daemon=True)
        self.update_thread.start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initial update
        self.update_display()

    def clock_in(self):
        """Record when user starts working"""
        # Prevent double clock-in
        if self.current_status == 'clocked_in':
            self.show_message("Already Clocked In", 
                          "You are already clocked in!", "warning")
            return

        # Get the clock in note
        clock_in_note = self.notes_entry.get("1.0", "end-1c").strip()
        
        # Don't save empty notes or placeholder text
        if not clock_in_note or clock_in_note == "Write note here before clock in":
            clock_in_note = ""
        
        # Record clock in time and update status
        self.current_status = 'clocked_in'
        self.clock_in_time = datetime.datetime.now()
        self.clock_in_note = clock_in_note if clock_in_note else None
        
        # Clear the notes field
        self.notes_entry.delete("1.0", tk.END)
        self.update_word_count()
        
        self.save_user_data()         # Save to file
        self.update_display()         # Update UI
        
        # Show success message
        success_msg = f"Clocked in at {self.clock_in_time.strftime('%I:%M:%S %p')}"
        if clock_in_note:
            success_msg += f"\nClock-in note: {clock_in_note}"
        messagebox.showinfo("Success", success_msg)

    def clock_out(self):
        """Record when user stops working"""
        # Prevent double clock-out
        if self.current_status == 'clocked_out':
            messagebox.showwarning("Already Clocked Out",
                                  "You are already clocked out!")
            return

        # Get the clock out note
        clock_out_note = self.notes_entry.get("1.0", "end-1c").strip()
        
        # Don't save empty notes or placeholder text
        if not clock_out_note or clock_out_note == "Write note here before clock in":
            clock_out_note = ""
            
        # Calculate session duration
        clock_out_time = datetime.datetime.now()
        session_time = clock_out_time - self.clock_in_time
        self.total_time_today += session_time

        # Combine notes if both exist
        combined_note = ""
        if self.clock_in_note:
            combined_note = f"Clock-in: {self.clock_in_note}"
        if clock_out_note:
            if combined_note:
                combined_note += " | "
            combined_note += f"Clock-out: {clock_out_note}"

        # Save session to history
        self.add_history_entry(self.clock_in_time, clock_out_time, session_time, combined_note)

        # Update status and save
        self.current_status = 'clocked_out'
        self.clock_in_note = None  # Reset clock in note
        self.notes_entry.delete("1.0", tk.END)  # Clear notes field
        self.update_word_count()
        
        self.save_user_data()
        self.update_display()

        # Show success message with duration and notes
        success_msg = f"Clocked out at {clock_out_time.strftime('%I:%M:%S %p')}\n"
        success_msg += f"Session duration: {self.format_timedelta(session_time)}"
        if combined_note:
            success_msg += f"\nNotes: {combined_note}"
        messagebox.showinfo("Success", success_msg)

    def add_missed_entry(self):
        """Add a missed clock in/out entry"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Missed Entry")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Add Missed Entry", 
                font=("Arial", 14, "bold")).pack(pady=10)

        # Date
        tk.Label(dialog, text="Date (YYYY-MM-DD):").pack()
        date_entry = tk.Entry(dialog, width=30)
        date_entry.insert(0, datetime.datetime.now().strftime('%Y-%m-%d'))
        date_entry.pack(pady=5)

        # Clock in time
        tk.Label(dialog, text="Clock In Time (HH:MM):").pack()
        clock_in_entry = tk.Entry(dialog, width=30)
        clock_in_entry.insert(0, "09:00")
        clock_in_entry.pack(pady=5)

        # Clock out time
        tk.Label(dialog, text="Clock Out Time (HH:MM):").pack()
        clock_out_entry = tk.Entry(dialog, width=30)
        clock_out_entry.insert(0, "17:00")
        clock_out_entry.pack(pady=5)

        def save_entry():
            try:
                date_str = date_entry.get()
                clock_in_str = clock_in_entry.get()
                clock_out_str = clock_out_entry.get()

                clock_in = datetime.datetime.strptime(
                    f"{date_str} {clock_in_str}", '%Y-%m-%d %H:%M')
                clock_out = datetime.datetime.strptime(
                    f"{date_str} {clock_out_str}", '%Y-%m-%d %H:%M')

                current_time = datetime.datetime.now()
                
                if clock_out <= clock_in:
                    self.show_message("Error", "Clock out must be after clock in!", "error")
                    return
                
                if clock_out > current_time:
                    self.show_message("Error", "Cannot clock out beyond current time!", "error")
                    return

                duration = clock_out - clock_in
                self.add_history_entry(clock_in, clock_out, duration)

                messagebox.showinfo("Success", 
                                   f"Added entry: {self.format_timedelta(duration)}")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid date/time format: {e}")

        tk.Button(dialog, text="Save Entry", command=save_entry,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                 padx=20, pady=5).pack(pady=20)

    def show_history(self):
        """Show complete history"""
        # Reload history to get latest data
        self.load_history()
        
        history_window = tk.Toplevel(self.root)
        history_window.title("Time Clock History")
        history_window.geometry("700x500")

        tk.Label(history_window, text=f"History for {self.current_user}", 
                font=("Arial", 14, "bold")).pack(pady=10)

        # Create treeview
        tree_frame = tk.Frame(history_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(tree_frame, 
                           columns=('Date', 'Clock In', 'Clock Out', 'Duration', 'Notes'),
                           show='headings',
                           yscrollcommand=scrollbar.set)

        tree.heading('Date', text='Date')
        tree.heading('Clock In', text='Clock In')
        tree.heading('Clock Out', text='Clock Out')
        tree.heading('Duration', text='Duration')
        tree.heading('Notes', text='Notes')
        
        # Handle attempts to edit notes
        def show_edit_error(event):
            col = tree.identify_column(event.x)
            col_name = tree.column(col)['id']
            if col_name == 'Notes':
                messagebox.showerror("Error", "Cannot edit notes")
                
        tree.bind('<Double-1>', show_edit_error)

        tree.column('Date', width=100)
        tree.column('Clock In', width=120)
        tree.column('Clock Out', width=120)
        tree.column('Duration', width=100)
        tree.column('Notes', width=200)

        scrollbar.config(command=tree.yview)

        # Sort history by date (newest first)
        sorted_history = sorted(self.history, 
                               key=lambda x: x['clock_in'], 
                               reverse=True)

        total_duration = datetime.timedelta()
        for entry in sorted_history:
            clock_in = datetime.datetime.fromisoformat(entry['clock_in'])
            clock_out = datetime.datetime.fromisoformat(entry['clock_out'])
            duration = datetime.timedelta(seconds=entry['duration_seconds'])
            total_duration += duration

            # Get note and filter out placeholder text
            note = entry.get('note', '').strip()
            if note == "Write note here before clock in":
                note = ''

            tree.insert('', tk.END, values=(
                clock_in.strftime('%Y-%m-%d'),
                clock_in.strftime('%I:%M:%S %p'),
                clock_out.strftime('%I:%M:%S %p'),
                self.format_timedelta(duration),
                note  # Only show actual notes, not placeholder
            ))

        tree.pack(fill=tk.BOTH, expand=True)

        # Total
        tk.Label(history_window, 
                text=f"Total Time: {self.format_timedelta(total_duration)}", 
                font=("Arial", 12, "bold")).pack(pady=10)

    def show_weekly_summary(self):
        """Show weekly summary"""
        self._show_summary("Weekly", 7)

    def show_monthly_summary(self):
        """Show monthly summary"""
        self._show_summary("Monthly", 30)

    def _show_summary(self, period_name, days):
        """Show summary for specified period"""
        summary_window = tk.Toplevel(self.root)
        summary_window.title(f"{period_name} Summary")
        summary_window.geometry("600x400")

        tk.Label(summary_window, 
                text=f"{period_name} Summary for {self.current_user}", 
                font=("Arial", 14, "bold")).pack(pady=10)

        # Calculate date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)

        # Filter history
        daily_totals = defaultdict(lambda: datetime.timedelta())

        for entry in self.history:
            clock_in = datetime.datetime.fromisoformat(entry['clock_in'])
            if start_date <= clock_in <= end_date:
                date_key = clock_in.strftime('%Y-%m-%d')
                duration = datetime.timedelta(seconds=entry['duration_seconds'])
                daily_totals[date_key] += duration

        # Create treeview
        tree_frame = tk.Frame(summary_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(tree_frame, 
                           columns=('Date', 'Hours Worked'),
                           show='headings',
                           yscrollcommand=y_scrollbar.set)

        tree.heading('Date', text='Date')
        tree.heading('Hours Worked', text='Hours Worked')

        tree.column('Date', width=200)
        tree.column('Hours Worked', width=200)
        
        y_scrollbar.config(command=tree.yview)

        total_time = datetime.timedelta()
        for date_key in sorted(daily_totals.keys(), reverse=True):
            duration = daily_totals[date_key]
            total_time += duration
            tree.insert('', tk.END, values=(
                date_key,
                self.format_timedelta(duration)
            ))

        tree.pack(fill=tk.BOTH, expand=True)

        # Summary stats
        stats_frame = tk.Frame(summary_window)
        stats_frame.pack(pady=10)

        days_worked = len(daily_totals)
        avg_per_day = total_time / days_worked if days_worked > 0 else datetime.timedelta()

        tk.Label(stats_frame, 
                text=f"Total Time: {self.format_timedelta(total_time)}", 
                font=("Arial", 11, "bold")).pack()
        tk.Label(stats_frame, 
                text=f"Days Worked: {days_worked}", 
                font=("Arial", 11)).pack()
        tk.Label(stats_frame, 
                text=f"Average per Day: {self.format_timedelta(avg_per_day)}", 
                font=("Arial", 11)).pack()

    def export_to_csv(self):
        """Export history to CSV file"""
        if not self.history:
            messagebox.showwarning("No Data", "No history to export!")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"timeclock_{self.current_user}_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
        )

        if filename:
            try:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['User', 'Date', 'Clock In', 'Clock Out', 
                                   'Duration (HH:MM:SS)', 'Duration (Hours)'])

                    for entry in sorted(self.history, key=lambda x: x['clock_in']):
                        clock_in = datetime.datetime.fromisoformat(entry['clock_in'])
                        clock_out = datetime.datetime.fromisoformat(entry['clock_out'])
                        duration = datetime.timedelta(seconds=entry['duration_seconds'])

                        writer.writerow([
                            self.current_user,
                            clock_in.strftime('%Y-%m-%d'),
                            clock_in.strftime('%I:%M:%S %p'),
                            clock_out.strftime('%I:%M:%S %p'),
                            self.format_timedelta(duration),
                            f"{duration.total_seconds() / 3600:.2f}"
                        ])

                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")

    def switch_user(self):
        """Switch to a different user"""
        self.running = False
        time.sleep(0.5)  # Wait for thread to stop
        self.show_user_selection()

    def reset_day(self):
        """Reset the daily time tracking"""
        result = messagebox.askyesno("Confirm Reset",
                                    "Are you sure you want to reset daily time?")
        if result:
            self.total_time_today = datetime.timedelta()
            if self.current_status == 'clocked_in':
                self.clock_in_time = datetime.datetime.now()
            self.save_user_data()
            self.update_display()
            messagebox.showinfo("Success", "Daily time has been reset!")

    def format_timedelta(self, td):
        """Format timedelta to readable string"""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
    def show_message(self, title, message, message_type="info"):
        """Show a centered message box of specified type"""
        if message_type == "error":
            dialog = messagebox.showerror(title, message, parent=self.root)
        elif message_type == "warning":
            dialog = messagebox.showwarning(title, message, parent=self.root)
        elif message_type == "yesno":
            dialog = messagebox.askyesno(title, message, parent=self.root)
            return dialog
        else:  # info
            dialog = messagebox.showinfo(title, message, parent=self.root)
            
    def center_window(self, window):
        """Center any window relative to the main window"""
        window.update_idletasks()  # Update window size
        
        # Get main window position and dimensions
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        
        # Calculate center position
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        position_x = main_x + (main_width - window_width) // 2
        position_y = main_y + (main_height - window_height) // 2
        
        # Set the position
        window.geometry(f"+{position_x}+{position_y}")
        window.lift()  # Bring window to front

    def update_display(self):
        """Update all display elements"""
        now = datetime.datetime.now()

        if self.current_status == 'clocked_in':
            self.status_label.config(text="🟢 CLOCKED IN", fg="#27ae60")
            self.clock_in_label.config(
                text=f"Clocked in at: {self.clock_in_time.strftime('%I:%M:%S %p')}")

            current_session = now - self.clock_in_time
            self.session_label.config(
                text=f"Current session: {self.format_timedelta(current_session)}")

            total_today = self.total_time_today + current_session
            self.total_label.config(
                text=f"Total time today: {self.format_timedelta(total_today)}")

            self.clock_in_btn.config(state=tk.DISABLED)
            self.clock_out_btn.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="🔴 CLOCKED OUT", fg="#e74c3c")
            self.clock_in_label.config(text="Not currently clocked in")
            self.session_label.config(text="Current session: 00:00:00")
            self.total_label.config(
                text=f"Total time today: {self.format_timedelta(self.total_time_today)}")

            self.clock_in_btn.config(state=tk.NORMAL)
            self.clock_out_btn.config(state=tk.DISABLED)

    def update_time_display(self):
        """Update current time display continuously"""
        while self.running:
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M:%S %p")
            date_str = now.strftime("%A, %B %d, %Y")

            try:
                self.current_time_label.config(text=f"{time_str}\n{date_str}")

                if self.current_status == 'clocked_in':
                    self.update_display()
            except Exception:
                break

            time.sleep(1)

    def update_word_count(self, event=None):
        """Update word count label and enforce 20 word limit"""
        text = self.notes_entry.get("1.0", "end-1c").strip()
        words = text.split()
        word_count = len(words)
        
        self.word_count_label.config(text=f"{word_count}/20 words")
        
        # If we're over the limit, truncate to 20 words
        if word_count > 20:
            # Join first 20 words and update text
            new_text = " ".join(words[:20])
            self.notes_entry.delete("1.0", tk.END)
            self.notes_entry.insert("1.0", new_text)
            return "break"

    def on_closing(self):
        """Handle window close event"""
        self.running = False
        # Destroy all toplevel windows
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
        # Destroy the main window
        self.root.destroy()


def main():
    root = tk.Tk()
    app = TimeClockGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
