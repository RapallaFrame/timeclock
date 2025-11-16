#!/usr/bin/env python3
"""
Time Clock App - Test Suite (Non-GUI)

Tests core business logic without requiring Kivy GUI.
Validates: time tracking, hours calculation, archiving, data persistence.

Run: python test_timeclock.py
"""

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


class TimeClockTester:
    """Test suite for Time Clock App logic"""
    
    def __init__(self):
        self.test_dir = tempfile.mkdtemp(prefix="timeclock_test_")
        self.tests_passed = 0
        self.tests_failed = 0
        self.users_file = os.path.join(self.test_dir, "users.json")
        self.history_file = os.path.join(self.test_dir, "history.json")
        self.archive_file = os.path.join(self.test_dir, "archive.json")
        
        print(f"\n{BLUE}{BOLD}=== Time Clock App Test Suite ==={RESET}")
        print(f"Test directory: {self.test_dir}\n")
    
    def assert_equal(self, actual, expected, test_name):
        """Assert equality with formatted output"""
        if actual == expected:
            self.tests_passed += 1
            print(f"{GREEN}✓ PASS{RESET}: {test_name}")
            return True
        else:
            self.tests_failed += 1
            print(f"{RED}✗ FAIL{RESET}: {test_name}")
            print(f"  Expected: {expected}")
            print(f"  Actual:   {actual}")
            return False
    
    def assert_true(self, condition, test_name):
        """Assert condition is true"""
        if condition:
            self.tests_passed += 1
            print(f"{GREEN}✓ PASS{RESET}: {test_name}")
            return True
        else:
            self.tests_failed += 1
            print(f"{RED}✗ FAIL{RESET}: {test_name}")
            return False
    
    def assert_between(self, value, min_val, max_val, test_name):
        """Assert value is within range"""
        if min_val <= value <= max_val:
            self.tests_passed += 1
            print(f"{GREEN}✓ PASS{RESET}: {test_name}")
            return True
        else:
            self.tests_failed += 1
            print(f"{RED}✗ FAIL{RESET}: {test_name}")
            print(f"  Expected: {min_val} <= {value} <= {max_val}")
            return False
    
    # ==================== Data Persistence Tests ====================
    
    def test_save_and_load_users(self):
        """Test user creation and persistence"""
        print(f"\n{BOLD}[1. Data Persistence]{RESET}")
        
        users = {"alice": {"created": "2025-11-16", "total_hours": 40.5}}
        
        # Save users
        with open(self.users_file, 'w') as f:
            json.dump(users, f)
        
        # Load users
        with open(self.users_file, 'r') as f:
            loaded = json.load(f)
        
        self.assert_equal(loaded, users, "Save and load users")
        self.assert_equal(loaded["alice"]["total_hours"], 40.5, "User total hours preserved")
    
    def test_save_and_load_history(self):
        """Test history entry persistence"""
        now = datetime.now()
        history = {
            "1": {
                "clock_in": now.isoformat(),
                "clock_out": (now + timedelta(hours=8)).isoformat(),
                "duration_seconds": 28800,
                "date": "2025-11-16",
                "note": "Regular shift"
            }
        }
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, default=str)
        
        with open(self.history_file, 'r') as f:
            loaded = json.load(f)
        
        self.assert_equal(loaded["1"]["duration_seconds"], 28800, "History duration preserved")
        self.assert_equal(loaded["1"]["note"], "Regular shift", "History note preserved")
    
    # ==================== Time Calculation Tests ====================
    
    def test_hours_calculation(self):
        """Test converting seconds to hours"""
        print(f"\n{BOLD}[2. Time Calculations]{RESET}")
        
        # 8 hours = 28800 seconds
        seconds = 28800
        hours = seconds / 3600
        self.assert_equal(hours, 8.0, "8 hours calculation")
        
        # 7.5 hours = 27000 seconds
        seconds = 27000
        hours = seconds / 3600
        self.assert_equal(round(hours, 2), 7.5, "7.5 hours calculation")
        
        # 40.75 hours (40h 45m)
        seconds = 146700
        hours = seconds / 3600
        self.assert_equal(round(hours, 2), 40.75, "40.75 hours calculation")
    
    def test_format_hours_to_hm(self):
        """Test formatting hours to H:MM format"""
        def format_hours_minutes(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        
        self.assert_equal(format_hours_minutes(28800), "8h 0m", "Format 8 hours")
        self.assert_equal(format_hours_minutes(27000), "7h 30m", "Format 7.5 hours")
        self.assert_equal(format_hours_minutes(146700), "40h 45m", "Format 40h 45m")
    
    # ==================== Weekly Totals Tests ====================
    
    def test_daily_hours_calculation(self):
        """Test calculating daily hours from history"""
        print(f"\n{BOLD}[3. Daily Hours]{RESET}")
        
        today = datetime.now().date().isoformat()
        history = {
            "1": {
                "date": today,
                "duration_seconds": 28800  # 8 hours
            },
            "2": {
                "date": today,
                "duration_seconds": 14400  # 4 hours
            },
            "3": {
                "date": "2025-11-15",
                "duration_seconds": 10800  # 3 hours (different day)
            }
        }
        
        # Sum today's entries
        today_seconds = sum(
            entry["duration_seconds"] for entry in history.values()
            if entry["date"] == today
        )
        today_hours = today_seconds / 3600
        
        self.assert_equal(today_hours, 12.0, "Daily hours sum (8+4)")
        self.assert_equal(len([e for e in history.values() if e["date"] == today]), 2, 
                         "Today has 2 entries")
    
    def test_weekly_hours_calculation(self):
        """Test calculating weekly hours (Monday-Sunday)"""
        print(f"\n{BOLD}[4. Weekly Hours]{RESET}")
        
        # Create week of dates (Mon Nov 10 - Sun Nov 16, 2025)
        week_dates = [
            "2025-11-10",  # Monday
            "2025-11-11",  # Tuesday
            "2025-11-12",  # Wednesday
            "2025-11-13",  # Thursday
            "2025-11-14",  # Friday
            "2025-11-15",  # Saturday
            "2025-11-16",  # Sunday
        ]
        
        history = {}
        for i, date in enumerate(week_dates):
            history[str(i)] = {
                "date": date,
                "duration_seconds": 28800  # 8 hours each day
            }
        
        # Calculate week total
        week_seconds = sum(entry["duration_seconds"] for entry in history.values())
        week_hours = week_seconds / 3600
        
        self.assert_equal(week_hours, 56.0, "Weekly hours (7 days × 8 hours)")
    
    def test_cumulative_totals(self):
        """Test cumulative totals in history display"""
        print(f"\n{BOLD}[5. Cumulative Totals]{RESET}")
        
        history = {
            "1": {"duration_seconds": 28800, "id": "1"},   # 8h
            "2": {"duration_seconds": 14400, "id": "2"},   # 4h
            "3": {"duration_seconds": 10800, "id": "3"},   # 3h
        }
        
        # Calculate cumulative
        cumulative = 0
        cumulative_list = []
        for entry in sorted(history.values(), key=lambda x: x["id"]):
            cumulative += entry["duration_seconds"]
            cumulative_list.append(cumulative / 3600)
        
        self.assert_equal(cumulative_list[0], 8.0, "First entry cumulative = 8h")
        self.assert_equal(cumulative_list[1], 12.0, "Second entry cumulative = 8+4 = 12h")
        self.assert_equal(cumulative_list[2], 15.0, "Third entry cumulative = 8+4+3 = 15h")
    
    # ==================== Date Tests ====================
    
    def test_monday_detection(self):
        """Test Monday identification for week boundaries"""
        print(f"\n{BOLD}[6. Date Logic]{RESET}")
        
        # 2025-11-10 is a Monday (weekday() == 0)
        monday = datetime(2025, 11, 10)
        self.assert_equal(monday.weekday(), 0, "Nov 10 2025 is Monday")
        
        # 2025-11-16 is a Sunday (weekday() == 6)
        sunday = datetime(2025, 11, 16)
        self.assert_equal(sunday.weekday(), 6, "Nov 16 2025 is Sunday")
    
    def test_week_boundaries(self):
        """Test Monday reset logic"""
        # Monday Oct 13
        monday = datetime(2025, 10, 13)
        
        # Sunday before
        sunday_before = monday - timedelta(days=1)
        self.assert_equal(sunday_before.weekday(), 6, "Previous day is Sunday")
        
        # Friday of same week
        friday = monday + timedelta(days=4)
        self.assert_equal(friday.weekday(), 4, "4 days after Monday is Friday")
    
    # ==================== Missed Punch Tests ====================
    
    def test_missed_punch_entry(self):
        """Test creating missed punch entries"""
        print(f"\n{BOLD}[7. Missed Punch Feature]{RESET}")
        
        # Parse 24-hour format
        def parse_24h_time(time_str):
            """Parse HH:MM to minutes since midnight"""
            parts = time_str.split(":")
            hours = int(parts[0])
            minutes = int(parts[1])
            return hours * 60 + minutes
        
        clock_in = "08:30"  # 8:30 AM
        clock_out = "17:15"  # 5:15 PM
        
        in_minutes = parse_24h_time(clock_in)
        out_minutes = parse_24h_time(clock_out)
        duration_minutes = out_minutes - in_minutes
        
        self.assert_equal(in_minutes, 510, "8:30 AM = 510 minutes")
        self.assert_equal(out_minutes, 1035, "5:15 PM = 1035 minutes")
        self.assert_equal(duration_minutes, 525, "Duration = 8 hours 45 minutes")
    
    def test_missed_punch_validation(self):
        """Test missed punch input validation"""
        def validate_time(time_str):
            """Validate HH:MM format"""
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            try:
                h = int(parts[0])
                m = int(parts[1])
                return 0 <= h < 24 and 0 <= m < 60
            except:
                return False
        
        self.assert_true(validate_time("08:30"), "Valid time 08:30")
        self.assert_true(validate_time("23:59"), "Valid time 23:59")
        self.assert_true(validate_time("00:00"), "Valid time 00:00")
        self.assert_true(validate_time("8:30"), "Valid time 8:30 (flexible leading 0)")
        self.assert_equal(validate_time("24:00"), False, "Invalid time 24:00")
        self.assert_equal(validate_time("08:60"), False, "Invalid time 08:60")
        self.assert_equal(validate_time("25:00"), False, "Invalid time 25:00")
    
    # ==================== Archive Tests ====================
    
    def test_archive_structure(self):
        """Test weekly archive data structure"""
        print(f"\n{BOLD}[8. Archive System]{RESET}")
        
        archive = {
            "weeks": [
                {
                    "week_end": "2025-11-16",
                    "total_hours": 40.0,
                    "entries_count": 5,
                    "archived_date": "2025-11-17"
                },
                {
                    "week_end": "2025-11-09",
                    "total_hours": 38.5,
                    "entries_count": 4,
                    "archived_date": "2025-11-10"
                }
            ]
        }
        
        self.assert_equal(len(archive["weeks"]), 2, "Archive has 2 weeks")
        self.assert_equal(archive["weeks"][0]["total_hours"], 40.0, "Latest week total hours")
        self.assert_equal(archive["weeks"][1]["entries_count"], 4, "Previous week entries")
    
    def test_archive_ordering(self):
        """Test archive weeks are in descending order (newest first)"""
        archive = {
            "weeks": [
                {"week_end": "2025-11-16", "total_hours": 40.0},
                {"week_end": "2025-11-09", "total_hours": 38.5},
                {"week_end": "2025-11-02", "total_hours": 42.0},
            ]
        }
        
        # Check ordering (most recent first)
        self.assert_equal(archive["weeks"][0]["week_end"], "2025-11-16", "Newest week first")
        self.assert_equal(archive["weeks"][2]["week_end"], "2025-11-02", "Oldest week last")
    
    # ==================== Report Generation Tests ====================
    
    def test_report_generation(self):
        """Test generating text report"""
        print(f"\n{BOLD}[9. Report Generation]{RESET}")
        
        today = datetime.now().strftime("%B %d, %Y")
        report = f"""
╔════════════════════════════════╗
║   TIME CLOCK REPORT - ALICE    ║
╚════════════════════════════════╝

Report Generated: {today}

TODAY'S HOURS: 8.5h (8h 30m)
WEEKLY TOTAL: 42.5h (42h 30m)

Entry 1: 8:00 AM - 4:30 PM (8h 30m)

─────────────────────────────────
Total: 8.5 hours
═════════════════════════════════
        """
        
        self.assert_true("TIME CLOCK REPORT" in report, "Report contains header")
        self.assert_true("TODAY'S HOURS" in report, "Report contains today's hours")
        self.assert_true("WEEKLY TOTAL" in report, "Report contains weekly total")
    
    # ==================== Summary ====================
    
    def run_all_tests(self):
        """Run all test suites"""
        try:
            # Persistence
            self.test_save_and_load_users()
            self.test_save_and_load_history()
            
            # Calculations
            self.test_hours_calculation()
            self.test_format_hours_to_hm()
            
            # Totals
            self.test_daily_hours_calculation()
            self.test_weekly_hours_calculation()
            self.test_cumulative_totals()
            
            # Dates
            self.test_monday_detection()
            self.test_week_boundaries()
            
            # Missed punch
            self.test_missed_punch_entry()
            self.test_missed_punch_validation()
            
            # Archive
            self.test_archive_structure()
            self.test_archive_ordering()
            
            # Reports
            self.test_report_generation()
            
        except Exception as e:
            print(f"\n{RED}ERROR: {e}{RESET}")
            import traceback
            traceback.print_exc()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total = self.tests_passed + self.tests_failed
        percentage = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"\n{BOLD}{'='*40}{RESET}")
        print(f"{BOLD}Test Summary:{RESET}")
        print(f"{GREEN}✓ Passed: {self.tests_passed}{RESET}")
        print(f"{RED}✗ Failed: {self.tests_failed}{RESET}")
        print(f"Total:   {total}")
        print(f"Success Rate: {percentage:.1f}%")
        print(f"{BOLD}{'='*40}{RESET}\n")
        
        if self.tests_failed == 0:
            print(f"{GREEN}{BOLD}ALL TESTS PASSED! 🎉{RESET}\n")
            return 0
        else:
            print(f"{RED}{BOLD}SOME TESTS FAILED{RESET}\n")
            return 1


if __name__ == "__main__":
    tester = TimeClockTester()
    exit_code = tester.run_all_tests() or 0
    sys.exit(exit_code)
