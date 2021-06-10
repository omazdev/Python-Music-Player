from tkinter import *
from tkinter import ttk, filedialog
import tkinter
import pygame
import os
import time
from mutagen import File

# TODO refactor code.
# TODO Catch pygame mixer exceptions


def play_pause(event=None, track_idx=None):
    """ Play or Pause curent track and update track status label accordingly """
    if playlist_box.size() > 0:  # Check if playlist is not empty
        print("EVENT==========> ", event)
        global active_track_idx
        global track_total_play_time
        global track_last_slided_pos
        global track_last_paused_pos
        global track_total_length
        
        if not playlist_box.curselection():  # If no track is selected, select the first track
            playlist_box.selection_set(0)
            # Keep record of selected track index (this variable is created only once at startup)
            selected_track_idx = 0

        track_name = playlist_box.get(playlist_box.curselection())

        track_pos_slider.configure(state="active")
        
        print("-----------TRACK INDEX: ", track_idx)
        if (track_idx is not None) or track_title.get() != track_name or track_status.get() == "(Stopped)" or event:  # event is a doube clic on a track
            
            # When playing another track while the current one is still playing or is paused,
            # Initialize track status    
            if track_status.get() == "(Playing)" or track_status.get() == "(Paused)":

                print("INITIALIZING TRACK")
                cancel_update_play_time_loop()
                track_last_slided_pos = 0
                track_last_paused_pos = 0
                track_total_play_time = 0
                track_pos_label.configure(text="00:00")
                track_pos.set(0)
            
            print("==========INDEX OF TRACK TO PLAY :", track_idx) 
            if track_idx is not None:
                selected_track_idx = track_idx
                track_path = playlist[selected_track_idx]
                # playlist_box.selection_set(track_idx)
                track_name = playlist_box.get(track_idx)
                print("--PLAYING IDX-- ", track_idx, "TRACK :", track_name)
            else:
                selected_track_idx = int(playlist_box.curselection()[0])
                track_path = playlist[selected_track_idx]

            try:
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.play()
                print("================PLAYING======================")
                # Display Selected track title
                track_title.set(track_name)
                # Display track Status
                track_status.set("(Playing)")
                play_pause_btn.configure(image=pause_img)

                track_total_length =  get_track_length(track_path)
                track_total_play_time = 0

                playlist_box.see(selected_track_idx)

                update_play_time()
                cancel_track_end_event_loop()
                check_track_end_event()

                active_track_idx = int(selected_track_idx)
            except:
                tkinter.messagebox.showwarning(
                    title="Warning!", message=f"Audio file incorrect : {track_name}, Please chose another file!")
                # Uselect the incorrect track
                playlist_box.selection_clear(selected_track_idx)
                # Select the previous active track
                playlist_box.selection_set(active_track_idx)
                playlist_box.see(active_track_idx)

        # PAUSE the track
        elif track_status.get() == "(Playing)":
            cancel_update_play_time_loop()
            cancel_track_end_event_loop()

            track_last_paused_pos = track_pos.get()
            # Displaying Status
            track_status.set("(Paused)")
            play_pause_btn.configure(image=play_img)
            
            print("================PAUSING======================")
            # Paused Song
            pygame.mixer.music.pause()

        # UNPAUSE the track
        elif track_status.get() == "(Paused)":

            cancel_track_end_event_loop()
            # Display the Status
            track_status.set("(Playing)")
            play_pause_btn.configure(image=pause_img)
            print("TIME BEFORE UNPAUSING : ", track_last_paused_pos, "POS : ", track_pos.get())

            # If track is PAUSED and the slider position changed,
            # play from the actual slider position
            if track_pos.get() != track_last_paused_pos:
                print("REPLAYING FROM SLIDER POS===========")
                # If the slider is at beginning position (1.000),
                # play the track from position 0
                if int(float(track_pos.get())) == 1.000:
                    print("=========VALUE IS ONE============= : ", track_pos.get())
                    track_last_slided_pos= 0
                pygame.mixer.music.play(0, track_pos.get())
            # UNPAUSE the track
            else:
                print("================UNPAUSING======================")
                pygame.mixer.music.unpause()
            
            root.after(500)
            update_play_time()
            check_track_end_event()
    else:
        tkinter.messagebox.showwarning(
            title="Warning!", message="Please insert at least One TRACK to play (menu: File->insert tracks)!")


