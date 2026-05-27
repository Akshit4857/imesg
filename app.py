import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time
import random
import os
import re

# 1. Spintax Logic
def process_spintax(message):
    return re.sub(r'\{([^{}]*)\}', lambda m: random.choice(m.group(1).split('|')), message)

# 2. Optimized Blue/Green Check (Better Version)
def is_imessage(number):
    script = f'''
    tell application "Messages"
        set iMessageService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{number}" of iMessageService
        return "true"
    end tell
    '''
    try:
        result = os.popen(f"osascript -e '{script}'").read().strip()
        return result == "true"
    except:
        return False

# 3. Message Sender with UI Scripting
def send_message(number, message):
    final_msg = process_spintax(message)
    # This AppleScript simulates human typing, checks the color visually, and then sends.
    script = f'''
    tell application "Messages" to activate
    delay 0.5
    tell application "System Events"
        -- 1. Press Cmd+N for New Message
        keystroke "n" using command down
        delay 1
        
        -- 2. Human Typewriter effect for the number
        set theNumber to "{number}"
        repeat with char in theNumber
            keystroke char
            delay (random number from 0.05 to 0.15)
        end repeat
        delay 0.5
        
        -- 3. Press Return to confirm the number
        key code 36
        
        -- 4. Wait for the blue/green check logic to visually appear
        delay 2.5
        
        -- Press Tab to move cursor from the "To:" field to the Message Body field
        key code 48
        delay 0.5
        
        -- 5. Type the message (Typewriter effect for the body too!)
        set theMessage to "{final_msg}"
        repeat with msgChar in theMessage
            keystroke msgChar
            delay (random number from 0.02 to 0.1)
        end repeat
        delay 1
        
        -- 6. Press Return to Send
        key code 36
    end tell
    '''
    os.system(f"osascript -e '{script}'")
    print(f"Sent to {number}")

class IMessageSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("iMessage Factory Agent")
        self.root.geometry("600x750")
        
        self.running = False
        self.msg_count = 0

        # UI Layout
        tk.Label(root, text="Phone Numbers (+91xxxxxxxxx):").pack(pady=5)
        self.numbers_input = scrolledtext.ScrolledText(root, height=10, width=60)
        self.numbers_input.pack(pady=5)
        
        tk.Label(root, text="Message Template:").pack(pady=5)
        self.template_input = scrolledtext.ScrolledText(root, height=5, width=60)
        self.template_input.pack(pady=5)
        
        # Delay Inputs
        delay_frame = tk.Frame(root)
        delay_frame.pack(pady=10)
        
        tk.Label(delay_frame, text="Min Delay (sec):").grid(row=0, column=0, padx=5)
        self.min_delay_entry = tk.Entry(delay_frame, width=5)
        self.min_delay_entry.insert(0, "3")
        self.min_delay_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(delay_frame, text="Max Delay (sec):").grid(row=0, column=2, padx=5)
        self.max_delay_entry = tk.Entry(delay_frame, width=5)
        self.max_delay_entry.insert(0, "4")
        self.max_delay_entry.grid(row=0, column=3, padx=5)
        
        self.run_btn = tk.Button(root, text="Start Sending", font=("Arial", 14), command=self.start_thread)
        self.run_btn.pack(pady=10)
        
        self.logs = scrolledtext.ScrolledText(root, height=15, width=60, state='disabled')
        self.logs.pack(pady=5)

    def log(self, msg):
        self.logs.config(state='normal')
        self.logs.insert(tk.END, msg + "\n")
        self.logs.see(tk.END)
        self.logs.config(state='disabled')

    def start_thread(self):
        try:
            min_delay = float(self.min_delay_entry.get())
            max_delay = float(self.max_delay_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Delays must be numbers.")
            return
            
        threading.Thread(target=self.run_loop, args=(min_delay, max_delay), daemon=True).start()

    def update_numbers_ui(self, remaining):
        self.numbers_input.delete("1.0", tk.END)
        self.numbers_input.insert(tk.END, "\n".join(remaining))

    def run_loop(self, min_delay, max_delay):
        numbers = [n.strip() for n in self.numbers_input.get("1.0", tk.END).split('\n') if n.strip()]
        template = self.template_input.get("1.0", tk.END).strip()
        
        remaining_numbers = list(numbers)
        for num in numbers:
            # Purge Logic (Har 200 msg pe clean)
            if self.msg_count >= 200:
                self.log("Limit hit. Purging Database...")
                os.system("killall Messages && rm -rf ~/Library/Messages/chat.db* && sleep 5")
                self.msg_count = 0
            
            self.log(f"Checking {num}...")
            if is_imessage(num):
                self.log(f"Verified iMessage. Sending...")
                send_message(num, template)
                self.log(f"SUCCESS: Sent message to {num}")
                self.msg_count += 1
                
                # Apply the user-defined delay
                delay = random.uniform(min_delay, max_delay)
                self.log(f"Waiting for {delay:.1f} seconds before next...")
                time.sleep(delay) 
            else:
                self.log(f"SKIPPED: {num} (Not iMessage)")
                
            # Remove the processed number from UI
            remaining_numbers.remove(num)
            self.root.after(0, self.update_numbers_ui, remaining_numbers)
        
        self.log("--- Batch Finished ---")

if __name__ == "__main__":
    root = tk.Tk()
    app = IMessageSenderApp(root)
    root.mainloop()