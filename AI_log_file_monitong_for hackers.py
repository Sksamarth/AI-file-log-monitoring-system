import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import winsound
from openai import OpenAI

class ModernLogMonitor:
    def __init__(self, master):
        self.master = master
        master.title("DEEPEYE - Log Security Monitor")
        master.geometry("1000x700")
        master.configure(bg='#1e2738')

        # Initialize log_file_path FIRST
        self.log_file_path = os.path.join(os.path.dirname(__file__), "server_log.txt")

        # Custom style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Custom color scheme
        self.bg_color = '#1e2738'  # Deep blue-gray background
        self.primary_color = '#4a90e2'  # Bright blue
        self.secondary_color = '#2c3e50'  # Dark blue-gray
        self.text_color = '#f0f4f8'  # Light text
        self.accent_color = '#2ecc71'  # Green for positive actions

        # Configure styles
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', 
            background=self.bg_color, 
            foreground=self.primary_color, 
            font=('Segoe UI', 12, 'normal')
        )
        self.style.configure('Title.TLabel', 
            background=self.bg_color, 
            foreground=self.text_color, 
            font=('Segoe UI', 20, 'bold')
        )
        self.style.configure('TButton', 
            background=self.secondary_color, 
            foreground=self.primary_color, 
            font=('Segoe UI', 12, 'bold'),
            padding=10
        )
        self.style.map('TButton',
            background=[('active', self.primary_color), ('disabled', '#4a4a4a')],
            foreground=[('active', self.text_color), ('disabled', '#7f8c8d')]
        )

        # Ensure log file exists
        self.ensure_log_file()

        # Main container
        self.main_frame = ttk.Frame(master, style='TFrame')
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Title
        self.title_label = ttk.Label(
            self.main_frame, 
            text="DEEPEYE - Log Security Monitor", 
            style='Title.TLabel'
        )
        self.title_label.pack(pady=(0, 30))

        # Status and Information Frame
        info_frame = ttk.Frame(self.main_frame, style='TFrame')
        info_frame.pack(fill=tk.X, pady=10)

        # Status Display
        self.status_var = tk.StringVar(value="Not Monitoring")
        self.status_label = ttk.Label(
            info_frame, 
            textvariable=self.status_var,
            font=('Segoe UI', 12, 'bold')
        )
        self.status_label.pack(side=tk.LEFT)

        # File Size Display
        self.file_size_var = tk.StringVar(value="File Size: 0 bytes")
        self.file_size_label = ttk.Label(
            info_frame, 
            textvariable=self.file_size_var
        )
        self.file_size_label.pack(side=tk.RIGHT)

        # AI Response Display with improved styling
        self.response_text = tk.Text(
            self.main_frame, 
            height=20, 
            width=100, 
            bg=self.secondary_color,  
            fg=self.primary_color,  
            insertbackground=self.primary_color,  
            selectbackground='#34495e',  
            font=('Consolas', 11),
            borderwidth=2,
            relief=tk.FLAT
        )
        self.response_text.pack(pady=15)

        # Configure tags for different text styles
        self.response_text.tag_configure('new_entry', 
            foreground='white', 
            font=('Segoe UI', 14, 'bold'),
            justify='center'
        )

        # Configure additional tags for AI response
        self.response_text.tag_configure('ai_response', 
            foreground='#2ecc71',  # Bright green for AI responses
            font=('Segoe UI', 12, 'normal'),
            spacing1=5,
            spacing3=5,
            lmargin1=10,
            lmargin2=10
        )
        
        self.response_text.tag_configure('ai_header', 
            foreground='#4a90e2',  # Bright blue for AI header
            font=('Segoe UI', 14, 'bold'),
            justify='center',
            spacing1=10,
            spacing3=10
        )

        # Button Frame with improved layout
        button_frame = ttk.Frame(self.main_frame, style='TFrame')
        button_frame.pack(pady=10)

        # Start Button
        self.start_button = ttk.Button(
            button_frame, 
            text="Start Monitoring", 
            command=self.start_monitoring,
            style='TButton'
        )
        self.start_button.pack(side=tk.LEFT, padx=15)

        # Stop Button
        self.stop_button = ttk.Button(
            button_frame, 
            text="Stop Monitoring", 
            command=self.stop_monitoring,
            style='TButton',
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=15)

        # Monitoring thread and event
        self.monitoring_thread = None
        self.is_monitoring = False

        # OpenAI client setup
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )

    def ensure_log_file(self):
        """Ensure the log file exists, creating it if necessary."""
        try:
            # Create the file if it doesn't exist
            if not os.path.exists(self.log_file_path):
                with open(self.log_file_path, 'w') as f:
                    f.write("Log file created at " + time.ctime() + "\n")
                print(f"Created log file at {self.log_file_path}")
        except Exception as e:
            print(f"Error creating log file: {e}")
            # Fallback to a temporary file if directory is not writable
            try:
                self.log_file_path = os.path.join(os.path.expanduser('~'), "server_log.txt")
                with open(self.log_file_path, 'w') as f:
                    f.write("Log file created at " + time.ctime() + "\n")
                print(f"Created log file at {self.log_file_path}")
            except Exception as fallback_error:
                print(f"Fallback log file creation failed: {fallback_error}")
                # Last resort: use a fixed path
                self.log_file_path = "C:\\temp\\server_log.txt"
                os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
                with open(self.log_file_path, 'w') as f:
                    f.write("Log file created at " + time.ctime() + "\n")

    def log_response(self, message, is_new_entry=False, is_ai_response=False, is_ai_header=False):
        """Log a response message to the text area with improved display."""
        self.master.after(0, self._update_response_text, message, is_new_entry, is_ai_response, is_ai_header)

    def _update_response_text(self, message, is_new_entry=False, is_ai_response=False, is_ai_header=False):
        """Update the response text area with enhanced formatting."""
        if is_new_entry:
            # Insert new entry with prominent styling
            self.response_text.insert(tk.END, message + "\n", 'new_entry')
        elif is_ai_header:
            # Insert AI header with centered, blue styling
            self.response_text.insert(tk.END, "\n" + message + "\n", 'ai_header')
        elif is_ai_response:
            # Insert AI response with green styling and padding
            self.response_text.insert(tk.END, message, 'ai_response')
        else:
            # Insert regular message
            self.response_text.insert(tk.END, message + "\n")
        
        self.response_text.see(tk.END)

    def update_file_size(self, size):
        """Update the file size display."""
        self.file_size_var.set(f"File Size: {size} bytes")

    def play_alert_sound(self):
        """Play an alert sound."""
        freqs = [800, 1000, 1200, 1400, 1600]
        for _ in range(3):
            for freq in freqs:
                try:
                    winsound.Beep(freq, 700)
                    time.sleep(0.2)
                except RuntimeError:
                    self.log_response("Warning: Sound playback failed.")

    def read_last_n_chars(self, filename, min_chars=100, max_chars=200):
        """Read the last N characters from a file."""
        try:
            with open(filename, 'rb') as file:
                file.seek(0, 2)
                file_size = file.tell()
                start_pos = max(0, file_size - max_chars)
                file.seek(start_pos)
                content = file.read().decode(errors='ignore')
                return content[-min_chars:]
        except Exception as e:
            self.log_response(f"Error reading file: {e}")
            return ""

    def analyze_with_ai(self, text):
        """Analyze text with AI for potential security risks."""
        try:
            # Log AI analysis start
            self.log_response("🤖 AI Security Analysis", is_ai_header=True)
            
            stream = self.client.chat.completions.create(
                model="deepseek/deepseek-r1-zero:free",
                messages=[
                    {"role": "system", "content": "You are monitoring a system log for security risks."},
                    {"role": "user", "content": f"{text} Only respond with 'Yes' or 'No'.if there is any useful information for hackers then only explain other vice say no only in this context in 20 to max 100 words."}
                ],
                stream=True
            )
            response_text = ""
            for chunk in stream:
                if chunk.choices:
                    chunk_content = chunk.choices[0].delta.content or ""
                    response_text += chunk_content
                    # Stream each chunk with AI response styling
                    self.log_response(chunk_content, is_ai_response=True)
            
            # Log the full AI response after streaming
            full_response = response_text.strip()
            
            return full_response
        except Exception as e:
            self.log_response(f"AI Analysis error: {e}", is_ai_response=True)
            return "No"

    def monitoring_loop(self):
        """Main monitoring loop."""
        check_interval = 1
        alert_interval = 1800

        try:
            # Ensure file exists before starting
            self.ensure_log_file()
            
            last_size = os.path.getsize(self.log_file_path)
            last_update_time = time.time()
            last_alert_time = time.time()

            while self.is_monitoring:
                time.sleep(check_interval)
                
                try:
                    new_size = os.path.getsize(self.log_file_path)
                    # Update file size on main thread
                    self.master.after(0, self.update_file_size, new_size)
                except FileNotFoundError:
                    # Recreate the file if it's deleted
                    self.ensure_log_file()
                    new_size = 0
                    self.log_response(f"File {self.log_file_path} was recreated.")

                if new_size > last_size:
                    # Get only the new part of the log
                    log_update = self.read_last_n_chars(self.log_file_path)
                    
                    # Log the new entry with large white font
                    self.log_response(f"🚨 NEW LOG ENTRY DETECTED 🚨", is_new_entry=True)
                    self.log_response("New Log Content:", is_new_entry=True)
                    self.log_response(log_update, is_new_entry=True)
                    
                    ai_response = self.analyze_with_ai(log_update)
                    
                    if "yes" in ai_response.lower():
                        self.log_response("*** Security Alert: Potential sensitive information detected! ***", is_new_entry=True)
                        self.play_alert_sound()

                    last_size = new_size
                    last_update_time = time.time()

                # Periodic alert
                if time.time() - last_update_time >= alert_interval and \
                   time.time() - last_alert_time >= alert_interval:
                    self.play_alert_sound()
                    last_alert_time = time.time()

        except Exception as e:
            self.log_response(f"Monitoring error: {e}")
        finally:
            self.master.after(0, self.stop_monitoring)

    def start_monitoring(self):
        """Start the monitoring process."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
            self.monitoring_thread.daemon = True  # Ensure thread exits when main program closes
            self.monitoring_thread.start()

            # Update UI
            self.status_var.set("Monitoring Active")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log_response(f"Monitoring started.")

    def stop_monitoring(self):
        """Stop the monitoring process."""
        if self.is_monitoring:
            self.is_monitoring = False
            
            # Reset UI
            self.status_var.set("Not Monitoring")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log_response("Monitoring stopped.")

def main():
    root = tk.Tk()
    root.configure(bg='#1e2738')
    app = ModernLogMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()