from tkinter import *
from tkinter import ttk, filedialog
import tkinter
import pygame
import os
import time
from mutagen import File


def play_pause(event=None):
    """ Play or Pause curent track and update track status label accordingly """
    if playlist_box.get(ACTIVE):  # Check if playlist is not empty

        global previous_active_track_idx
        
        if not playlist_box.curselection():  # If no track is selected, select the first track
            playlist_box.selection_set(0)
            # Keep record of selected track index (this variable is created only once at startup)
            selected_track_idx = 0

        track_name = playlist_box.get(playlist_box.curselection())

        if track_title.get() != track_name or track_status.get() == "(Stopped)" or event:  # event is a doube clic on a track
            selected_track_idx = int(playlist_box.curselection()[0])
            track_path = playlist[selected_track_idx]

            # pygame.mixer.music.load(track_path)
            # pygame.mixer.music.play()

            # track_length(track_path)
            # play_time()

            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            # Display Selected track title
            track_title.set(track_name)
            # Displa track Status
            track_status.set("(Playing)")
            play_pause_btn.configure(image=pause_img)

            track_length(track_path)
            play_time()
            previous_active_track_idx = int(selected_track_idx)
            # try:
            #     pygame.mixer.music.load(track_path)
            #     pygame.mixer.music.play()
            #     # Display Selected track title
            #     track_title.set(track_name)
            #     # Displa track Status
            #     track_status.set("(Playing)")
            #     play_pause_btn.configure(image=pause_img)

            #     track_length(track_path)
            #     play_time()
            #     previous_active_track_idx = int(selected_track_idx)
            # except:
            #     tkinter.messagebox.showwarning(
            #         title="Warning!", message=f"Audio file incorrect : {track_name}, Please chose another file!")
            #     # Uselect the incorrect track
            #     playlist_box.selection_clear(selected_track_idx)
            #     # Select the previous active track
            #     playlist_box.selection_set(previous_active_track_idx)
            #     playlist_box.see(previous_active_track_idx)


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
    """" Stop playing current track """
    # Displaying Status
    track_status.set("(Stopped)")
    play_pause_btn.configure(image=play_img)
    track_pos_label.configure(text="00:00")
    # Stopped Song
    pygame.mixer.music.stop()


