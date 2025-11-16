"""
Time Clock App for Android using Kivy
Simplified version of timeclock_gui_enhanced.py adapted for mobile
"""

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import datetime
import json
import os

# Set window size for testing on desktop
Window.size = (400, 700)


class TimeClockApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # File paths
        self.data_file = 'timeclock_data.json'
        self.history_file = 'timeclock_history.json'
        self.users_file = 'timeclock_users.json'
        self.weekly_archive_file = 'timeclock_weekly_archive.json'
        
        # State variables
        self.current_user = None
        self.current_status = 'clocked_out'
        self.clock_in_time = None
        self.clock_in_note = None
        self.total_time_today = datetime.timedelta()
        self.history = []
        self.users = {}
        self.weekly_archive = {}
        
        # Load existing data
        self.load_users()
        self.load_history()
        self.load_weekly_archive()
    
    def load_users(self):
        """Load users from file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            except:
                self.users = {}
    
    def save_users(self):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def load_history(self):
        """Load history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    all_history = json.load(f)
                    self.history = all_history.get(self.current_user, []) if self.current_user else []
            except:
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
            except:
                pass
        
        all_history[self.current_user] = self.history
        
        with open(self.history_file, 'w') as f:
            json.dump(all_history, f, indent=2)
    
    def load_weekly_archive(self):
        """Load weekly archive from file"""
        if os.path.exists(self.weekly_archive_file):
            try:
                with open(self.weekly_archive_file, 'r') as f:
                    self.weekly_archive = json.load(f)
            except:
                self.weekly_archive = {}
        else:
            self.weekly_archive = {}
    
    def save_weekly_archive(self):
        """Save weekly archive to file"""
        with open(self.weekly_archive_file, 'w') as f:
            json.dump(self.weekly_archive, f, indent=2)
    
    def add_to_weekly_archive(self, week_end_date, total_hours, entries_count):
        """Add a week's total to the archive"""
        if self.current_user not in self.weekly_archive:
            self.weekly_archive[self.current_user] = []
        
        week_entry = {
            'week_end': week_end_date,
            'total_hours': total_hours,
            'entries_count': entries_count,
            'archived_date': datetime.datetime.now().isoformat()
        }
        self.weekly_archive[self.current_user].append(week_entry)
        self.save_weekly_archive()
    
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
            except:
                self.current_status = 'clocked_out'
    
    def save_user_data(self):
        """Save current user's data"""
        all_data = {}
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    all_data = json.load(f)
            except:
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
    
    def add_history_entry(self, clock_in, clock_out, duration, note=""):
        """Add entry to history"""
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
    
    def format_timedelta(self, td):
        """Format timedelta to readable string"""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def format_hours(self, td):
        """Format timedelta to hours decimal (e.g. 7.5 hours)"""
        total_seconds = td.total_seconds()
        hours = total_seconds / 3600
        return f"{hours:.1f}"
    
    def format_hours_minutes(self, td):
        """Format timedelta to hours and minutes (e.g. 7h 30m)"""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    
    def get_today_hours(self):
        """Get total hours clocked in today"""
        today = datetime.datetime.now().date()
        today_total = datetime.timedelta()
        
        for entry in self.history:
            clock_in = datetime.datetime.fromisoformat(entry['clock_in'])
            if clock_in.date() == today:
                duration = datetime.timedelta(seconds=entry['duration_seconds'])
                today_total += duration
        
        # Add current session if clocked in
        if self.current_status == 'clocked_in':
            current_session = datetime.datetime.now() - self.clock_in_time
            today_total += current_session
        
        return today_total
    
    def get_weekly_hours(self):
        """Get total hours clocked in this week (last 7 days)"""
        today = datetime.datetime.now().date()
        week_start = today - datetime.timedelta(days=today.weekday())  # Monday
        week_total = datetime.timedelta()
        
        for entry in self.history:
            clock_in = datetime.datetime.fromisoformat(entry['clock_in'])
            if week_start <= clock_in.date() <= today:
                duration = datetime.timedelta(seconds=entry['duration_seconds'])
                week_total += duration
        
        # Add current session if clocked in
        if self.current_status == 'clocked_in':
            current_session = datetime.datetime.now() - self.clock_in_time
            week_total += current_session
        
        return week_total
    
    def get_daily_breakdown(self):
        """Get hours per day for the week"""
        today = datetime.datetime.now().date()
        week_start = today - datetime.timedelta(days=today.weekday())  # Monday
        daily_hours = {}
        
        # Initialize all days
        for i in range(7):
            day = week_start + datetime.timedelta(days=i)
            daily_hours[day.strftime('%a')] = datetime.timedelta()
        
        # Sum up entries
        for entry in self.history:
            clock_in = datetime.datetime.fromisoformat(entry['clock_in'])
            if week_start <= clock_in.date() <= today:
                day_name = clock_in.strftime('%a')
                duration = datetime.timedelta(seconds=entry['duration_seconds'])
                daily_hours[day_name] += duration
        
        # Add current session if clocked in
        if self.current_status == 'clocked_in':
            current_session = datetime.datetime.now() - self.clock_in_time
            today_name = today.strftime('%a')
            daily_hours[today_name] += current_session
        
        return daily_hours
    
    def build(self):
        """Build the main UI"""
        if not self.users:
            return self.create_first_user_screen()
        else:
            return self.show_user_selection_screen()
    
    def create_first_user_screen(self):
        """Screen to create first user"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        layout.add_widget(Label(text='Create Your Account', size_hint_y=0.2, 
                               font_size='24sp', bold=True))
        
        username_input = TextInput(
            hint_text='Enter your name',
            multiline=False,
            size_hint_y=0.2
        )
        layout.add_widget(username_input)
        
        def create_user():
            if username_input.text.strip():
                self.users[username_input.text] = {
                    'created': datetime.datetime.now().isoformat(),
                    'total_hours': 0
                }
                self.current_user = username_input.text
                self.save_users()
                self.load_user_data()
                self.root.clear_widgets()
                self.root.add_widget(self.create_main_screen())
            else:
                self.show_popup('Error', 'Username is required!')
        
        create_btn = Button(text='Create Account', size_hint_y=0.2)
        create_btn.bind(on_press=lambda x: create_user())
        layout.add_widget(create_btn)
        
        layout.add_widget(Label(size_hint_y=0.4))  # Spacer
        
        return layout
    
    def show_user_selection_screen(self):
        """Screen to select user - Modern purple, black, white theme"""
        from kivy.graphics import Color, Rectangle
        
        # Black background layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        def update_bg(instance, value):
            layout.canvas.before.clear()
            with layout.canvas.before:
                Color(0, 0, 0, 1)  # Black background
                Rectangle(size=layout.size, pos=layout.pos)
        
        layout.bind(size=update_bg, pos=update_bg)
        update_bg(layout, None)
        
        # Header with purple background
        header_layout = BoxLayout(size_hint_y=0.12, padding=10)
        
        def update_header_bg(instance, value):
            header_layout.canvas.before.clear()
            with header_layout.canvas.before:
                Color(0.6, 0.2, 1, 1)  # Bright purple
                Rectangle(size=header_layout.size, pos=header_layout.pos)
        
        header_layout.bind(size=update_header_bg, pos=update_header_bg)
        update_header_bg(header_layout, None)
        
        header_label = Label(
            text='Select User',
            size_hint_y=1,
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1)  # White text
        )
        header_layout.add_widget(header_label)
        layout.add_widget(header_layout)
        
        # User list with purple buttons
        user_list = GridLayout(cols=1, spacing=10, size_hint_y=0.7)
        
        for username in self.users.keys():
            btn = Button(
                text=username,
                size_hint_y=None,
                height=60,
                background_color=(0.6, 0.2, 1, 1),  # Purple background
                color=(1, 1, 1, 1),  # White text
                font_size='16sp',
                bold=True
            )
            btn.bind(on_press=lambda x, u=username: self.select_user(u))
            user_list.add_widget(btn)
        
        scroll = ScrollView(size_hint=(1, 0.7))
        scroll.add_widget(user_list)
        layout.add_widget(scroll)
        
        # New User Button - Accent style
        new_user_btn = Button(
            text='+ New User',
            size_hint_y=0.15,
            background_color=(0.35, 0.1, 0.6, 1),  # Darker purple accent
            color=(1, 1, 1, 1),  # White text
            font_size='16sp',
            bold=True
        )
        new_user_btn.bind(on_press=self.show_new_user_dialog)
        layout.add_widget(new_user_btn)
        
        return layout
    
    def select_user(self, username):
        """Select a user"""
        self.current_user = username
        self.load_user_data()
        self.load_history()
        self.root.clear_widgets()
        self.root.add_widget(self.create_main_screen())
    
    def show_new_user_dialog(self, instance):
        """Show dialog to create new user"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        username_input = TextInput(
            hint_text='Enter username',
            multiline=False
        )
        content.add_widget(username_input)
        
        btn_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        
        def create():
            if username_input.text.strip():
                if username_input.text in self.users:
                    self.show_popup('Error', 'User already exists!')
                else:
                    self.users[username_input.text] = {
                        'created': datetime.datetime.now().isoformat(),
                        'total_hours': 0
                    }
                    self.save_users()
                    popup.dismiss()
                    self.root.clear_widgets()
                    self.root.add_widget(self.show_user_selection_screen())
        
        btn_layout.add_widget(Button(text='Create', on_press=lambda x: create()))
        btn_layout.add_widget(Button(text='Cancel', on_press=lambda x: popup.dismiss()))
        content.add_widget(btn_layout)
        
        popup = Popup(title='New User', content=content, size_hint=(0.9, 0.3))
        popup.open()
    
    def create_main_screen(self):
        """Create main application screen"""
        from kivy.clock import Clock
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        # Header
        header = Label(text=f'⏰ {self.current_user}', size_hint_y=0.08, 
                      font_size='20sp', bold=True)
        layout.add_widget(header)
        
        # Current time (will be updated by timer)
        current_time = Label(
            text=datetime.datetime.now().strftime('%I:%M:%S %p'),
            size_hint_y=0.08,
            font_size='16sp'
        )
        layout.add_widget(current_time)
        
        # Status (will be updated by timer)
        status_text = '🟢 CLOCKED IN' if self.current_status == 'clocked_in' else '🔴 CLOCKED OUT'
        status = Label(text=status_text, size_hint_y=0.08, font_size='16sp', bold=True)
        layout.add_widget(status)
        
        # Daily and Weekly Hours Summary (will be updated by timer)
        stats_label = Label(
            text="Today: 0.0 hrs | Week: 0.0 hrs",
            size_hint_y=0.08,
            font_size='14sp',
            bold=True
        )
        layout.add_widget(stats_label)
        
        # Time display HH:MM:SS (will be updated by timer)
        time_info = Label(
            text='Total today: 00:00:00',
            size_hint_y=0.08,
            font_size='14sp'
        )
        layout.add_widget(time_info)
        
        # Notes
        notes_input = TextInput(
            hint_text='Add note (max 20 words)',
            multiline=True,
            size_hint_y=0.15
        )
        layout.add_widget(notes_input)
        
        # Buttons
        button_layout = GridLayout(cols=1, spacing=5, size_hint_y=0.35)
        
        clock_in_btn = Button(
            text='CLOCK IN',
            background_color=(0.15, 0.68, 0.37, 1),
            size_hint_y=0.15
        )
        
        def on_clock_in():
            if self.current_status == 'clocked_in':
                self.show_popup('Error', 'Already clocked in!')
                return
            
            self.current_status = 'clocked_in'
            self.clock_in_time = datetime.datetime.now()
            self.clock_in_note = notes_input.text.strip()
            self.save_user_data()
            self.show_popup('Success', f'Clocked in at {self.clock_in_time.strftime("%I:%M:%S %p")}')
            notes_input.text = ''
            self.root.clear_widgets()
            self.root.add_widget(self.create_main_screen())
        
        clock_in_btn.bind(on_press=lambda x: on_clock_in())
        button_layout.add_widget(clock_in_btn)
        
        clock_out_btn = Button(
            text='CLOCK OUT',
            background_color=(0.91, 0.30, 0.24, 1),
            size_hint_y=0.15
        )
        
        def on_clock_out():
            if self.current_status == 'clocked_out':
                self.show_popup('Error', 'Already clocked out!')
                return
            
            clock_out_time = datetime.datetime.now()
            session_time = clock_out_time - self.clock_in_time
            self.total_time_today += session_time
            
            note = notes_input.text.strip()
            if self.clock_in_note:
                note = f"In: {self.clock_in_note} | Out: {note}" if note else f"In: {self.clock_in_note}"
            
            self.add_history_entry(self.clock_in_time, clock_out_time, session_time, note)
            
            self.current_status = 'clocked_out'
            self.clock_in_note = None
            self.save_user_data()
            
            self.show_popup('Success', 
                          f'Clocked out\nSession: {self.format_timedelta(session_time)}')
            notes_input.text = ''
            self.root.clear_widgets()
            self.root.add_widget(self.create_main_screen())
        
        clock_out_btn.bind(on_press=lambda x: on_clock_out())
        button_layout.add_widget(clock_out_btn)
        
        view_history_btn = Button(text='View History', size_hint_y=0.12)
        view_history_btn.bind(on_press=lambda x: self.show_history_screen())
        button_layout.add_widget(view_history_btn)
        
        view_archive_btn = Button(text='View Previous Weeks', size_hint_y=0.12)
        view_archive_btn.bind(on_press=lambda x: self.show_archive_screen())
        button_layout.add_widget(view_archive_btn)
        
        reset_weekly_btn = Button(text='Reset Weekly', size_hint_y=0.12)
        reset_weekly_btn.bind(on_press=lambda x: self.reset_weekly_hours())
        button_layout.add_widget(reset_weekly_btn)
        
        print_btn = Button(text='Print Hours', size_hint_y=0.12)
        print_btn.bind(on_press=lambda x: self.show_print_screen())
        button_layout.add_widget(print_btn)
        
        switch_user_btn = Button(text='Switch User', size_hint_y=0.12)
        switch_user_btn.bind(on_press=lambda x: self.switch_user())
        button_layout.add_widget(switch_user_btn)
        
        layout.add_widget(button_layout)
        
        # Timer to update labels every second
        def update_display(dt):
            try:
                # Update time
                current_time.text = datetime.datetime.now().strftime('%I:%M:%S %p')
                
                # Update status
                status_text = '🟢 CLOCKED IN' if self.current_status == 'clocked_in' else '🔴 CLOCKED OUT'
                status.text = status_text
                
                # Update hours display
                today_hours = self.get_today_hours()
                weekly_hours = self.get_weekly_hours()
                today_display = self.format_hours_minutes(today_hours)
                weekly_display = self.format_hours_minutes(weekly_hours)
                stats_label.text = f"Today: {today_display} | Week: {weekly_display}"
                
                # Update time info
                time_info.text = f'Total today: {self.format_timedelta(today_hours)}'
            except:
                pass
        
        # Schedule the update to run every 1 second
        Clock.schedule_interval(update_display, 1)
        
        return layout
    
    def show_history_screen(self):
        """Show history in a scrollable list with cumulative total hours"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='Time Clock History', size_hint_y=0.1, 
                               font_size='18sp', bold=True))
        
        history_list = GridLayout(cols=1, spacing=5, size_hint_y=0.8)
        
        # Sort history by date (oldest first to calculate cumulative totals)
        sorted_history = sorted(self.history, key=lambda x: x['clock_in'])
        
        cumulative_total = datetime.timedelta()
        
        # Reverse for display (newest first) but calculate cumulative from oldest
        for entry in reversed(sorted_history):
            clock_in = datetime.datetime.fromisoformat(entry['clock_in'])
            clock_out = datetime.datetime.fromisoformat(entry['clock_out'])
            duration = datetime.timedelta(seconds=entry['duration_seconds'])
            cumulative_total += duration
            
            session_time_display = self.format_hours_minutes(duration)
            cumulative_time_display = self.format_hours_minutes(cumulative_total)
            
            entry_text = f"{clock_in.strftime('%Y-%m-%d')}\nIn: {clock_in.strftime('%I:%M %p')} → Out: {clock_out.strftime('%I:%M %p')}\nSession: {session_time_display} | Total: {cumulative_time_display}"
            if entry.get('note'):
                entry_text += f"\nNote: {entry['note']}"
            
            history_list.add_widget(Label(
                text=entry_text,
                size_hint_y=None,
                height=100,
                markup=True
            ))
        
        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(history_list)
        layout.add_widget(scroll)
        
        back_btn = Button(text='Back', size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: (self.root.clear_widgets(), 
                                          self.root.add_widget(self.create_main_screen())))
        layout.add_widget(back_btn)
        
        self.root.clear_widgets()
        self.root.add_widget(layout)
    
    def show_archive_screen(self):
        """Show archived previous weeks data"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='Previous Weeks Archive', size_hint_y=0.1, 
                               font_size='18sp', bold=True))
        
        archive_list = GridLayout(cols=1, spacing=5, size_hint_y=0.8)
        
        # Get archived weeks for current user
        user_archive = self.weekly_archive.get(self.current_user, [])
        
        if not user_archive:
            archive_list.add_widget(Label(
                text='No previous weeks archived yet.\n\nUse "Reset Weekly" to archive data.',
                size_hint_y=None,
                height=100
            ))
        else:
            # Sort by week_end date (newest first)
            sorted_archive = sorted(user_archive, key=lambda x: x['week_end'], reverse=True)
            
            for week in sorted_archive:
                week_end = datetime.datetime.fromisoformat(week['week_end']).date()
                total_hours = week['total_hours']
                entries_count = week['entries_count']
                archived_date = datetime.datetime.fromisoformat(week['archived_date'])
                
                # Convert total_hours (decimal) to hours and minutes
                hours = int(total_hours)
                minutes = int((total_hours - hours) * 60)
                
                entry_text = (
                    f"Week Ended: {week_end.strftime('%Y-%m-%d (%A)')}\n"
                    f"Total: {hours}h {minutes}m | Entries: {entries_count}\n"
                    f"Archived: {archived_date.strftime('%Y-%m-%d %I:%M %p')}"
                )
                
                archive_list.add_widget(Label(
                    text=entry_text,
                    size_hint_y=None,
                    height=90,
                    markup=True
                ))
        
        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(archive_list)
        layout.add_widget(scroll)
        
        back_btn = Button(text='Back', size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: (self.root.clear_widgets(), 
                                          self.root.add_widget(self.create_main_screen())))
        layout.add_widget(back_btn)
        
        self.root.clear_widgets()
        self.root.add_widget(layout)
    
    def show_print_screen(self):
        """Show printable hours report for current and previous week"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='Hours Report', size_hint_y=0.08, 
                               font_size='18sp', bold=True))
        
        # Generate report content
        report_text = self.generate_hours_report()
        
        # Display report in a scrollable text area
        report_display = Label(
            text=report_text,
            size_hint_y=0.8,
            markup=True,
            valign='top',
            halign='left'
        )
        
        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(report_display)
        layout.add_widget(scroll)
        
        # Buttons for print actions
        button_layout = GridLayout(cols=2, spacing=10, size_hint_y=0.12)
        
        print_btn = Button(text='Print (System)')
        print_btn.bind(on_press=lambda x: self.print_report())
        button_layout.add_widget(print_btn)
        
        copy_btn = Button(text='Copy to Clipboard')
        copy_btn.bind(on_press=lambda x: self.copy_report_to_clipboard())
        button_layout.add_widget(copy_btn)
        
        layout.add_widget(button_layout)
        
        back_btn = Button(text='Back', size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: (self.root.clear_widgets(), 
                                          self.root.add_widget(self.create_main_screen())))
        layout.add_widget(back_btn)
        
        self.root.clear_widgets()
        self.root.add_widget(layout)
    
    def generate_hours_report(self):
        """Generate a text report of current and previous week hours"""
        today = datetime.datetime.now().date()
        week_start = today - datetime.timedelta(days=today.weekday())  # Monday
        week_end = week_start + datetime.timedelta(days=6)  # Sunday
        
        # Get current week hours
        current_week_duration = self.get_weekly_hours()
        current_week_display = self.format_hours_minutes(current_week_duration)
        
        # Get previous week hours from archive
        user_archive = self.weekly_archive.get(self.current_user, [])
        previous_week_hours = "No data"
        previous_week_display = ""
        
        if user_archive:
            # Get most recent archived week
            sorted_archive = sorted(user_archive, key=lambda x: x['week_end'], reverse=True)
            if sorted_archive:
                recent_week = sorted_archive[0]
                previous_week_end = datetime.datetime.fromisoformat(recent_week['week_end']).date()
                total_hours_decimal = recent_week['total_hours']
                
                # Convert to hours and minutes
                hours = int(total_hours_decimal)
                minutes = int((total_hours_decimal - hours) * 60)
                previous_week_display = f"{hours}h {minutes}m"
        
        # Generate report with ASCII characters (no special Unicode)
        report = (
            f"=======================================\n"
            f"        HOURS WORKED REPORT\n"
            f"         User: {self.current_user}\n"
            f"    Printed: {datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n"
            f"=======================================\n\n"
            f"CURRENT WEEK\n"
            f"Period: {week_start.strftime('%a, %b %d')} - {week_end.strftime('%a, %b %d')}\n"
            f"Hours Worked: {current_week_display}\n\n"
            f"---------------------------------------\n"
            f"PREVIOUS WEEK\n"
        )
        
        if user_archive and sorted_archive:
            recent_week = sorted_archive[0]
            previous_week_end = datetime.datetime.fromisoformat(recent_week['week_end']).date()
            previous_week_start = previous_week_end - datetime.timedelta(days=6)
            
            report += (
                f"Period: {previous_week_start.strftime('%a, %b %d')} - {previous_week_end.strftime('%a, %b %d')}\n"
                f"Hours Worked: {previous_week_display}\n"
            )
        else:
            report += f"No previous week data available.\n"
        
        report += (
            f"---------------------------------------\n"
            f"=======================================\n"
        )
        
        return report
    
    def print_report(self):
        """Print the hours report - opens system print dialog"""
        report = self.generate_hours_report()
        
        try:
            import subprocess
            import platform
            import os
            import tempfile
            
            # Create a temporary file with the report
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(report)
                temp_path = f.name
            
            try:
                if platform.system() == 'Windows':
                    # On Windows, use notepad with print dialog
                    # This opens the file in Notepad with print dialog
                    subprocess.Popen(['notepad', temp_path])
                    self.show_popup('Print', 'Notepad opened with your report.\nUse File > Print to print.')
                elif platform.system() == 'Darwin':
                    # macOS - open with default app
                    subprocess.run(['open', temp_path])
                    self.show_popup('Print', 'Report opened in default application.')
                else:
                    # Linux
                    subprocess.run(['xdg-open', temp_path])
                    self.show_popup('Print', 'Report opened in default application.')
                    
            except Exception as e:
                self.show_popup('Error', f'Failed to open print dialog: {str(e)}')
                
        except Exception as e:
            self.show_popup('Error', f'Error: {str(e)}')
    
    def copy_report_to_clipboard(self):
        """Copy the hours report to clipboard"""
        report = self.generate_hours_report()
        
        try:
            # Try using pyperclip if available
            try:
                import pyperclip
                pyperclip.copy(report)
            except:
                # Fallback: use tkinter if available
                try:
                    import tkinter as tk
                    root = tk.Tk()
                    root.withdraw()
                    root.clipboard_clear()
                    root.clipboard_append(report)
                    root.update()
                    root.destroy()
                except:
                    self.show_popup('Error', 'Clipboard copy not supported on this system')
                    return
            
            self.show_popup('Success', 'Report copied to clipboard!')
        except Exception as e:
            self.show_popup('Error', f'Copy failed: {str(e)}')
    
    def reset_weekly_hours(self):
        """Reset weekly hours - archive completed week (Mon-Sun), keep current week and daily hours"""
        # Get the start of the current week (Monday)
        today = datetime.datetime.now().date()
        week_start = today - datetime.timedelta(days=today.weekday())  # Monday of this week
        
        # Calculate week end (Sunday of this week)
        week_end = week_start + datetime.timedelta(days=6)  # Sunday
        
        # Get ALL entries this week (Monday through today)
        current_week_entries = [
            entry for entry in self.history
            if datetime.datetime.fromisoformat(entry['clock_in']).date() >= week_start
        ]
        
        # Get current session if clocked in
        current_session_duration = datetime.timedelta()
        if self.current_status == 'clocked_in' and self.clock_in_time:
            current_session_duration = datetime.datetime.now() - self.clock_in_time
        
        # Calculate current week total (entries + current session)
        week_total_seconds = sum(entry.get('duration_seconds', 0) for entry in current_week_entries)
        week_total_seconds += current_session_duration.total_seconds()
        week_total_duration = datetime.timedelta(seconds=week_total_seconds)
        
        # Get entries from previous weeks (before this week's Monday)
        previous_weeks_entries = [
            entry for entry in self.history
            if datetime.datetime.fromisoformat(entry['clock_in']).date() < week_start
        ]
        
        # Calculate total hours for the previous week(s) being archived
        if previous_weeks_entries:
            total_seconds = sum(entry.get('duration_seconds', 0) for entry in previous_weeks_entries)
            total_hours = round(total_seconds / 3600, 2)
            
            # Archive uses the END date of the week being archived (previous Sunday)
            prev_week_end = (week_start - datetime.timedelta(days=1)).isoformat()
            
            # Add to archive before removing entries
            self.add_to_weekly_archive(prev_week_end, total_hours, len(previous_weeks_entries))
        
        # Filter history to keep only current week entries (Mon onwards)
        original_count = len(self.history)
        self.history = [
            entry for entry in self.history
            if datetime.datetime.fromisoformat(entry['clock_in']).date() >= week_start
        ]
        removed_count = original_count - len(self.history)
        
        # Save the updated history
        self.save_history()
        
        # Show summary with current week total and week range
        current_week_display = self.format_hours_minutes(week_total_duration)
        week_range = f"{week_start.strftime('%a %b %d')} - {week_end.strftime('%a %b %d')}"
        self.show_popup(
            'Weekly Hours Reset',
            f'Week: {week_range}\n'
            f'This Week Total: {current_week_display}\n\n'
            f'Archived: {removed_count} entries from previous weeks\n'
            f'Kept: {len(self.history)} entries from current week'
        )
    
    def switch_user(self):
        """Switch to different user"""
        self.root.clear_widgets()
        self.root.add_widget(self.show_user_selection_screen())
    
    def show_popup(self, title, message):
        """Show a popup message"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        
        close_btn = Button(text='OK', size_hint_y=0.3)
        popup = Popup(title=title, content=content, size_hint=(0.9, 0.3))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()


if __name__ == '__main__':
    TimeClockApp().run()
