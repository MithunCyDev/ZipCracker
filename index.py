import os
import zipfile
import rarfile
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading  # Import threading for background tasks

# Function to try and extract the ZIP or RAR file using the given password
def try_file_password(file_path, password):
    try:
        if file_path.endswith(".zip"):
            return try_zip_password(file_path, password)
        elif file_path.endswith(".rar"):
            return try_rar_password(file_path, password)
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Function to try and extract ZIP file
def try_zip_password(zip_file, password):
    try:
        with zipfile.ZipFile(zip_file, 'r') as zf:
            zf.setpassword(password.encode('utf-8'))  # Ensure utf-8 encoding for password
            zf.testzip()  # Test for password correctness
            # If no exception was raised, the password is correct
            return True
    except RuntimeError:
        return False  # Password incorrect
    except zipfile.BadZipFile:
        return False  # Not a valid ZIP file

# Function to try and extract RAR file
def try_rar_password(rar_file, password):
    try:
        with rarfile.RarFile(rar_file) as rf:
            rf.setpassword(password)  # Set password
            rf.test()  # Test the password
            return True
    except rarfile.BadRarFile:
        return False  # Not a valid RAR file
    except rarfile.RarWrongPassword:
        return False  # Wrong password
    except Exception as e:
        print(f"Error while handling RAR file: {e}")
        return False

# Function to prompt user to select a file
def select_file():
    file_path = filedialog.askopenfilename(
        title="Select ZIP or RAR File", 
        filetypes=[("All Files", "*.*"), ("ZIP files", "*.zip"), ("RAR files", "*.rar")]
    )
    return file_path

# GUI Setup
class FilePasswordCrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Password Cracker")
        self.root.geometry("450x400")
        self.root.config(bg="black")  # Set background to black

        self.file_path = None

        # Label for instructions
        self.instruction_label = tk.Label(self.root, text="Select a ZIP or RAR file to attempt password recovery.", fg="red", bg="black", font=("Arial", 12))
        self.instruction_label.pack(pady=10)

        # Button to select the ZIP or RAR file
        self.select_file_button = tk.Button(self.root, text="Select File", command=self.load_file, bg="red", fg="white", font=("Arial", 12))
        self.select_file_button.pack(pady=5)

        # Label to show selected file
        self.selected_file_label = tk.Label(self.root, text="No file selected", fg="red", bg="black", font=("Arial", 10))
        self.selected_file_label.pack(pady=5)

        # Button to find the password from dictionary
        self.find_password_button = tk.Button(self.root, text="Find Password from Dictionary", command=self.start_find_password_thread, bg="red", fg="white", font=("Arial", 12))
        self.find_password_button.pack(pady=10)

        # Text area to display results
        self.result_text = tk.Text(self.root, height=6, width=40, bg="black", fg="red", font=("Arial", 10))
        self.result_text.pack(pady=10)

        # Button to clear results
        self.clear_button = tk.Button(self.root, text="Clear", command=self.clear_results, bg="red", fg="white", font=("Arial", 12))
        self.clear_button.pack(pady=5)

    # Load the file (ZIP or RAR)
    def load_file(self):
        self.file_path = select_file()
        if self.file_path:
            if not (self.file_path.endswith(".zip") or self.file_path.endswith(".rar")):
                messagebox.showerror("Invalid File Type", "Please select a valid ZIP or RAR file.")
                self.selected_file_label.config(text="No valid file selected")
                self.file_path = None  # Reset file path
                return
            self.selected_file_label.config(text=f"Selected file: {self.file_path}")
        else:
            self.selected_file_label.config(text="No file selected")

    # Function to find password from dictionary (run in a separate thread)
    def start_find_password_thread(self):
        if not self.file_path:
            messagebox.showwarning("No File", "Please select a file first.")
            return
        
        # Disable the button and change its text to "Searching..."
        self.find_password_button.config(state="disabled", text="Searching...")

        # Clear previous results
        self.result_text.delete(1.0, tk.END)

        # Start a new thread to search for the password in the dictionary
        password_search_thread = threading.Thread(target=self.find_password_from_dict)
        password_search_thread.start()

    # Function to search for password from dictionary
    def find_password_from_dict(self):
        try:
            with open("dictionary.txt", "r", encoding="utf-8") as file:
                passwords = file.readlines()

            # Try each password from the dictionary
            for password in passwords:
                password = password.strip()  # Remove any leading/trailing whitespaces

                if try_file_password(self.file_path, password):
                    self.result_text.insert(tk.END, f"Password found: {password}\n")
                    self.result_text.insert(tk.END, "You can now extract the file.")
                    break  # Exit the loop once the correct password is found

            else:
                # If no password is found
                self.result_text.insert(tk.END, "Password not found in dictionary.\n")
                self.result_text.insert(tk.END, "Try adding more passwords to the dictionary.")

        except FileNotFoundError:
            messagebox.showerror("File Not Found", "The dictionary.txt file is missing.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

        # Re-enable the button and restore the original text after the search
        self.find_password_button.config(state="normal", text="Find Password from Dictionary")

    # Clear the result text area
    def clear_results(self):
        self.result_text.delete(1.0, tk.END)

# Main function to run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = FilePasswordCrackerApp(root)
    root.mainloop()
