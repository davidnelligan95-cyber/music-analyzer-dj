import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import random
import math

class SeratoDeck:
    """Serato DJ style deck with circular BPM display and hot cues"""
    def __init__(self, parent, deck_number, deck_name):
        self.deck_number = deck_number
        self.deck_name = deck_name
        self.is_playing = False
        self.current_track = None # Stores the filename
        self.full_track_path = None # Stores the full path for loading
        self.bpm = 127.0
        self.pitch = 0.0
        self.setup_ui(parent)
    
    def setup_ui(self, parent):
        # Main deck frame
        self.frame = tk.Frame(parent, bg='#1a1a1a', highlightbackground='#444', highlightthickness=1)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Deck header
        header = tk.Frame(self.frame, bg='#0a0a0a', height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text=str(self.deck_number), font=("Arial", 20, "bold"),
                fg="white", bg='#0a0a0a').pack(side=tk.LEFT, padx=10)
        
        # Track info
        track_info = tk.Frame(header, bg='#0a0a0a')
        track_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.track_name_label = tk.Label(track_info, text=self.deck_name, 
                                         font=("Arial", 11, "bold"),
                                         fg="white", bg='#0a0a0a', anchor=tk.W)
        self.track_name_label.pack(fill=tk.X, padx=5)
        
        self.track_artist_label = tk.Label(track_info, text="Atomic Load", 
                                          font=("Arial", 9),
                                          fg="#999", bg='#0a0a0a', anchor=tk.W)
        self.track_artist_label.pack(fill=tk.X, padx=5)
        
        # BPM and time display
        bpm_time_frame = tk.Frame(header, bg='#0a0a0a')
        bpm_time_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Label(bpm_time_frame, text=str(int(self.bpm)), 
                font=("Arial", 16, "bold"), fg="#00ff00", bg='#0a0a0a').pack()
        
        self.time_label = tk.Label(bpm_time_frame, text="04:14.90",
                                   font=("Courier", 10), fg="white", bg='#0a0a0a')
        self.time_label.pack()
        
        # Hot cues section
        hotcue_frame = tk.Frame(self.frame, bg='#1a1a1a')
        hotcue_frame.pack(fill=tk.X, padx=5, pady=5)
        
        cue_colors = ['#ff0000', '#0000ff', '#00ff00', '#ffff00'] # Red, Blue, Green, Yellow
        for i in range(1, 5):
            cue_btn = tk.Button(hotcue_frame, text=str(i), font=("Arial", 10, "bold"),
                               bg=cue_colors[i-1], fg='black', width=4, height=2,
                               relief=tk.FLAT, command=lambda x=i: self.set_hotcue(x))
            cue_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Button(hotcue_frame, text="X", font=("Arial", 10, "bold"),
                 bg='#666', fg='white', width=4, height=2,
                 relief=tk.FLAT, command=self.clear_hotcues).pack(side=tk.LEFT, padx=2)
        
        # Circular BPM display (Serato style)
        bpm_display_frame = tk.Frame(self.frame, bg='#1a1a1a', height=180)
        bpm_display_frame.pack(fill=tk.X, padx=5, pady=10)
        bpm_display_frame.pack_propagate(False)
        
        self.bpm_canvas = tk.Canvas(bpm_display_frame, bg='#0a0a0a', 
                                    width=160, height=160, highlightthickness=0)
        self.bpm_canvas.pack(expand=True)
        self.draw_circular_bpm()
        
        # Transport controls
        transport = tk.Frame(self.frame, bg='#1a1a1a')
        transport.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(transport, text="SYNC", font=("Arial", 8, "bold"),
                 bg='#0066cc', fg='white', width=6, relief=tk.FLAT,
                 command=self.sync).pack(side=tk.LEFT, padx=2)
        
        tk.Button(transport, text="◀◀", font=("Arial", 10),
                 bg='#333', fg='white', width=4, relief=tk.FLAT,
                 command=self.rewind).pack(side=tk.LEFT, padx=2)
        
        self.play_btn = tk.Button(transport, text="▶", font=("Arial", 14, "bold"),
                                  bg='#00ff00', fg='black', width=4, height=2,
                                  relief=tk.FLAT, command=self.toggle_play)
        self.play_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Button(transport, text="▶▶", font=("Arial", 10),
                 bg='#333', fg='white', width=4, relief=tk.FLAT,
                 command=self.fast_forward).pack(side=tk.LEFT, padx=2)
        
        # Loop controls
        loop_frame = tk.Frame(self.frame, bg='#1a1a1a')
        loop_frame.pack(fill=tk.X, padx=5, pady=5)
        
        for loop_size in ['1/8', '1/4', '1/2', '1', '2', '4', '8', '16']:
            tk.Button(loop_frame, text=loop_size, font=("Arial", 7),
                     bg='#333', fg='white', width=3, height=1,
                     relief=tk.FLAT).pack(side=tk.LEFT, padx=1)
        
        # FX and cue buttons
        fx_frame = tk.Frame(self.frame, bg='#1a1a1a')
        fx_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(fx_frame, text="CUE", font=("Arial", 10, "bold"),
                 bg='#ff6600', fg='white', width=8, height=2,
                 relief=tk.FLAT, command=self.cue).pack(side=tk.LEFT, padx=2)
        
        tk.Button(fx_frame, text="📁 LOAD", font=("Arial", 9, "bold"),
                 bg='#0066cc', fg='white', width=8, height=2,
                 relief=tk.FLAT, command=self.load_track_dialog).pack(side=tk.RIGHT, padx=2)
    
    def draw_circular_bpm(self):
        """Draw Serato-style circular BPM display"""
        self.bpm_canvas.delete("all")
        
        cx, cy = 80, 80
        radius = 70
        
        # Outer circle
        self.bpm_canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius,
                                    outline='#444', width=3)
        
        # BPM text
        self.bpm_canvas.create_text(cx, cy-20, text=f"{self.bpm:.1f}",
                                   font=("Arial", 24, "bold"), fill='white')
        
        # Pitch percentage
        pitch_text = f"{self.pitch:+.1f}%"
        self.bpm_canvas.create_text(cx, cy+10, text=pitch_text,
                                   font=("Arial", 12), fill='#00ff00')
        
        # Time display (simulated)
        self.bpm_canvas.create_text(cx, cy+35, text="01:19.4",
                                   font=("Courier", 11), fill='white')
        self.bpm_canvas.create_text(cx, cy+50, text="02:55.5",
                                   font=("Courier", 11), fill='#666')
    
    def load_track_dialog(self):
        """Open file dialog to load a track"""
        file_path = filedialog.askopenfilename(
            title=f"Load Track - Deck {self.deck_number}",
            filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.m4a")]
        )
        if file_path:
            self.load_track(file_path)

    def load_track(self, file_path):
        """Load track and update deck display"""
        self.full_track_path = file_path
        self.current_track = os.path.basename(file_path)
        self.track_name_label.config(text=self.current_track[:25]) # Update track name
        self.track_artist_label.config(text="Artist Name") # Placeholder
        self.bpm_canvas.delete("all") # Redraw BPM display
        self.draw_circular_bpm() # Update BPM display with new track info (simulated)
        messagebox.showinfo("Loaded", f"Deck {self.deck_number}: {self.current_track}")
    
    def toggle_play(self):
        if not self.current_track:
            messagebox.showwarning("No Track", "Load a track first!")
            return
        
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_btn.config(text="⏸", bg='#ffaa00')
        else:
            self.play_btn.config(text="▶", bg='#00ff00')
    
    def cue(self):
        self.is_playing = False
        self.play_btn.config(text="▶", bg='#00ff00')
    
    def sync(self):
        messagebox.showinfo("Sync", f"Deck {self.deck_number}: Synced to master")
    
    def rewind(self):
        messagebox.showinfo("Rewind", f"Deck {self.deck_number}: Rewind")
    
    def fast_forward(self):
        messagebox.showinfo("Fast Forward", f"Deck {self.deck_number}: Fast Forward")
    
    def set_hotcue(self, number):
        messagebox.showinfo("Hot Cue", f"Deck {self.deck_number}: Hot cue {number} set")
    
    def clear_hotcues(self):
        messagebox.showinfo("Clear", f"Deck {self.deck_number}: All hot cues cleared")