def play_previous():
    """ Play previous track """
    global active_track_idx
    # Playlist in not empty
    if playlist_box.size() > 0:
        # No active track (no track is playing)
        if active_track_idx < 0:
            # play first track in playlist
            play_pause()
        # A track is playing 
        else:
            print(">>>>>>ACTIVE TRACK INDEX :", active_track_idx)
            # active track is the first in playlist
            if active_track_idx == 0:
                print(">>>>>>>>>>>REWINDING<<<<<<<<<<<")
                # rewind track
                play_pause(track_idx=active_track_idx)
            # active track is not first in playlist
            else:
                print(">>>>>>>>>>>PLAYING PREVIOUS TRACK<<<<<<<<<<<")
                # play previous track
                playlist_box.selection_clear(0, END)
                # root.after(100)
                playlist_box.selection_set(active_track_idx-1)
                # root.after(100)
                play_pause(track_idx=active_track_idx-1)


def play_next():
    """ Play next track """
    global active_track_idx
    global track_last_slided_pos
    global track_last_paused_pos
    global track_total_play_time

    # Playlist in not empty
    if playlist_box.size() > 0:
        # No active track (no track is playing)
        if active_track_idx < 0:
            # play first track in playlist
            play_pause()
        # A track is playing 
        else:
            print(">>>>>>ACTIVE TRACK INDEX :", active_track_idx)
            # active track is the last in playlist
            if active_track_idx == playlist_box.size()-1:
                # RESET player
                print("INITIALIZING TRACK AFTER NO NEXT TO PLAY")
                playlist_box.selection_clear(0, END)
                active_track_idx = -1
                # playlist_box.see(0)
                cancel_update_play_time_loop()
                cancel_track_end_event_loop()
                track_status.set("---")
                track_title.set("---  : ")
                play_pause_btn.configure(image=play_img)
                track_last_slided_pos = 0
                track_last_paused_pos = 0
                track_total_play_time = 0
                track_pos_label.configure(text="00:00")
                track_length_label.configure(text="00:00")
                track_pos_slider.configure(state="disabled")
                track_pos.set(0)        
                # BUG Using rewind and pause instead of stop,
                # Reason: after stopping a track and playing the same track (or other track),
                # an "End of track" event is generated, BUGGG???
                pygame.mixer.music.rewind()
                pygame.mixer.music.pause()

            # active track is not last in playlist
            else:
                print(">>>>>>>>>>>PLAYING PREVIOUS TRACK<<<<<<<<<<<")
                # play next track
                playlist_box.selection_clear(0, END)
                # root.after(100)
                playlist_box.selection_set(active_track_idx+1)
                # root.after(100)
                play_pause(track_idx=active_track_idx+1)

def stop():
    """" Stop playing current track """
    global track_last_slided_pos 
    global track_last_paused_pos
    if playlist_box.size() > 0:
        print("================STOPPING======================")
        # Displaying Status
        track_status.set("(Stopped)")
        play_pause_btn.configure(image=play_img)
        track_pos_label.configure(text="00:00")
        track_pos.set(0)
        track_last_slided_pos = 0
        track_last_paused_pos = 0
        track_pos_slider.configure(state="disabled")
        cancel_update_play_time_loop()
        cancel_track_end_event_loop()
        # Stopped Song
        # pygame.mixer.music.stop()
        # BUG Using rewind and pause instead of stop,
        # Reason: after stoping track and playing the same track,
        # and "End of track" event is generated, BUGGG???
        pygame.mixer.music.rewind()
        pygame.mixer.music.pause()


