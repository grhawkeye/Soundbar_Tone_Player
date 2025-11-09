__file__ = "soundbar_tone_player.py"
__author__ = "Nikolaos Ntouroutlis"
__license__ = "MIT License"
__version__ = "1.0.0"
__status__ = "Production"

"""
Soundbar Tone Player - System Tray Application
Plays audio files (WAV/MP3) at regular intervals
Reads configuration from player_settings.json
"""
import json
import time
import os
import sys
import threading
from pathlib import Path
import sounddevice as sd
import soundfile as sf
import pystray
from PIL import Image, ImageDraw
import winreg


class TonePlayer:
    def __init__(self, settings_file="player_settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()
        self.running = False
        self.timer_thread = None
        self.icon = None
    
    def get_base_path(self):
        """Get the base path for the application (works for both .py and .exe)"""
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            return Path(sys.executable).parent
        else:
            # Running as script
            return Path(__file__).parent
        
    def load_settings(self):
        """Load settings from JSON file"""
        settings_path = self.get_base_path() / self.settings_file
        
        if not settings_path.exists():
            # Create default settings
            default_settings = {
                "tone_file": "tone.wav",
                "interval_minutes": 10
            }
            with open(settings_path, 'w') as f:
                json.dump(default_settings, f, indent=4)
            self.log(f"Created default settings file: {settings_path}")
            return default_settings
        
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        return settings
    
    def get_audio_path(self):
        """Get the full path to the audio file"""
        tone_file = self.settings.get("tone_file", "tone.wav")
        audio_path = self.get_base_path() / tone_file
        return audio_path
    
    def log(self, message, end="\n"):
        """Log message to console (if available)"""
        try:
            print(message, end=end, flush=True)
        except:
            pass  # Suppress errors when running without console
    
    def play_audio(self):
        """Play the configured audio file (supports WAV and MP3)"""
        try:
            audio_path = self.get_audio_path()
            
            if not audio_path.exists():
                self.log(f"❌ Audio file not found: {audio_path}")
                if self.icon:
                    self.icon.notify("Error", f"Audio file not found: {audio_path.name}")
                return False
            
            self.log(f"🔊 Playing: {audio_path.name} ... ", end="")
            
            # Load audio file
            try:
                data, samplerate = sf.read(str(audio_path))
                
                # Play the audio
                sd.play(data, samplerate)
                sd.wait()  # Wait until playback is finished
                
                self.log(f"✓ Played at {time.strftime('%H:%M:%S')}")
                return True
                
            except RuntimeError as e:
                self.log(f"\n❌ Error: {e}")
                if self.icon:
                    self.icon.notify("Playback Error", "Could not play audio file")
                return False
            
        except Exception as e:
            self.log(f"\n❌ Error playing audio: {e}")
            if self.icon:
                self.icon.notify("Error", str(e))
            return False
    
    def timer_loop(self):
        """Background loop that plays tone at intervals"""
        while self.running:
            interval_minutes = self.settings.get("interval_minutes", 10)
            interval_seconds = interval_minutes * 60
            
            self.play_audio()
            
            # Sleep in small intervals to allow for quick shutdown
            for _ in range(int(interval_seconds)):
                if not self.running:
                    break
                time.sleep(1)
    
    def start_timer(self):
        """Start the timer loop"""
        if not self.running:
            self.running = True
            self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
            self.timer_thread.start()
            self.log("✅ Started tone player timer")
            if self.icon:
                interval = self.settings.get("interval_minutes", 10)
                self.icon.notify("Tone Player Started", f"Playing every {interval} minute(s)")
    
    def stop_timer(self):
        """Stop the timer loop"""
        if self.running:
            self.running = False
            if self.timer_thread:
                self.timer_thread.join(timeout=2)
            self.log("🛑 Stopped tone player timer")
    
    def set_interval(self, minutes):
        """Set the interval and save to settings"""
        self.settings["interval_minutes"] = minutes
        self.save_settings()
        
        # Restart timer with new interval
        was_running = self.running
        if was_running:
            self.stop_timer()
            time.sleep(0.5)
            self.start_timer()
        else:
            # Update menu to show new setting
            if self.icon:
                self.icon.menu = self.create_menu()
        
        if self.icon:
            self.icon.notify("Interval Updated", f"Now playing every {minutes} minute(s)")
    
    def save_settings(self):
        """Save current settings to JSON file"""
        settings_path = self.get_base_path() / self.settings_file
        with open(settings_path, 'w') as f:
            json.dump(self.settings, f, indent=4)
    
    def open_settings_file(self):
        """Open the settings JSON file in default editor"""
        settings_path = self.get_base_path() / self.settings_file
        try:
            os.startfile(str(settings_path))
            if self.icon:
                self.icon.notify("Settings Opened", "Edit and save, then restart the app")
        except Exception as e:
            self.log(f"Error opening settings file: {e}")
    
    def get_startup_key(self):
        """Get the Windows registry key for startup programs"""
        return r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    def is_startup_enabled(self):
        """Check if the app is set to start with Windows"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.get_startup_key(), 0, winreg.KEY_READ)
            try:
                winreg.QueryValueEx(key, "SoundbarTonePlayer")
                winreg.CloseKey(key)
                return True
            except WindowsError:
                winreg.CloseKey(key)
                return False
        except:
            return False
    
    def toggle_startup(self, item=None):
        """Toggle startup with Windows"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.get_startup_key(), 0, winreg.KEY_ALL_ACCESS)
            
            if self.is_startup_enabled():
                # Remove from startup
                try:
                    winreg.DeleteValue(key, "SoundbarTonePlayer")
                    self.log("Removed from Windows startup")
                    if self.icon:
                        self.icon.notify("Startup Disabled", "App will not start with Windows")
                except:
                    pass
            else:
                # Add to startup
                script_path = str(Path(__file__).resolve())
                python_exe = sys.executable
                # Use pythonw.exe to run without console window
                python_no_console = python_exe.replace("python.exe", "pythonw.exe")
                if os.path.exists(python_no_console):
                    python_exe = python_no_console
                startup_command = f'"{python_exe}" "{script_path}"'
                winreg.SetValueEx(key, "SoundbarTonePlayer", 0, winreg.REG_SZ, startup_command)
                self.log("Added to Windows startup")
                if self.icon:
                    self.icon.notify("Startup Enabled", "App will start with Windows")
            
            winreg.CloseKey(key)
            
            # Update menu
            if self.icon:
                self.icon.menu = self.create_menu()
                
        except Exception as e:
            self.log(f"Error toggling startup: {e}")
            if self.icon:
                self.icon.notify("Error", "Could not modify startup settings")
    
    def create_icon_image(self):
        """Create a simple icon for the system tray"""
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Draw speaker shape
        draw.rectangle([10, 20, 25, 44], fill='black')
        draw.polygon([25, 20, 40, 10, 40, 54, 25, 44], fill='black')
        
        # Draw sound waves
        draw.arc([42, 25, 52, 39], 270, 90, fill='black', width=2)
        draw.arc([45, 20, 57, 44], 270, 90, fill='black', width=2)
        
        return image
    
    def on_play_now(self, icon, item):
        """Handle play now menu item"""
        threading.Thread(target=self.play_audio, daemon=True).start()
    
    def on_set_interval_3(self, icon, item):
        """Set interval to 3 minutes"""
        self.set_interval(3)
    
    def on_set_interval_5(self, icon, item):
        """Set interval to 5 minutes"""
        self.set_interval(5)
    
    def on_set_interval_10(self, icon, item):
        """Set interval to 10 minutes"""
        self.set_interval(10)
    
    def on_set_custom_interval(self, icon, item):
        """Open settings file for custom interval"""
        self.open_settings_file()
    
    def on_quit(self, icon, item):
        """Handle quit menu item"""
        self.stop_timer()
        icon.stop()
    
    def create_menu(self):
        """Create the system tray menu"""
        startup_text = "✓ Start with Windows" if self.is_startup_enabled() else "Start with Windows"
        current_interval = self.settings.get("interval_minutes", 10)
        
        return pystray.Menu(
            pystray.MenuItem(startup_text, self.toggle_startup),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Play Now", self.on_play_now),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Interval",
                pystray.Menu(
                    pystray.MenuItem(
                        f"{'• ' if current_interval == 3 else ''}Every 3 minutes",
                        self.on_set_interval_3
                    ),
                    pystray.MenuItem(
                        f"{'• ' if current_interval == 5 else ''}Every 5 minutes",
                        self.on_set_interval_5
                    ),
                    pystray.MenuItem(
                        f"{'• ' if current_interval == 10 else ''}Every 10 minutes",
                        self.on_set_interval_10
                    ),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("Set Custom Interval...", self.on_set_custom_interval)
                )
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.on_quit)
        )
    
    def run_systray(self):
        """Run the system tray application"""
        # Create the icon
        icon_image = self.create_icon_image()
        
        # Create menu
        menu = self.create_menu()
        
        # Create and run the system tray icon
        self.icon = pystray.Icon("soundbar_tone_player", icon_image, "Soundbar Tone Player", menu)
        
        # Automatically start the timer when app launches
        self.start_timer()
        
        # Run the icon (this blocks until quit)
        self.icon.run()
    
    def test_play(self):
        """Test play the audio once"""
        print("=" * 60)
        print("🧪 Testing Audio Playback")
        print("=" * 60)
        print(f"📁 Audio file: {self.settings.get('tone_file')}")
        print()
        
        success = self.play_audio()
        
        print()
        if success:
            print("✅ Test successful!")
        else:
            print("❌ Test failed - check the error messages above")
        print("=" * 60)


def main():
    """Main entry point"""
    player = TonePlayer()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--test', '-t']:
            player.test_play()
            return
        elif sys.argv[1] in ['--help', '-h']:
            print("""
Soundbar Tone Player - System Tray Application

Usage:
  python tone_player.py          Run in system tray (background)
  python tone_player.py --test   Test play once and exit
  python tone_player.py --help   Show this help message

Features:
  - Runs in Windows system tray
  - Right-click menu for all controls
  - Quick interval presets (3, 5, 10 minutes)
  - Custom interval via settings file
  - Start with Windows option
  - Play on demand

Configuration:
  Right-click the system tray icon and select:
  - "Interval" → Choose preset or custom
  - "Set Custom Interval..." opens player_settings.json

Supported formats:
  - WAV: Full support
  - MP3: Basic support

System Tray Menu:
  - Start with Windows  (Toggle startup)
  - Play Now            (Play immediately)
  - Interval            (Set 3, 5, 10 min or custom)
  - Exit                (Close application)
            """)
            return
    
    # Run the system tray application
    player.run_systray()


if __name__ == "__main__":
    main()