class SeratoWaveform:
    """Serato-style vertical waveform display in the center"""
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg='#0a0a0a')
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Waveform header
        header = tk.Frame(self.frame, bg='#0a0a0a', height=30)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="serato DJ", font=("Arial", 12, "bold"),
                fg="white", bg='#0a0a0a').pack(side=tk.LEFT, padx=10)
        
        tk.Label(header, text="Master", font=("Arial", 9),
                fg="#999", bg='#0a0a0a').pack(side=tk.LEFT, padx=5)
        
        tk.Label(header, text="MIDI", font=("Arial", 8, "bold"),
                fg="white", bg='#333', padx=5).pack(side=tk.RIGHT, padx=5)
        
        tk.Label(header, text="SETUP", font=("Arial", 8, "bold"),
                fg="white", bg='#333', padx=5).pack(side=tk.RIGHT, padx=5)
        
        # Time display
        time_label = tk.Label(header, text="3:25 PM", font=("Arial", 9),
                             fg="white", bg='#0a0a0a')
        time_label.pack(side=tk.RIGHT, padx=10)
        
        # Waveform canvas
        self.canvas = tk.Canvas(self.frame, bg='#000', height=300, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.draw_waveform()
    
    def draw_waveform(self):
        """Draw Serato-style dual waveform with orange/blue colors"""
        self.canvas.delete("all")
        
        width = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 600
        height = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 300
        center_y = height // 2
        
        # Draw center line
        self.canvas.create_line(0, center_y, width, center_y, fill='#333', width=2)
        
        # Draw beat markers (yellow lines)
        beat_interval = width // 10 # Simulate 10 beats across the screen
        for x in range(0, width, beat_interval):
            self.canvas.create_line(x, 0, x, height, fill='#ffff00', width=2)
        
        # Draw top waveform (orange)
        for x in range(0, width, 3):
            amp = random.randint(20, 80)
            # Orange gradient
            color = '#ff8800' if x % 6 == 0 else '#ff6600'
            self.canvas.create_rectangle(x, center_y - amp, x+2, center_y,
                                        fill=color, outline='')
        
        # Draw bottom waveform (blue)
        for x in range(0, width, 3):
            amp = random.randint(20, 80)
            # Blue gradient
            color = '#0088ff' if x % 6 == 0 else '#0066cc'
            self.canvas.create_rectangle(x, center_y, x+2, center_y + amp,
                                        fill=color, outline='')
        
        # Draw playhead (white vertical line)
        playhead_x = width // 2
        self.canvas.create_line(playhead_x, 0, playhead_x, height, fill='white', width=3)
        
        # Draw time markers (simulated)
        for i, time in enumerate(['30', '35', '40']):
            x_pos = width // 4 + (i * width // 4)
            self.canvas.create_text(x_pos, 10, text=time, fill='white', font=("Arial", 10))


class MusicAnalyzerDJ:
    """Main Serato DJ style application"""
    def __init__(self, root):
        self.root = root
        self.root.title("Music Analyzer DJ - Serato Style by Dave Nelligan")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#0a0a0a')
        self.tracks = [] # Stores full paths of loaded tracks
        self.deck1 = None # Will store SeratoDeck instance for Deck 1
        self.deck2 = None # Will store SeratoDeck instance for Deck 2
        self.setup_ui()
    
    def setup_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root, bg='#1a1a1a', fg='white', 
                         activebackground='#0066cc', activeforeground='white')
        self.root.config(menu=menubar)
        
        # FILE MENU
        file_menu = tk.Menu(menubar, tearoff=0, bg='#2a2a2a', fg='white',
                           activebackground='#0066cc', activeforeground='white')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="📁 Load Files...", command=self.load_files)
        file_menu.add_command(label="📂 Load Folder...", command=self.select_folder)
        file_menu.add_separator()
        file_menu.add_command(label="💾 Save Crate", command=self.save_crate)
        file_menu.add_command(label="📤 Export Playlist...", command=self.export)
        file_menu.add_separator()
        file_menu.add_command(label="⚙️ Preferences...", command=self.preferences)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Exit", command=self.root.quit)
        
        # VIEW MENU
        view_menu = tk.Menu(menubar, tearoff=0, bg='#2a2a2a', fg='white',
                           activebackground='#0066cc', activeforeground='white')
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="🎚️ Horizontal Layout", command=lambda: self.change_layout("horizontal"))
        view_menu.add_command(label="🎚️ Vertical Layout", command=lambda: self.change_layout("vertical"))
        view_menu.add_command(label="🎚️ 4 Deck View", command=lambda: self.change_layout("4deck"))
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Show Library") # Placeholder
        view_menu.add_checkbutton(label="Show Waveforms") # Placeholder
        view_menu.add_separator()
        view_menu.add_command(label="⛶ Fullscreen", command=self.toggle_fullscreen)
        
        # TRACK MENU
        track_menu = tk.Menu(menubar, tearoff=0, bg='#2a2a2a', fg='white',
                            activebackground='#0066cc', activeforeground='white')
        menubar.add_cascade(label="Track", menu=track_menu)
        track_menu.add_command(label="🔍 Analyze Files", command=self.analyze_files)
        track_menu.add_command(label="✏️ Edit ID3 Tags...", command=self.edit_tags)
        track_menu.add_command(label="🎵 Set Beatgrid...", command=self.set_beatgrid)
        track_menu.add_separator()
        track_menu.add_command(label="📊 Track Info...", command=self.track_info)
        
        # PLAYLIST MENU
        playlist_menu = tk.Menu(menubar, tearoff=0, bg='#2a2a2a', fg='white',
                               activebackground='#0066cc', activeforeground='white')
        menubar.add_cascade(label="Playlist", menu=playlist_menu)
        playlist_menu.add_command(label="➕ New Crate", command=self.new_crate)
        playlist_menu.add_command(label="📁 New Smart Crate", command=self.new_smart_crate)
        playlist_menu.add_separator()
        playlist_menu.add_command(label="📥 Import Playlist...", command=self.import_playlist)
        playlist_menu.add_command(label="📤 Export Playlist...", command=self.export)
        
        # HELP MENU
        help_menu = tk.Menu(menubar, tearoff=0, bg='#2a2a2a', fg='white',
                           activebackground='#0066cc', activeforeground='white')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="📖 User Guide", command=self.show_guide)
        help_menu.add_command(label="🔑 Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ About", command=self.show_about)
        
        # Main container
        main = tk.Frame(self.root, bg='#0a0a0a')
        main.pack(fill=tk.BOTH, expand=True)
        
        # Top section - Decks and waveform
        top_section = tk.Frame(main, bg='#0a0a0a')
        top_section.pack(fill=tk.BOTH, expand=True)
        
        # Left deck
        self.deck1 = SeratoDeck(top_section, 1, "Badlands")
        
        # Center waveform
        self.center_waveform = SeratoWaveform(top_section)
        
        # Right deck
        self.deck2 = SeratoDeck(top_section, 2, "Feel me")
        
        # Bottom section - Library browser
        self.create_library_browser(main)
    
    def create_library_browser(self, parent):
        """Create Serato-style library browser"""
        browser = tk.Frame(parent, bg='#1a1a1a', height=300)
        browser.pack(fill=tk.BOTH, padx=5, pady=5)
        browser.pack_propagate(False)
        
        # Browser tabs
        tabs = tk.Frame(browser, bg='#2a2a2a', height=35)
        tabs.pack(fill=tk.X)
        tabs.pack_propagate(False)
        
        tab_names = ["Files", "Browse", "Prepare", "History"]
        self.current_browser_tab = tk.StringVar(value="Files")
        for i, tab in enumerate(tab_names):
            btn = tk.Button(tabs, text=tab, font=("Arial", 10, "bold"),
                           bg='#0066cc' if tab=="Files" else '#2a2a2a', fg='white',
                           relief=tk.FLAT, width=12,
                           command=lambda t=tab: self.switch_browser_tab(t))
            btn.pack(side=tk.LEFT, padx=2, pady=5)
            # Store button reference to update color
            if tab == "Files": self.files_tab_btn = btn
            elif tab == "Browse": self.browse_tab_btn = btn
            elif tab == "Prepare": self.prepare_tab_btn = btn
            elif tab == "History": self.history_tab_btn = btn
        
        # Search box
        search_frame = tk.Frame(tabs, bg='#2a2a2a')
        search_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Label(search_frame, text="🔍", bg='#2a2a2a', fg='white').pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               bg='#333', fg='white', width=20, relief=tk.FLAT)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Browser content
        self.browser_content_frame = tk.Frame(browser, bg='#1a1a1a')
        self.browser_content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar - Crates/Folders (Files tab content)
        self.files_sidebar = tk.Frame(self.browser_content_frame, bg='#2a2a2a', width=200)
        self.files_sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.files_sidebar.pack_propagate(False)
        
        tk.Label(self.files_sidebar, text="⭐ All...", font=("Arial", 9),
                fg="white", bg='#2a2a2a', anchor=tk.W, padx=10).pack(fill=tk.X, pady=2)
        tk.Label(self.files_sidebar, text="🔊 All Audio...", font=("Arial", 9),
                fg="white", bg='#2a2a2a', anchor=tk.W, padx=10).pack(fill=tk.X, pady=2)
        tk.Label(self.files_sidebar, text="📹 All Videos...", font=("Arial", 9),
                fg="white", bg='#2a2a2a', anchor=tk.W, padx=10).pack(fill=tk.X, pady=2)
        
        tk.Label(self.files_sidebar, text="📂 A List", font=("Arial", 9, "bold"),
                fg="white", bg='#2a2a2a', anchor=tk.W, padx=10).pack(fill=tk.X, pady=5)
        
        # Expandable folders (using Treeview for better structure)
        self.folder_tree = ttk.Treeview(self.files_sidebar, show="tree", height=8)
        self.folder_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        crates_id = self.folder_tree.insert("", 'end', "crates", text="📦 Crates", open=True)
        self.folder_tree.insert(crates_id, 'end', text="➕ New Crate")
        self.folder_tree.insert(crates_id, 'end', text="A List")
        self.folder_tree.insert(crates_id, 'end', text="Party Tunes")

        music_id = self.folder_tree.insert("", 'end', "music_folders", text="📁 Music", open=True)
        self.folder_tree.insert(music_id, 'end', text="Electronic")
        self.folder_tree.insert(music_id, 'end', text="Drum and Bass")
        self.folder_tree.insert(music_id, 'end', text="House")
        self.folder_tree.insert(music_id, 'end', text="Techno")
        
        self.folder_tree.bind('<<TreeviewSelect>>', self.on_folder_click)
        
        tk.Button(self.files_sidebar, text="📁 SELECT FOLDER", font=("Arial", 9, "bold"),
                 bg='#00ff00', fg='black', relief=tk.FLAT,
                 command=self.select_folder).pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)
        
        # Track list
        self.list_frame = tk.Frame(self.browser_content_frame, bg='#1a1a1a')
        self.list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Column headers
        columns = ("song", "artist", "album", "bpm", "bitrate", "length")
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show="headings", height=12)
        
        self.tree.heading("song", text="song")
        self.tree.heading("artist", text="artist")
        self.tree.heading("album", text="album")
        self.tree.heading("bpm", text="bpm")
        self.tree.heading("bitrate", text="bitrate")
        self.tree.heading("length", text="length")
        
        self.tree.column("song", width=250)
        self.tree.column("artist", width=200)
        self.tree.column("album", width=200)
        self.tree.column("bpm", width=60)
        self.tree.column("bitrate", width=80)
        self.tree.column("length", width=80)
        
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # RIGHT-CLICK MENU
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<Double-Button-1>', self.load_to_deck)
        
        # Placeholder frames for other tabs
        self.browse_frame = tk.Frame(self.browser_content_frame, bg='#1a1a1a')
        self.prepare_frame = tk.Frame(self.browser_content_frame, bg='#1a1a1a')
        self.history_frame = tk.Frame(self.browser_content_frame, bg='#1a1a1a')
        
        self.create_browse_tab_content()
        self.create_prepare_tab_content()
        self.create_history_tab_content()
        # Configure ttk styles for Serato look