def insert_tracks(event=None):
    """" Open dialog to insert audio files """
    # playlist_items = playlist_box.get(0, len(playlist))
    # Fetching tracks
    tracks_items = filedialog.askopenfilenames(filetypes=[(
        "Audio files", ('*.flac', '*.wav', '*.mp3', '.ogg'))], title="Select tracks")

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


def change_volume(vol_event=None):
    """" Control track volume """
    pygame.mixer.music.set_volume(float(vol_event))


def update_play_time(value=None):
    """" Print track time position """
    global track_total_play_time
    global track_last_slided_pos
    global play_time_loop_id 
    # Print track position only if the track is playing
    if track_status.get() == "(Playing)":
            
        # The track is playing normally
        if (not value) and pygame.mixer.music.get_busy():

            # Get current track time in seconds
            track_total_play_time = pygame.mixer.music.get_pos()/1000 + float(track_last_slided_pos)

            print("TRACK TOTAL TIME: ", track_total_play_time)
            print("track_last_slided_pos: ", track_last_slided_pos)
            # Convert to format minutes:seconds
            current_time_formated = time.strftime('%M:%S', time.gmtime(track_total_play_time)) 

            # update slider position
            track_pos.set(track_total_play_time)
            print("current time: ", track_total_play_time, "slider position: ", track_pos.get())

            # Print play time in the label 
            track_pos_label.configure(text=current_time_formated)

        # The user is moving the slider
        else:
            print("LAST SLIDER POS: ", track_last_slided_pos)
            print("LAST TOTAL TIME: ", track_total_play_time)
            print("VALUE", int(float(track_last_slided_pos)))

            if int(float(track_last_slided_pos)) == 1.000:
                print("=========VALUE IS ONE============= : ", track_last_slided_pos)
                track_last_slided_pos= 0

            # BUG : after every slide, playing from slider position
            # is queued, pygame mixer plays from all positions
            # Bug Fix : Loading after every user slide,
            pygame.mixer.music.load(playlist[active_track_idx])
            pygame.mixer.music.play(0, float(track_last_slided_pos) )

            # Convert to format minutes:seconds
            current_time_formated = time.strftime('%M:%S', time.gmtime(float(track_last_slided_pos)))
            track_pos_label.configure(text=current_time_formated)
            print("after current time: ", track_total_play_time, "slider position: ", track_pos.get())

        # Update every 1 second
        play_time_loop_id = track_pos_label.after(1000, update_play_time)


def cancel_update_play_time_loop():
    global play_time_loop_id
    
    if play_time_loop_id is not None:
        track_pos_label.after_cancel(play_time_loop_id)
        play_time_loop_id = None
    

def check_track_end_event():
    
    global track_last_slided_pos 
    global track_last_paused_pos
    global track_pos_label
    global check_track_end_id
    global TRACK_END

    print("----End event TRACK STATUS-------- : ", track_status.get())
    if track_status.get() == "(Playing)":

        # If we reach the end of the track, initialize the player
        for event in pygame.event.get():
            print("===____EVENT IS____=== ", event.type)
            if event.type == TRACK_END:
                print("======END OF TRACK=========")
                cancel_track_end_event_loop()
                cancel_update_play_time_loop()
                # Displaying Status
                track_status.set("(Stopped)")
                track_pos_label.configure(text="00:00")
                track_pos.set(0)
                track_last_slided_pos = 0
                track_last_paused_pos = 0
                play_next()
                return

        print("-------CHECKING END EVENT----------------")
        
        check_track_end_id = root.after(100, check_track_end_event)


def cancel_track_end_event_loop():
    global check_track_end_id
    
    if check_track_end_id is not None:
        root.after_cancel(check_track_end_id)
        check_track_end_id = None


def get_track_length(track_path):
    """ Extract and print track length """
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
            return track_total_length

 
def change_track_play_position(value):
    global track_last_slided_pos

    cancel_update_play_time_loop()
    print("=====SLIDING VALUE====== :", value)
    track_last_slided_pos = value

    # If the track is playing, send slider value to update_play_time()
    if track_status.get() == "(Playing)":
        update_play_time(value)
    #else just update track position Label
    else: 
        # Convert to format minutes:seconds
        current_time_formated = time.strftime('%M:%S', time.gmtime(float(track_pos.get())))
        track_pos_label.configure(text=current_time_formated)
         