def insert_tracks(event=None):
    """" Open dialog to insert audio files """
    # playlist_items = playlist_box.get(0, len(playlist))
    # Fetching tracks
    tracks_items= filedialog.askopenfilenames(filetypes=[("Audio files", ('*.flac', '*.wav', '*.mp3', '.ogg'))],
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

def change_vol(vol_event=None):
    """" Control track volume """
    pygame.mixer.music.set_volume(float(vol_event))

def play_time(value=None):
    """" Print track time position """
    global update_pos
    global track_total_play_time
    global pos_list
    # Print track position only if the track is playing
    if not track_status.get() == "(Stopped)":
        
        # Get current track time in seconds
        track_total_play_time = pygame.mixer.music.get_pos()/1000

        if not value and pygame.mixer.music.get_busy():
            if pos_list[-1] == 'SLIDED':
                track_total_play_time += float(pos_list[-2])
                # pos_list.pop()
            # Convert to format minutes:seconds
            current_time_formated = time.strftime('%M:%S', time.gmtime(track_total_play_time)) 
            # current_time += 1
            print("current time: ", track_total_play_time, "slider position: ", track_pos.get())

            # update slider position
            track_pos.set(track_total_play_time)
            # Print play time in the label 
            track_pos_label.configure(text=current_time_formated)

        else:
            print("LAST SLIDER POS: ", pos_list[-1])
            pygame.mixer.music.play(0, float(pos_list[-1]) )
            track_total_play_time += float(pos_list[-1])
            pos_list.append(pos_list[-1])
            pos_list.append('SLIDED')

            # Convert to format minutes:seconds
            current_time_formated = time.strftime('%M:%S', time.gmtime(float(pos_list[-2])))
            track_pos_label.configure(text=current_time_formated)
            print("after current time: ", pos_list[-2], "slider position: ", track_pos.get())

        # Update label every 1 second
        update_pos = track_pos_label.after(1000, play_time)


def track_length(track_path):
    """ Extract and print track length """
    global track_total_length
    track_extension = os.path.splitext(track_path)[1]
    if track_extension:
        try:
            mutagen_track = File(track_path) 
            track_total_length = mutagen_track.info.length
        except:
            track_total_length = 0
            tkinter.messagebox.showwarning(
                title="Warning!", message=f"Audio file incorrect : {track_path}")
        finally:
            track_length_formated = time.strftime('%M:%S', time.gmtime(track_total_length))
            track_length_label.configure(text=track_length_formated)
            track_pos_slider.configure(to=track_total_length)

 
def slider_watcher(value):
    global update_pos
    track_pos_label.after_cancel(update_pos)
    print("VALUE", value)
    pos_list.append(value)
    pygame.mixer.music.stop()
    # track_pos_label.after(100,play_time(pos_list[-1]))
    play_time(value)


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
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
# pygame.mixer.music.set_volume(0.2)

# Initialize var containing tracks full path
playlist = []

track_title = StringVar()
track_title.set("---  : ")

track_status = StringVar()
track_status.set("---")

track_pos = DoubleVar()
track_pos.set(0)
update_pos = None

pos_list = [0]

track_total_play_time = 0
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

main_frame = ttk.Frame(root, padding="5 5 5 5")
main_frame.grid(column=0, row=0)
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(0, weight=1)

# Creating Playlist Frame
songs_frame = ttk.Frame(main_frame, padding="5 5 5 5")
songs_frame.grid(column=0, row=0)

# Inserting scrollbar
scrol_y = Scrollbar(songs_frame, orient=VERTICAL)

# Inserting Playlist listbox
playlist_box = Listbox(songs_frame, width=60, height=10, yscrollcommand=scrol_y.set, selectbackground="grey",
                       selectmode=SINGLE, font=("times new roman", 12, "bold"), bg="white", fg="navyblue")

# Applying Scrollbar to listbox
scrol_y.pack(side=RIGHT, fill=Y)
scrol_y.config(command=playlist_box.yview)
playlist_box.pack(fill=BOTH)

# Handle double click on playlist item
playlist_box.bind('<Double-Button-1>', play_pause)

previous_active_track_idx = 0

# Track Frame for Song infos
track_frame = ttk.Frame(main_frame, padding="1 1 1 1")
track_frame.grid(column=0, row=1)

track_title_label = Label(track_frame, text="Song Title", textvariable=track_title, font=(
    "times new roman", 12, "bold"), fg="navyblue")
track_title_label.grid(row=0, column=0)

track_status_label = Label(track_frame, text="Song Title", textvariable=track_status, font=(
    "times new roman", 12, "bold"), fg="navyblue")
track_status_label.grid(row=0, column=1)

# Track Frame for Song slider and play time
track_pos_frame = ttk.Frame(main_frame, padding="1 1 1 1")
track_pos_frame.grid(column=0, row=2)

# track_pos = StringVar(value="0:0")
track_pos_label = Label(track_pos_frame, text="00:00")
track_pos_label.grid(row=1, column=0)

track_length_label = Label(track_pos_frame, text="00:00")
track_length_label.grid(row=1, column=2)


track_pos_slider = Scale(track_pos_frame, length=400, from_=1, to=0, orient=HORIZONTAL,
                         resolution=.001, showvalue=False, variable=track_pos, command=slider_watcher)
track_pos_slider.grid(row=1, column=1)


# Buttons Frame
buttons_frame = ttk.Frame(main_frame, padding="2 2 2 2")
buttons_frame.grid(column=0, row=3)

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

# Volume Slider
volume_ctrl = Scale(buttons_frame, from_ = 1, to = 0, orient = VERTICAL, resolution = .1, command=change_vol)
volume_ctrl.grid(row=0, column=2)
# Set volume's initial value
volume_ctrl.set(0.6)


insert_tracks()


root.mainloop()