def configure_styles():
    """Configure ttk styles for Serato DJ appearance"""
    style = ttk.Style()
    style.theme_use('clam')
    
    # General button style
    style.configure("TButton",
                   background="#2a2a2a",
                   foreground="white",
                   font=("Arial", 9, "bold"),
                   relief="flat",
                   borderwidth=0)
    style.map("TButton",
             background=[('active', '#0066cc')])
    
    # Treeview styling
    style.configure("Treeview",
                   background="#1a1a1a",
                   foreground="white",
                   fieldbackground="#1a1a1a",
                   borderwidth=0,
                   rowheight=24) # Adjust row height for better look
    
    style.configure("Treeview.Heading",
                   background="#2a2a2a",
                   foreground="white",
                   font=("Arial", 9, "bold"),
                   borderwidth=1,
                   relief="flat")
    
    style.map("Treeview",
             background=[('selected', '#0066cc')])
    
    style.map("Treeview.Heading",
             background=[('active', '#0066cc')])
    
    # Scrollbar styling
    style.configure("Vertical.TScrollbar",
                   background="#333",
                   troughcolor="#1a1a1a",
                   bordercolor="#1a1a1a",
                   arrowcolor="white")
    style.map("Vertical.TScrollbar",
             background=[('active', '#0066cc')])


# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    configure_styles() # Apply the custom styles
    app = MusicAnalyzerDJ(root)
    root.mainloop()