def remove_track():
    global track_total_play_time
    global track_last_slided_pos
    global track_last_paused_pos
    
    if playlist_box.size() > 0: # Check if the playlist is not empty

        if playlist_box.curselection(): # Check if a track is selected
            track_indx = int(playlist_box.curselection()[0]) # Get index of selected track
            print(">>>>>TRACK INDX TO REMOVE<<<<< ", track_indx)

            if track_indx >= 0 and track_indx <= playlist_box.size()-1:

                print("============TRACK JBEFORE REMOVING ", track_indx, "PLAYLIST :", playlist)

                track = playlist_box.get(track_indx)
                playlist_box.delete(track_indx)
                playlist.pop(track_indx)
                print("--REMOVED TRACK FROM LIST :", playlist)

                print("TRACK TITLE : ", track_title.get(), "DELETED TRACK", track) 
                print("track_indx :", track_indx)
                print("playlist_box state :", playlist_box.size())
                if playlist_box.size() == 0:  # Check if playlist is empty
                    print("INITIALIZING TRACK after delete")
                    cancel_update_play_time_loop()
                    cancel_track_end_event_loop()
                    track_status.set("---")
                    track_title.set("---  : ")
                    play_pause_btn.configure(image=play_img)
                    track_last_slided_pos = 0
                    track_last_paused_pos = 0
                    track_total_play_time = 0
                    track_pos_label.configure(text="00:00")
                    track_length_label.configure(text="00:00")
                    track_pos_slider.configure(state="disabled")
                    track_pos.set(0)        
                    # BUG Using rewind and pause instead of stop,
                    # Reason: after stopping a track and playing the same track (or other track),
                    # an "End of track" event is generated, BUGGG???
                    pygame.mixer.music.rewind()
                    pygame.mixer.music.pause()
                    # pygame.mixer.music.stop()
                # Playlist is not empty
                elif track_title.get() == track: # The deleted track is the track being played
                    # If track is not the last, play the next track (same index of removed track)
                    if track_indx <= playlist_box.size()-1:
                        playlist_box.selection_set(track_indx)
                        play_pause(track_idx=track_indx)
                    # If deleted track is the last, play the first track in playlist
                    else:
                        play_pause()
                    print("----------DELETED PLAYING TRACK-----------")
                else: # The deleted track is not the track being played
                    print("====================ACTIVE TRACK BEFORE DELETION :", active_track_idx)
                    # Select the Playing (Active) track
                    if track_indx < active_track_idx: # The deleted track is before playing track
                        playlist_box.selection_set(active_track_idx-1) 
                    else: # The deleted track is after playing track
                        playlist_box.selection_set(active_track_idx)
                        
        else: # User didn't select a track to delete
            tkinter.messagebox.showwarning(
                title="Warning!", message="Please select a TRACK to DELETE!")
    else: # User trying to delete from empty playlist
        tkinter.messagebox.showwarning(
            title="Warning!", message="Playlist is empty. Please insert at least One TRACK to DELETE!")
    
    
def quit_app(event=None):
    pygame.mixer.quit()
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

# Configure track end event
TRACK_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(TRACK_END)

track_title = StringVar()
track_title.set("---  : ")

# track_status : Playing, Paused, Stopped
track_status = StringVar()
track_status.set("---")

track_pos = DoubleVar()
track_pos.set(1)

play_time_loop_id = None
check_track_end_id  = None

track_last_slided_pos = 0

track_last_paused_pos = 0

track_total_play_time = 0

active_track_idx = -1

# Configure Menus
menubar = Menu(root)
root.configure(menu=menubar)
menu_file = Menu(menubar)
menubar.add_cascade(menu=menu_file, label='File')

# Insert tracks menu item
menu_file.add_command(label='Insert tracks', command=insert_tracks, accelerator="Ctrl+I")
root.bind("<Control-i>", insert_tracks)

