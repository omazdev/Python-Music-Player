from tkinter import *
from tkinter import ttk, filedialog
import tkinter
import pygame
import os


def play_pause(event=None):

    if playlist_box.get(ACTIVE):  # Check if playlist is not empty

        if not playlist_box.curselection():  # If no track is selected, select the first track
            playlist_box.selection_set(0)

        track_name = playlist_box.get(playlist_box.curselection())

        if track_title.get() != track_name or track_status.get() == "(Stopped)" or event:  # event is a doube clic on a track
            track_idx = int(playlist_box.curselection()[0])
            track_path = playlist[track_idx]
            # Display Selected track title
            track_title.set(track_name)
            # Displa track Status
            track_status.set("(Playing)")

            play_pause_btn.configure(image=pause_img)
            try:
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.play()
            except:
                tkinter.messagebox.showwarning(
                    title="Warning!", message="Unable to play current track. Please choose another track!")

        elif track_status.get() == "(Playing)":
            # Displaying Status
            track_status.set("(Paused)")
            play_pause_btn.configure(image=play_img)

            # Paused Song
            pygame.mixer.music.pause()

        elif track_status.get() == "(Paused)":
            # It will Display the  Status
            track_status.set("(Playing)")
            play_pause_btn.configure(image=pause_img)
            # Playing back Song
            pygame.mixer.music.unpause()
    else:
        tkinter.messagebox.showwarning(
            title="Warning!", message="Please insert at least One TRACK to play (menu: File->insert tracks)!")


def stopsong():
    # Displaying Status
    track_status.set("(Stopped)")
    play_pause_btn.configure(image=play_img)
    # Stopped Song
    pygame.mixer.music.stop()


def insert_tracks(event=None):

    # playlist_items = playlist_box.get(0, len(playlist))
    # Fetching tracks
    tracks_items= filedialog.askopenfilenames(filetypes=[("Audio files", ('*.flac', '*.wav', '*.mp3'))],
                                              title="Select tracks")

    # Force insertion of at least one track
    # if (not tracks_list) and (not playlist_items):
    #     insert_tracks()

    # Inserting into Playlist
    for track_path in tracks_items:
        # Extract file name from full path
        track = os.path.basename(track_path)
        if track not in playlist_box.get(0, len(playlist)):  # Avoid duplicates
            playlist_box.insert(END, track)
            playlist.append(track_path)

# TODO Implement remove tracks


def remove_tracks():
    pass


def quit_app(event=None):
    root.destroy()

root = Tk()

# Title of the window
root.title("Hawk3Player")
# Window geometry
root.geometry("540x400")
# Window not resizable
root.resizable(0, 0)
# Delete Dashes from menus
root.option_add('*tearOff', FALSE)

# Initiating Pygame
pygame.init()
# Initiating Pygame Mixer
pygame.mixer.init()
pygame.mixer.music.set_volume(0.2)

# Initialize var containing tracks full path
playlist = []

track_title = StringVar()
track_title.set("---  : ")

track_status = StringVar()
track_status.set("---")

# Configure Menus
menubar = Menu(root)
root.configure(menu=menubar)
menu_file = Menu(menubar)
menubar.add_cascade(menu=menu_file, label='File')

# Insert tracks menu item
menu_file.add_command(label='Insert tracks', command=insert_tracks, accelerator="Ctrl+I")
root.bind("<Control-i>", insert_tracks)

menu_file.add_command(label='Remove tracks')

# Quit menu item
menu_file.add_command(label='Quit', command= quit_app, accelerator="Ctrl+Q")
root.bind('<Control-q>', quit_app)

main_frame = ttk.Frame(root, padding="10 10 10 10")
main_frame.grid(column=0, row=0)
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(0, weight=1)

# Creating Playlist Frame
songs_frame = ttk.Frame(main_frame, padding="10 10 10 10")
songs_frame.grid(column=0, row=0)

# Inserting scrollbar
scrol_y = Scrollbar(songs_frame, orient=VERTICAL)

# Inserting Playlist listbox
playlist_box = Listbox(songs_frame, width=60, height=10, yscrollcommand=scrol_y.set, selectbackground="grey",
                       selectmode=SINGLE, font=("times new roman", 12, "bold"), bg="white", fg="navyblue")
# Handle double click on playlist item
playlist_box.bind('<Double-Button-1>', play_pause)
# Applying Scrollbar to listbox
scrol_y.pack(side=RIGHT, fill=Y)
scrol_y.config(command=playlist_box.yview)
playlist_box.pack(fill=BOTH)

# Track Frame for Song infos
track_frame = ttk.Frame(main_frame, padding="10 10 10 10")
track_frame.grid(column=0, row=1)

track_title_label = Label(track_frame, text="Song Title", textvariable=track_title, font=(
    "times new roman", 12, "bold"), fg="navyblue")
track_title_label.pack(side=LEFT)

track_status_label = Label(track_frame, text="Song Title", textvariable=track_status, font=(
    "times new roman", 12, "bold"), fg="navyblue")
track_status_label.pack()

# Buttons Frame
buttons_frame = ttk.Frame(main_frame, padding="10 10 10 10")
buttons_frame.grid(column=0, row=2)

# Load Play Image
play_img = PhotoImage(
    file="/home/nhwk/Documents/WebDev/Desktop/simple-mp3-player/player-play.png")
play_img = play_img.subsample(10)

# Load Pause Image
pause_img = PhotoImage(
    file="/home/nhwk/Documents/WebDev/Desktop/simple-mp3-player/player-pause.png")
pause_img = pause_img.subsample(10)

# Play/Pause button
play_pause_btn = Button(buttons_frame, image=play_img, command=play_pause,
                        borderwidth=0, padx=200, pady=200)
play_pause_btn.grid(row=0, column=0)

# Stop Button
stop_img = PhotoImage(
    file="/home/nhwk/Documents/WebDev/Desktop/simple-mp3-player/player-stop.png")
stop_img = stop_img.subsample(3)
stop_btn = Button(buttons_frame, image=stop_img,
                  command=stopsong, borderwidth=0)
stop_btn.grid(row=0, column=1)

insert_tracks()


root.mainloop()