# menu_file.add_command(label='Remove tracks')

# Quit menu item
menu_file.add_command(label='Quit', command= quit_app, accelerator="Ctrl+Q")
root.bind('<Control-q>', quit_app)

main_frame = ttk.Frame(root, padding="5 5 5 5")
main_frame.grid(column=0, row=0)
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(0, weight=1)

# Creating Playlist Frame
songs_frame = ttk.Frame(main_frame, padding="1 1 1 1")
songs_frame.grid(column=0, row=0)

# Inserting scrollbar
scrol_y = Scrollbar(songs_frame, orient=VERTICAL)

# Inserting Playlist listbox
playlist_box = Listbox(songs_frame, width=55, height=10, yscrollcommand=scrol_y.set, selectbackground="grey",
                       selectmode=SINGLE, font=("times new roman", 12, "bold"), bg="white", fg="navyblue")

# Applying Scrollbar to listbox
scrol_y.pack(side=RIGHT, fill=Y)
scrol_y.config(command=playlist_box.yview)
playlist_box.pack(fill=BOTH)

# Add/remove track Frame
add_remove_frame = ttk.Frame(main_frame, padding="1 1 1 1")
add_remove_frame.grid(column=1, row=0, sticky="n")


# Add track button
add_track_btn = Button(add_remove_frame, text="+", width=1, height=1, command=insert_tracks)
add_track_btn.grid(row=0, column=0)

# Remove track button
remove_track_btn = Button(add_remove_frame, text="-", width=1, height=1, command=remove_track)
remove_track_btn.grid(row=1, column=0)

# Handle double click on playlist item
playlist_box.bind('<Double-Button-1>', play_pause)


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
                         resolution=1, showvalue=False, variable=track_pos, state="disabled", command=change_track_play_position)
track_pos_slider.grid(row=1, column=1)


# Buttons Frame
buttons_frame = ttk.Frame(main_frame, padding="2 2 2 2")
buttons_frame.grid(column=0, row=3)

# Load "Previous" Image
previous_img = PhotoImage(
    file="/home/nhwk/Documents/WebDev/Desktop/simple-mp3-player/player-previous.png")
previous_img = previous_img.subsample(11)

# Load Play Image
play_img = PhotoImage(
    file="/home/nhwk/Documents/WebDev/Desktop/simple-mp3-player/player-play.png")
play_img = play_img.subsample(10)

# Load Pause Image
pause_img = PhotoImage(
    file="/home/nhwk/Documents/WebDev/Desktop/simple-mp3-player/player-pause.png")
pause_img = pause_img.subsample(10)

# Load "Next" Image
next_img = PhotoImage(
    file="/home/nhwk/Documents/WebDev/Desktop/simple-mp3-player/player-next.png")
next_img = next_img.subsample(11)

# "Previous" button
previous_btn = Button(buttons_frame, image=previous_img, command=play_previous,
                        borderwidth=0, padx=200, pady=200)
previous_btn.grid(row=0, column=0)

# Play/Pause button
play_pause_btn = Button(buttons_frame, image=play_img, command=play_pause,
                        borderwidth=0, padx=200, pady=200)
play_pause_btn.grid(row=0, column=1)

# Stop Button
stop_img = PhotoImage(
    file="/home/nhwk/Documents/WebDev/Desktop/simple-mp3-player/player-stop.png")
stop_img = stop_img.subsample(3)
stop_btn = Button(buttons_frame, image=stop_img,
                  command=stop, borderwidth=0)
stop_btn.grid(row=0, column=2)

# "Next" button
next_btn = Button(buttons_frame, image=next_img, command=play_next,
                        borderwidth=0, padx=200, pady=200)
next_btn.grid(row=0, column=3)


# Volume Slider
volume_ctrl = Scale(buttons_frame, from_ = 1, to = 0, orient = VERTICAL, resolution = .1, command=change_volume)
volume_ctrl.grid(row=0, column=4)
# Set volume's initial value
volume_ctrl.set(0.2)


insert_tracks()


root.mainloop()
