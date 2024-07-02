import random
import threading
import time
from tkinter import *
from tkinter.ttk import *
import os
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk
import pygame
from mutagen.mp3 import MP3
from moviepy.editor import AudioFileClip
from pytube import YouTube
from pytube import Playlist
import shutil
import drive_sync
from tktooltip import ToolTip

selected_folder = ''
current_playing_song = {}
paused = False
playing = False
muted = False
progressbar_locked = False
trash_thread = False
refresh_songs_after_update = False
panel_visible = False
focus_flag = False
shuffle_flag_dict = {}
repeat_flag = None
folder_list = None
entry = None
progress_info = None
volume_info = None
progressbar = None
shuffle_button = None
log_field = None
entry_var = None
song_list = []
songs = {}
song_length = 0
current_time = 0
current_time_static = 0
vol_tmp = 0.5
pygame.mixer.init()


def toggle_panel(panel):
    global panel_visible
    if panel_visible:
        panel.withdraw()
        panel_visible = False
    else:
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        panel.geometry(f'400x760+{root_x + 1083}+{root_y + 27}')
        panel.deiconify()
        panel_visible = True


def on_move(event, panel):
    if panel_visible:
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        panel.geometry(f'400x760+{root_x + 1083}+{root_y + 27}')


def main_focus_in(event, panel):
    if panel_visible:
        panel.deiconify()
        root.focus()


def side_focus_in(event, panel):
    if panel_visible:
        panel.deiconify()
        panel.lift()


def on_iconify(event, panel):
    if panel_visible:
        panel.withdraw()


def on_deiconify(event, panel):
    if panel_visible:
        panel.deiconify()


def insert_log(text, color=None):
    log_field.insert(tk.END, f'{text}\n\n', color)
    log_field.see(tk.END)


def on_copy(event):
    try:
        selected_text = log_field.get(tk.SEL_FIRST, tk.SEL_LAST)
        if selected_text:
            root.clipboard_clear()
            root.clipboard_append(selected_text)
    except:
        pass


def filter_songs(var):
    try:
        if not var.get():
            songs_tmp = []
            for song in os.listdir(f'Songs/{selected_folder}'):
                name, ext = os.path.splitext(song)
                if ext == '.mp3':
                    songs_tmp.append(song)
            songs[selected_folder] = songs_tmp
            song_list.delete(0, 'end')
            try:
                if shuffle_flag_dict[selected_folder]:
                    random.shuffle(songs[selected_folder])
            except:
                pass
            for song in songs[selected_folder]:
                song_list.insert('end', song.replace('.mp3', ''))
            return
        song_list.delete(0, 'end')
        songs_tmp = []
        for song in os.listdir(f'Songs/{selected_folder}'):
            name, ext = os.path.splitext(song)
            if ext == '.mp3' and var.get().lower() in song.lower():
                songs_tmp.append(song)
        songs[selected_folder] = songs_tmp
        try:
            if shuffle_flag_dict[selected_folder]:
                random.shuffle(songs[selected_folder])
        except:
            pass
        for song in songs[selected_folder]:
            song_list.insert('end', song.replace('.mp3', ''))
    except Exception as e:
        print(e)
        pass



def main_GUI():
    global song_list, progress_info, progressbar, folder_list, songs, shuffle_button, repeat_flag, volume_info, log_field, entry_var

    root.title('Music Project')
    root.iconbitmap('Additional/icons/music-player.ico')

    root.tk.call('lappend', 'auto_path', os.getcwd())
    root.tk.call('package', 'require', 'awdark')
    Style().theme_use('awdark')
    style = Style()
    style.theme_use('awdark')
    style.configure('My.TButton', font=('Miriam Libre', 14, 'bold'), borderwidth='0')
    style.map('My.TButton', foreground=[('active', '!disabled', 'blue'), ('!disabled', 'lime')], background=[('active', 'black')])
    bg_color = style.lookup('TFrame', 'background')

    panel = Toplevel(root)
    panel.withdraw()
    panel.overrideredirect(True)
    panel.geometry('400x600')
    panel.resizable(False, False)
    log_frame = Frame(panel)
    log_frame.place(relx=0.001, rely=-0.001, relwidth=1, relheight=1.002)
    log_field = Text(log_frame)
    log_field.place(relx=0.01, rely=0.01, relwidth=0.957, relheight=0.98)
    scrollbar_log_field = Scrollbar(log_frame, orient=tk.VERTICAL, command=log_field.yview)
    log_field.config(yscrollcommand=scrollbar_log_field.set)
    scrollbar_log_field.place(relx=0.95, rely=0.002, relheight=0.995, relwidth=0.05)
    log_field.config(font=("Courier", 13))
    log_field.config(state="normal", wrap=tk.WORD)
    log_field.tag_configure("yellow_text", foreground="yellow")
    log_field.tag_configure("red_text", foreground="red")
    log_field.tag_configure("green_text", foreground="green")

    root.bind("<Control-c>", on_copy)

    root.bind('<Configure>', lambda event: on_move(event, panel))
    root.bind("<FocusIn>", lambda event: side_focus_in(event, panel))
    panel.bind("<FocusIn>", lambda event: main_focus_in(event, panel))
    root.bind('<Unmap>', lambda event: on_iconify(event, panel))
    root.bind('<Map>', lambda event: on_deiconify(event, panel))

    upper_main_frame = LabelFrame(root)
    upper_main_frame.place(relx=0, rely=0, relwidth=1, relheight=.15)

    middle_main_frame = LabelFrame(root)
    middle_main_frame.place(relx=0, rely=.15, relwidth=1, relheight=.78)

    middle_left_frame = Label(middle_main_frame, text='Folders', padding=5)
    middle_left_frame.place(relx=0, rely=0, relwidth=.3, relheight=1)

    middle_right_frame = Label(middle_main_frame, text='Songs', padding=5)
    middle_right_frame.place(relx=.3, rely=0, relwidth=.7, relheight=1)

    middle_left_frame.columnconfigure(0, weight=1)
    middle_left_frame.rowconfigure(0, weight=1)

    middle_right_frame.columnconfigure(0, weight=1)
    middle_right_frame.rowconfigure(0, weight=1)

    lower_main_frame = Label(root)
    lower_main_frame.place(relx=0, rely=.93, relwidth=.22, relheight=.07)

    lower_side_frame = Label(root)
    lower_side_frame.place(relx=.22, rely=.93, relwidth=.78, relheight=.07)

    folder_list = Listbox(middle_left_frame, fg='white', selectbackground='lime', selectforeground='black', exportselection=False, font=('Miriam Libre', 12))
    folder_list.grid(row=0, column=0, padx=0, pady=0, sticky='news')

    song_list = Listbox(middle_right_frame, fg='white', selectbackground='lime', selectforeground='black', exportselection=False, font=('Miriam Libre', 12))
    song_list.grid(row=0, column=0, padx=0, pady=0, sticky='news')
    song_list.bind('<Double-Button>', play_music)

    scrollbar_songs = Scrollbar(middle_right_frame)
    scrollbar_songs.grid(row=0, column=1, sticky='ns')

    song_list.config(yscrollcommand=scrollbar_songs.set)
    scrollbar_songs.config(command=song_list.yview)

    for folder in os.listdir('Songs'):
        folder_list.insert('end', folder)
        songs_tmp = []
        for song in os.listdir(f'Songs/{folder}'):
            name, ext = os.path.splitext(song)
            if ext == '.mp3':
                songs_tmp.append(song)
        songs[folder] = songs_tmp
    folder_list.bind('<<ListboxSelect>>', change_folder)

    scrollbar_folder = Scrollbar(middle_left_frame)
    scrollbar_folder.grid(row=0, column=1, sticky='ns')

    folder_list.config(yscrollcommand=scrollbar_folder.set)
    scrollbar_folder.config(command=folder_list.yview)

    add_new_song_image = Image.open('Additional/icons/download-music.png').resize((60, 60))
    rename_song_image = Image.open('Additional/icons/edit.png').resize((60, 60))
    delete_song_image = Image.open('Additional/icons/delete-track.png').resize((60, 60))
    move_song_image = Image.open('Additional/icons/move-track.png').resize((60, 60))
    new_folder_image = Image.open('Additional/icons/add-folder.png').resize((60, 60))
    delete_folder_image = Image.open('Additional/icons/delete-folder.png').resize((60, 60))
    sync_image = Image.open('Additional/icons/data-synchronization.png').resize((60, 60))
    log_image = Image.open('Additional/icons/log.png').resize((60, 60))

    previous_image = Image.open('Additional/icons/previous-track.png').resize((40, 40))
    play_image = Image.open('Additional/icons/pause-play.png').resize((40, 40))
    next_image = Image.open('Additional/icons/next-track.png').resize((40, 40))
    volume_image = Image.open('Additional/icons/sound-button.png').resize((40, 40))

    shuffle_image = Image.open('Additional/icons/shuffle.png').resize((26, 28))
    unshuffle_image = Image.open('Additional/icons/unshuffle.png').resize((26, 28))
    repeat_on_image = Image.open('Additional/icons/repeat_on.png').resize((30, 29))
    repeat_off_image = Image.open('Additional/icons/repeat_off.png').resize((30, 29))

    root.add_new_song_btn_image = ImageTk.PhotoImage(add_new_song_image)
    root.rename_song_btn_image = ImageTk.PhotoImage(rename_song_image)
    root.delete_song_btn_image = ImageTk.PhotoImage(delete_song_image)
    root.move_song_btn_image = ImageTk.PhotoImage(move_song_image)
    root.new_folder_btn_image = ImageTk.PhotoImage(new_folder_image)
    root.delete_folder_btn_image = ImageTk.PhotoImage(delete_folder_image)
    root.sync_btn_image = ImageTk.PhotoImage(sync_image)
    root.log_btn_image = ImageTk.PhotoImage(log_image)

    root.previous_btn_image = ImageTk.PhotoImage(previous_image)
    root.play_btn_image = ImageTk.PhotoImage(play_image)
    root.next_btn_image = ImageTk.PhotoImage(next_image)
    root.volume_btn_image = ImageTk.PhotoImage(volume_image)

    root.shuffle_btn_image = ImageTk.PhotoImage(shuffle_image)
    root.unshuffle_btn_image = ImageTk.PhotoImage(unshuffle_image)
    root.repeat_on_btn_image = ImageTk.PhotoImage(repeat_on_image)
    root.repeat_off_btn_image = ImageTk.PhotoImage(repeat_off_image)

    add_new_song_btn = Button(upper_main_frame, image=root.add_new_song_btn_image, command=lambda: download_song_window())
    rename_song_btn = Button(upper_main_frame, image=root.rename_song_btn_image, command=lambda: create_rename_song_window(selected_folder))
    delete_song_btn = Button(upper_main_frame, image=root.delete_song_btn_image, command=delete_song)
    move_song_btn = Button(upper_main_frame, image=root.move_song_btn_image, command=move_song_window)
    new_folder_btn = Button(upper_main_frame, image=root.new_folder_btn_image, command=lambda: create_directory_window())
    delete_folder_btn = Button(upper_main_frame, image=root.delete_folder_btn_image, command=delete_folder)
    sync_btn = Button(upper_main_frame, image=root.sync_btn_image, command=cloud_sync_window)
    log_btn = Button(upper_main_frame, image=root.log_btn_image, command=lambda: toggle_panel(panel))

    ToolTip(add_new_song_btn, msg="Download song", follow=True, delay=0.5)
    ToolTip(rename_song_btn, msg="Rename song", follow=True, delay=0.5)
    ToolTip(delete_song_btn, msg="Delete song", follow=True, delay=0.5)
    ToolTip(move_song_btn, msg="Move song", follow=True, delay=0.5)
    ToolTip(new_folder_btn, msg="New folder", follow=True, delay=0.5)
    ToolTip(delete_folder_btn, msg="Delete folder", follow=True, delay=0.5)
    ToolTip(sync_btn, msg="Synchronize with cloud", follow=True, delay=0.5)
    ToolTip(log_btn, msg="Logs", follow=True, delay=0.5)

    previous_btn = Button(lower_main_frame, image=root.previous_btn_image, command=prev_music)
    next_btn = Button(lower_main_frame, image=root.next_btn_image, command=next_music)
    play_btn = Button(lower_main_frame, image=root.play_btn_image, command=play_music)
    volume_btn = Button(lower_main_frame, image=root.volume_btn_image, command=mute_song)

    add_new_song_btn.grid(row=0, column=0, padx=10, pady=10)
    rename_song_btn.grid(row=0, column=1, padx=10, pady=10)
    delete_song_btn.grid(row=0, column=2, padx=10, pady=10)
    move_song_btn.grid(row=0, column=3, padx=10, pady=10)
    new_folder_btn.grid(row=0, column=4, padx=10, pady=10)
    delete_folder_btn.grid(row=0, column=5, padx=10, pady=10)
    sync_btn.grid(row=0, column=6, padx=10, pady=10)
    log_btn.grid(row=0, column=7, padx=10, pady=10, sticky='e')
    upper_main_frame.columnconfigure(7, weight=1)

    previous_btn.grid(row=0, column=0, padx=0, pady=2)
    next_btn.grid(row=0, column=2, padx=0, pady=2)
    play_btn.grid(row=0, column=1, padx=0, pady=2)
    volume_btn.grid(row=0, column=3, padx=11, pady=2)

    progress_info = Label(lower_side_frame, text='00:00/00:00', foreground='lime', font=('Miriam Libre', 10))
    progress_info.grid(row=0, column=1, padx=5, pady=3, sticky='es')

    volume_info = Label(lower_side_frame, text=f'Vol: {int(vol_tmp*100)}', foreground='lime', font=('Miriam Libre', 12))
    volume_info.grid(row=0, column=0, padx=10, pady=7, sticky='ws')

    info_search = Label(lower_side_frame, text='Search:', foreground='lime', font=('Miriam Libre', 11))
    info_search.grid(row=0, column=0, padx=3, pady=5, sticky='nse')

    progressbar = Scale(lower_side_frame, from_=0, to=100, orient=HORIZONTAL, value=0, length=570)
    progressbar.bind("<Button-1>", lock_progressbar)
    progressbar.bind("<ButtonRelease-1>", progress)
    progressbar.grid(row=1, column=1, padx=5, pady=5, sticky='news')

    vol = Scale(lower_side_frame, from_=0, to=100, orient=HORIZONTAL, value=50, length=140, command=lambda value: volume_change(value))
    vol.grid(row=1, column=0, padx=10, pady=5, sticky='news')

    repeat_flag = BooleanVar()
    repeat_checkbox = tk.Checkbutton(lower_side_frame, image=root.repeat_off_btn_image, selectimage=root.repeat_on_btn_image, indicatoron=False, onvalue=1, offvalue=0, variable=repeat_flag, relief='flat', bd=0, bg=bg_color, activebackground=bg_color, selectcolor=bg_color)
    repeat_checkbox.grid(row=1, column=2, padx=1, pady=0, sticky='new')
    root.bind_all("<Button-1>", lambda event: event.widget.focus_set())
    entry_var = StringVar()
    entry_var.trace("w", lambda name, index, mode, var=entry_var: filter_songs(var))
    entry_filter = Entry(lower_side_frame, width=60, font=('Miriam Libre', 10), foreground='deep pink2', textvariable=entry_var)
    entry_filter.grid(row=0, column=1, padx=4, pady=5, sticky='wsn')

    shuffle_button = tk.Button(lower_side_frame, image=root.unshuffle_btn_image, bd=0, highlightthickness=0, bg=bg_color, activebackground=bg_color, command=shuffle_music)
    shuffle_button.grid(row=0, column=2, padx=5, pady=0, sticky='news')

    lower_side_frame.columnconfigure(0, weight=1)
    lower_side_frame.columnconfigure(1, weight=1)
    lower_side_frame.columnconfigure(2, weight=1)
    lower_side_frame.rowconfigure(0, weight=1)
    lower_side_frame.rowconfigure(1, weight=1)


def download_song_window():
    global entry

    if hasattr(root, 'download_song') and root.download_song:
        root.download_song.destroy()

    root.download_song = tk.Toplevel(root)
    root.download_song.withdraw()
    root.download_song.title("Download Song")
    root.download_song.iconbitmap('Additional/icons/music-player.ico')
    root.download_song.geometry('500x480+200+300')
    root.download_song.resizable(False, False)

    root.download_song.tk.call('lappend', 'auto_path', os.getcwd())
    root.download_song.tk.call('package', 'require', 'awdark')

    root.download_song.deiconify()

    main_frame = Frame(root.download_song)
    main_frame.place(relx=0, rely=0, relwidth=1, relheight=0.8)

    main_frame.columnconfigure(0, weight=1)

    side_frame = Frame(root.download_song)
    side_frame.place(relx=0, rely=0.8, relwidth=1, relheight=0.2)

    folder_list_yt = Listbox(main_frame, fg='white', selectbackground='lime', selectforeground='black', exportselection=False, font=('Miriam Libre', 12))
    folder_list_yt.grid(row=0, column=0, padx=0, pady=5, sticky='news')

    scrollbar_folder = Scrollbar(main_frame)
    scrollbar_folder.grid(row=0, column=1, sticky='ns', pady=5)

    folder_list_yt.config(yscrollcommand=scrollbar_folder.set)
    scrollbar_folder.config(command=folder_list_yt.yview)

    local_dir_list = os.listdir('Songs')
    for folder in local_dir_list:
        folder_list_yt.insert('end', folder)
    folder_list_yt.selection_set(0)

    label = Label(main_frame, text='Enter youtube URL', font=('Miriam Libre', 14), foreground='lime')
    label.grid(row=1, column=0, padx=150, pady=30, sticky='news')

    entry = Entry(main_frame, width=40, font=('Miriam Libre', 14), foreground='deep pink2')
    entry.grid(row=2, column=0, padx=20, pady=10, sticky='news')
    entry.focus()
    root.download_song.bind('<FocusIn>', lambda event: on_focus_in(event, entry))

    playlist_checkbox = BooleanVar()
    Checkbutton(side_frame, text='', variable=playlist_checkbox).grid(row=0, column=1, padx=95, pady=0, sticky='e')

    label = Label(side_frame, text='Playlist', font=('Miriam Libre', 11), foreground='lime')
    label.grid(row=0, column=1, padx=40, pady=10, sticky='e')

    root.download_song.bind('<Return>', lambda event: create_thread_youtube_audio_download(youtube_audio_download, video_url=entry.get(), download_dir=[local_dir_list, folder_list_yt.curselection()],
                                                                                           playlist=playlist_checkbox))
    download_song_btn = Button(side_frame, text='Download', style='My.TButton', command=lambda: create_thread_youtube_audio_download(youtube_audio_download, video_url=entry.get(), download_dir=[local_dir_list, folder_list_yt.curselection()], playlist=playlist_checkbox))
    download_song_btn.grid(row=0, column=0, padx=20, pady=30, sticky='we')

    side_frame.columnconfigure(0, weight=1)
    side_frame.columnconfigure(1, weight=1)


def create_thread_youtube_audio_download(target_script, **kwargs):
    global entry
    try:
        thread_count = 5
        if trash_thread:
            thread_count = 6
        if threading.active_count() <= thread_count:
            thread = threading.Thread(target=target_script, args=kwargs.values(), daemon=True)
            thread.start()
        else:
            entry.delete(0, tk.END)
            insert_log(f'Threading Error for\n{kwargs['video_url']}\nTry later', 'yellow_text')
            pass
    except Exception as e:
        insert_log(f'{e} in create_thread_youtube_audio_download function', 'red_text')
        pass


def youtube_audio_download(video_url, download_dir_list, playlist):
    global song_list, entry, trash_thread, songs
    entry.delete(0, tk.END)
    try:
        download_dir = download_dir_list[0][download_dir_list[-1][0]]
    except:
        entry.insert(0, 'No folder detected...')
        return
    try:
        folder_tmp = folder_list.curselection()[0]
    except:
        pass

    if playlist.get() == 1:
        videos = Playlist(video_url)
        for video in videos.videos:
            try:
                audio = video.streams.filter(only_audio=True).order_by('abr').desc().first()
                info = video.vid_info
                full_title = (info['videoDetails']['author'] + ' - ' + info['videoDetails']['title']).replace('"', '').replace('.', '').replace('*', '').replace(':', '').replace('/', '').replace('\\', '').replace('|', '').replace('<', '').replace('>', '').replace('?', '')
                downloaded_file = audio.download(f'Songs/{download_dir}')
                mp3_file = f'Songs/{download_dir}/{full_title}' + '.mp3'
                audio_clip = AudioFileClip(downloaded_file)
                audio_clip.write_audiofile(mp3_file)
                audio_clip.close()
                os.remove(downloaded_file)
                insert_log(f'{full_title} downloaded successfully', 'green_text')
                try:
                    songs[download_dir].append(full_title + '.mp3')
                    songs[download_dir] = list(set(songs[download_dir]))
                    if folder_tmp == folder_list.curselection()[0]:
                        change_folder()
                except:
                    pass
            except Exception as e:
                insert_log(f"Failed to download {full_title} - {e}", 'red_text')
    else:
        try:
            video = YouTube(video_url, use_oauth=True)
            audio = video.streams.filter(only_audio=True).order_by('abr').desc().first()
            info = video.vid_info
            full_title = (info['videoDetails']['author'] + ' - ' + info['videoDetails']['title']).replace('"', '').replace('.', '').replace('*', '').replace(':', '').replace('/', '').replace('\\', '').replace('|', '').replace('<', '').replace('>', '').replace('?', '')
            downloaded_file = audio.download(f'Songs/{download_dir}')
            mp3_file = f'Songs/{download_dir}/{full_title}' + '.mp3'
            audio_clip = AudioFileClip(downloaded_file)
            audio_clip.write_audiofile(mp3_file)
            audio_clip.close()
            os.remove(downloaded_file)
            insert_log(f'{full_title} downloaded successfully', 'green_text')
            try:
                songs[download_dir].append(full_title + '.mp3')
                songs[download_dir] = list(set(songs[download_dir]))
                if folder_tmp == folder_list.curselection()[0]:
                    change_folder()
            except:
                pass
        except Exception as e:
            try:
                insert_log(f"Failed to download {full_title} - {e}", 'red_text')
            except:
                insert_log(f"Failed to download - {e}", 'red_text')
    trash_thread = True


def create_rename_song_window(current_folder):
    try:
        song_to_rename = songs[selected_folder][song_list.curselection()[0]].replace('.mp3', '')
    except:
        insert_log('No selected song for rename', 'yellow_text')
        return
    if hasattr(root, 'rename_song') and root.rename_song:
        root.rename_song.destroy()

    root.rename_song = tk.Toplevel(root)
    root.rename_song.withdraw()
    root.rename_song.title("Rename Song")
    root.rename_song.iconbitmap('Additional/icons/music-player.ico')
    root.rename_song.geometry('500x150+200+300')
    root.rename_song.resizable(False, False)

    root.rename_song.tk.call('lappend', 'auto_path', os.getcwd())
    root.rename_song.tk.call('package', 'require', 'awdark')

    root.rename_song.deiconify()

    main_frame = Frame(root.rename_song)
    main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    main_frame.columnconfigure(0, weight=1)

    entry = Entry(main_frame, width=40, font=('Miriam Libre', 14), foreground='deep pink2')
    entry.grid(row=0, column=0, padx=20, pady=30, sticky='news')
    entry.insert(0, song_to_rename)
    entry.focus()
    root.rename_song.bind('<FocusIn>', lambda event: on_focus_in(event, entry))

    download_song_btn = Button(main_frame, text='Rename', style='My.TButton', command=lambda: rename_song(current_folder, song_to_rename + '.mp3', entry.get()))
    download_song_btn.grid(row=1, column=0, padx=20, pady=0, sticky='')


def rename_song(current_folder, old_name, new_name):
    global playing, songs

    if new_name + '.mp3' in songs[current_folder]:
        insert_log(f"{new_name + '.mp3'} already exists", 'yellow_text')
        root.rename_song.destroy()
        return

    if (playing or paused) and old_name == current_playing_song['song']:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        playing = False
        pygame.mixer.init()

    os.rename(f'Songs/{current_folder}/{old_name}', f"Songs/{current_folder}/{new_name + '.mp3'}")
    songs[current_folder][songs[current_folder].index(old_name)] = new_name + '.mp3'
    change_folder()
    insert_log(f"{old_name} has been renamed to {new_name + '.mp3'}", 'green_text')
    root.rename_song.destroy()
    if song_list.curselection()[0] == 0:
        song_list.selection_clear(0)
        song_list.selection_set(songs[current_folder].index(new_name + '.mp3'))
        song_list.see(songs[current_folder].index(new_name + '.mp3'))


def delete_song():
    global song_list, playing, songs
    try:
        answer = messagebox.askquestion(title='Delete?!', message=f'Are you sure you want to delete the track\n{songs[selected_folder][song_list.curselection()[0]]}?', type=messagebox.YESNO)
        if answer == 'no':
            return
        if (playing or paused) and songs[selected_folder][song_list.curselection()[0]] == current_playing_song['song']:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            playing = False
            pygame.mixer.init()
        os.remove(f'Songs/{selected_folder}/{songs[selected_folder][song_list.curselection()[0]]}')
        insert_log(f"{songs[selected_folder][song_list.curselection()[0]]} has been deleted", 'green_text')
        pygame.mixer.init()
        try:
            songs[selected_folder].remove(songs[selected_folder][song_list.curselection()[0]])
            change_folder()
        except:
            song_list.selection_set(len(songs[selected_folder]) - 1)
            song_list.see(len(songs[selected_folder]) - 1)
            pass
    except:
        pass


def move_song_window():
    try:
        song_name = songs[selected_folder][song_list.curselection()[0]]
        old_folder = os.listdir('Songs')[folder_list.curselection()[0]]

        if hasattr(root, 'move_song') and root.move_song:
            root.move_song.destroy()

        root.move_song = tk.Toplevel(root)
        root.move_song.withdraw()
        root.move_song.title("Move Song")
        root.move_song.iconbitmap('Additional/icons/music-player.ico')
        root.move_song.geometry('400x300+200+300')
        root.move_song.resizable(False, False)

        root.move_song.tk.call('lappend', 'auto_path', os.getcwd())
        root.move_song.tk.call('package', 'require', 'awdark')

        root.move_song.deiconify()

        main_frame = Frame(root.move_song)
        main_frame.place(relx=0, rely=0, relwidth=1, relheight=.8)

        main_frame.columnconfigure(0, weight=1)

        side_frame = Frame(root.move_song)
        side_frame.place(relx=0, rely=.8, relwidth=1, relheight=.2)

        folder_list_ms = Listbox(main_frame, fg='white', selectbackground='lime', selectforeground='black', exportselection=False, font=('Miriam Libre', 12))
        folder_list_ms.grid(row=0, column=0, padx=0, pady=0, sticky='news')

        local_dir_list = os.listdir('Songs')
        for folder in local_dir_list:
            folder_list_ms.insert('end', folder)
        folder_list_ms.selection_set(0)

        scrollbar_folder = Scrollbar(main_frame)
        scrollbar_folder.grid(row=0, column=1, sticky='ns')

        folder_list_ms.config(yscrollcommand=scrollbar_folder.set)
        scrollbar_folder.config(command=folder_list_ms.yview)

        move_song_btn = Button(side_frame, text='Move Song', style='My.TButton', command=lambda: move_song(local_dir_list[folder_list_ms.curselection()[0]], old_folder, song_name))
        move_song_btn.grid(row=0, column=0, padx=130, pady=3)
    except:
        pass


def move_song(new_folder, old_folder, song_name):
    global playing, songs
    try:
        shutil.move(f'Songs/{old_folder}/{song_name}', f'Songs/{new_folder}/{song_name}')
        insert_log(f"{song_name} has been moved form {old_folder} to {new_folder}", 'green_text')
        songs[old_folder].remove(song_name)
        songs[new_folder].append(song_name)
        songs[new_folder] = list(set(songs[new_folder]))
        change_folder()

        if hasattr(root, 'move_song') and root.move_song:
            root.move_song.destroy()

    except:
        if playing:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            playing = False
            pygame.mixer.init()
            shutil.move(f'Songs/{old_folder}/{song_name}', f'Songs/{new_folder}/{song_name}')
            insert_log(f"{song_name} has been moved form {old_folder} to {new_folder}", 'green_text')
            songs[old_folder].remove(song_name)
            songs[new_folder].append(song_name)
            songs[new_folder] = list(set(songs[new_folder]))
            change_folder()

            if hasattr(root, 'move_song') and root.move_song:
                root.move_song.destroy()


def create_directory_window():

    if hasattr(root, 'add_dir') and root.add_dir:
        root.add_dir.destroy()

    root.add_dir = tk.Toplevel(root)
    root.add_dir.withdraw()
    root.add_dir.title("Create Directory")
    root.add_dir.iconbitmap('Additional/icons/music-player.ico')
    root.add_dir.geometry('500x250+200+300')
    root.add_dir.resizable(False, False)

    root.add_dir.tk.call('lappend', 'auto_path', os.getcwd())
    root.add_dir.tk.call('package', 'require', 'awdark')

    root.add_dir.deiconify()

    main_frame = Frame(root.add_dir)
    main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    label = Label(main_frame, text='Enter a folder name', font=('Miriam Libre', 14), foreground='lime')
    label.grid(row=0, column=0, padx=150, pady=30, sticky='news')

    entry_directory_window = Entry(main_frame, width=40, font=('Miriam Libre', 14), foreground='deep pink2')
    entry_directory_window.grid(row=1, column=0, padx=20, pady=10, sticky='news')
    entry_directory_window.focus()

    create_dir_btn = Button(main_frame, text='Create', style='My.TButton', command=lambda: create_directory(entry_directory_window.get()))
    create_dir_btn.grid(row=2, column=0, padx=20, pady=30)


def create_directory(path):
    global folder_list, songs
    directory = f'Songs/{path}'
    if not os.path.exists(directory):
        os.makedirs(directory)
        insert_log(f"{directory} has been created", 'green_text')
        songs[path] = []
        folder_list.delete(0, 'end')
        for folder in os.listdir('Songs'):
            folder_list.insert('end', folder)
        try:
            folder_list.selection_set(os.listdir('Songs').index(selected_folder))
        except:
            pass
    root.add_dir.destroy()


def delete_folder():
    global folder_list, selected_folder, playing
    if selected_folder != '':
        answer = messagebox.askquestion(title='Delete?!', message=f'Are you sure you want to delete the folder\n{selected_folder}?', type=messagebox.YESNO)
        if answer == 'yes':
            current_folder_tmp = folder_list.curselection()[0]
            folder_list.delete(0, 'end')
            try:
                shutil.rmtree(f'Songs/{selected_folder}')
                insert_log(f"{selected_folder} has been removed", 'green_text')
            except:
                pygame.mixer.music.stop()
                playing = False
                pygame.mixer.quit()
                shutil.rmtree(f'Songs/{selected_folder}')
                insert_log(f"{selected_folder} has been removed", 'green_text')
                pygame.mixer.init()
            for folder in os.listdir('Songs'):
                folder_list.insert('end', folder)
            try:
                folder_list.selection_set(current_folder_tmp)
                selected_folder = folder_list.get(folder_list.curselection()[0])
                change_folder()
            except:
                try:
                    folder_list.selection_set(current_folder_tmp-1)
                    selected_folder = folder_list.get(folder_list.curselection()[0])
                    change_folder()
                except:
                    selected_folder = ''


def cloud_sync_window():
    delete_flag = BooleanVar()

    if hasattr(root, 'cloud_sync') and root.cloud_sync:
        root.cloud_sync.destroy()

    root.cloud_sync = tk.Toplevel(root)
    root.cloud_sync.withdraw()
    root.cloud_sync.title("Download Song")
    root.cloud_sync.iconbitmap('Additional/icons/music-player.ico')
    root.cloud_sync.geometry('450x220+200+300')
    root.cloud_sync.resizable(False, False)

    root.cloud_sync.tk.call('lappend', 'auto_path', os.getcwd())
    root.cloud_sync.tk.call('package', 'require', 'awdark')
    style = Style()
    style.theme_use('awdark')
    bg_color = style.lookup('TFrame', 'background')

    root.cloud_sync.deiconify()

    main_frame = Frame(root.cloud_sync)
    main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    cloud_upload_image = Image.open('Additional/icons/cloud-upload.png').resize((120, 120))
    cloud_download_image = Image.open('Additional/icons/cloud-download.png').resize((120, 120))
    on_image = Image.open('Additional/icons/on-button.png').resize((60, 60))
    off_image = Image.open('Additional/icons/off-button.png').resize((60, 60))

    root.cloud_upload_bnt_image = ImageTk.PhotoImage(cloud_upload_image)
    root.cloud_download_btn_image = ImageTk.PhotoImage(cloud_download_image)
    root.on_bnt_image = ImageTk.PhotoImage(on_image)
    root.off_btn_image = ImageTk.PhotoImage(off_image)

    cloud_upload_bnt = Button(main_frame, image=root.cloud_upload_bnt_image, command=lambda: create_thread_drive_sync(drive_sync.upload_list, wind=root.cloud_sync, delete_flag=delete_flag.get(), folder_list=folder_list, song_list=song_list, log_field=log_field))
    cloud_download_btn = Button(main_frame, image=root.cloud_download_btn_image, command=lambda: create_thread_drive_sync(drive_sync.download_list, wind=root.cloud_sync, delete_flag=delete_flag.get(), folder_list=folder_list, song_list=song_list, log_field=log_field))
    delete_checkbox = tk.Checkbutton(main_frame, image=root.off_btn_image, selectimage=root.on_bnt_image, indicatoron=False, onvalue=1, offvalue=0, variable=delete_flag, relief='flat', bd=0, bg=bg_color, activebackground=bg_color, selectcolor=bg_color)

    ToolTip(cloud_upload_bnt, msg="Upload", follow=True, delay=0.5)
    ToolTip(cloud_download_btn, msg="Download", follow=True, delay=0.5)

    cloud_upload_bnt.grid(row=0, column=0, padx=10, pady=10)
    cloud_download_btn.grid(row=0, column=1, padx=10, pady=10)
    delete_checkbox.grid(row=1, column=1, padx=0, pady=0, sticky='ns')

    label = Label(main_frame, text='Delete not matches?', font=('Miriam Libre', 14), foreground='lime')
    label.grid(row=1, column=0, padx=0, pady=0, sticky='nes')


def create_thread_drive_sync(target_script, **kwargs):
    global playing, refresh_songs_after_update
    try:
        thread_count = 1
        if trash_thread:
            thread_count = 2
        if threading.active_count() <= thread_count:
            try:
                if target_script.__name__ == 'download_list' and kwargs['delete_flag']:
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
                    playing = False
                    pygame.mixer.init()
                thread = threading.Thread(target=target_script, args=kwargs.values(), daemon=True)
                thread.start()
            except:
                pass
        else:
            pass
        refresh_songs_after_update = True
    except Exception as e:
        insert_log(f'{e} in create_thread_drive_sync function', 'red_text')


def prev_music():
    global song_list, song_length, current_time_static, current_playing_song
    try:
        try:
            if current_playing_song['folder'] == selected_folder:
                song_list.selection_set(song_list.curselection()[0] - 1)
                song_list.see(song_list.curselection()[0] - 1)
                song_list.selection_clear(song_list.curselection()[0] + 1)
                if playing and not paused:
                    current_playing_song['song'] = songs[selected_folder][song_list.curselection()[0]]
                    pygame.mixer.music.load(os.path.join(f'Songs/{selected_folder}', current_playing_song['song']))
                    pygame.mixer.music.play(loops=0)
                    song_length = MP3(f'Songs/{selected_folder}/{current_playing_song['song']}').info.length
                    current_time_static = 0
                    play_time()
            else:
                if playing and not paused:
                    current_playing_song['song'] = songs[current_playing_song['folder']][songs[current_playing_song['folder']].index(current_playing_song['song']) - 1]
                    pygame.mixer.music.load(os.path.join(f'Songs/{current_playing_song['folder']}', current_playing_song['song']))
                    pygame.mixer.music.play(loops=0)
                    song_length = MP3(f'Songs/{current_playing_song['folder']}/{current_playing_song['song']}').info.length
                    current_time_static = 0
                    play_time()
                else:
                    song_list.selection_set(song_list.curselection()[0] - 1)
                    song_list.see(song_list.curselection()[0] - 1)
                    song_list.selection_clear(song_list.curselection()[0] + 1)
        except:
            if playing and not paused:
                current_playing_song['song'] = songs[current_playing_song['folder']][songs[current_playing_song['folder']].index(current_playing_song['song']) - 1]
                pygame.mixer.music.load(os.path.join(f'Songs/{current_playing_song['folder']}', current_playing_song['song']))
                pygame.mixer.music.play(loops=0)
                song_length = MP3(f'Songs/{current_playing_song['folder']}/{current_playing_song['song']}').info.length
                current_time_static = 0
                play_time()
            else:
                song_list.selection_set(song_list.curselection()[0] - 1)
                song_list.see(song_list.curselection()[0] - 1)
                song_list.selection_clear(song_list.curselection()[0] + 1)
    except:
        pass


def play_music(event=None):
    global paused, playing, song_length, current_time_static, current_playing_song
    try:
        try:
            current_palying_song_tmp = songs[selected_folder][song_list.curselection()[0]]
        except:
            current_palying_song_tmp = current_playing_song['song']
        if playing and not paused and current_playing_song['song'] == current_palying_song_tmp:
            pygame.mixer.music.pause()
            playing = False
            paused = True
        elif not playing and paused and current_playing_song['song'] == current_palying_song_tmp:
            pygame.mixer.music.unpause()
            paused = False
            playing = True
            play_time()
        else:
            current_time_static = 0
            current_playing_song['song'] = songs[selected_folder][song_list.curselection()[0]]
            pygame.mixer.music.load(os.path.join(f'Songs/{selected_folder}', current_playing_song['song']))
            pygame.mixer.music.play(loops=0)
            current_playing_song['folder'] = selected_folder
            if not muted:
                pygame.mixer.music.set_volume(vol_tmp)
            song_length = MP3(f'Songs/{selected_folder}/{current_playing_song['song']}').info.length
            playing = True
            paused = False
            play_time()
    except Exception as e:
        pass


def next_music():
    global song_list, song_length, current_time_static, current_playing_song
    try:
        if current_playing_song['folder'] == selected_folder:
            if current_playing_song['song'] == songs[selected_folder][-1]:
                try:
                    song_list.selection_clear(song_list.curselection()[0])
                    song_list.selection_set(0)
                    song_list.see(0)
                    if playing and not paused:
                        current_playing_song['song'] = songs[selected_folder][song_list.curselection()[0]]
                except:
                    pass
            else:
                try:
                    song_list.selection_set(song_list.curselection()[0] + 1)
                    song_list.see(song_list.curselection()[0] + 1)
                    song_list.selection_clear(song_list.curselection()[0])
                    if playing and not paused:
                        current_playing_song['song'] = songs[selected_folder][song_list.curselection()[0]]
                except:
                    pass
            if playing and not paused:
                pygame.mixer.music.load(os.path.join(f'Songs/{current_playing_song['folder']}', current_playing_song['song']))
                pygame.mixer.music.play(loops=0)
                song_length = MP3(f'Songs/{current_playing_song['folder']}/{current_playing_song['song']}').info.length
                current_time_static = 0
                play_time()
        else:
            if current_playing_song['song'] == songs[current_playing_song['folder']][-1] and playing and not paused:
                current_playing_song['song'] = songs[current_playing_song['folder']][0]
            else:
                try:
                    if playing and not paused:
                        current_playing_song['song'] = songs[current_playing_song['folder']][songs[current_playing_song['folder']].index(current_playing_song['song']) + 1]
                except:
                    pass
            if playing and not paused:
                pygame.mixer.music.load(os.path.join(f'Songs/{current_playing_song['folder']}', current_playing_song['song']))
                pygame.mixer.music.play(loops=0)
                song_length = MP3(f'Songs/{current_playing_song['folder']}/{current_playing_song['song']}').info.length
                current_time_static = 0
                play_time()
    except:
        try:
            if songs[selected_folder][song_list.curselection()[0]] == songs[selected_folder][-1]:
                song_list.selection_clear(song_list.curselection()[0])
                song_list.selection_set(0)
                song_list.see(0)
            else:
                song_list.selection_set(song_list.curselection()[0] + 1)
                song_list.see(song_list.curselection()[0] + 1)
                song_list.selection_clear(song_list.curselection()[0])
        except:
            pass
        pass


def shuffle_music():
    global vol_tmp, muted, songs, shuffle_flag_dict, shuffle_button
    try:
        shuffle_flag = shuffle_flag_dict[selected_folder]
    except:
        shuffle_flag_dict[selected_folder] = False
        shuffle_flag = False
    try:
        if not shuffle_flag:
            random.shuffle(songs[selected_folder])
            shuffle_flag_dict[selected_folder] = True
            shuffle_button.config(image=root.shuffle_btn_image)
            change_folder()
        else:
            songs[selected_folder].sort()
            shuffle_flag_dict[selected_folder] = False
            shuffle_button.config(image=root.unshuffle_btn_image)
            change_folder()
    except:
        pass


def mute_song():
    global vol_tmp, muted, volume_info
    if not muted:
        vol_tmp = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(0)
        volume_info.config(text='Vol: 0')
        muted = True
    else:
        pygame.mixer.music.set_volume(vol_tmp)
        volume_info.config(text=f'Vol: {int(vol_tmp * 100)}')
        muted = False


def change_folder(evt=None):
    global songs, song_list, selected_folder, refresh_songs_after_update, shuffle_button, shuffle_flag_dict, current_playing_song
    song_list.delete(0, 'end')
    if evt:
        try:
            w = evt.widget
            index = int(w.curselection()[0])
            value = w.get(index)
            selected_folder = value
        except:
            return
    if refresh_songs_after_update:
        for folder in os.listdir('Songs'):
            songs_tmp = []
            for song in os.listdir(f'Songs/{folder}'):
                name, ext = os.path.splitext(song)
                if ext == '.mp3':
                    songs_tmp.append(song)
            songs[folder] = songs_tmp
        current_playing_song = {}
        refresh_songs_after_update = False
        shuffle_button.config(image=root.unshuffle_btn_image)
        shuffle_flag_dict = {}
    if entry_var.get():
        songs_tmp = []
        for song in os.listdir(f'Songs/{selected_folder}'):
            name, ext = os.path.splitext(song)
            if ext == '.mp3' and entry_var.get().lower() in song.lower():
                songs_tmp.append(song)
        songs[selected_folder] = songs_tmp
        try:
            if shuffle_flag_dict[selected_folder]:
                random.shuffle(songs[selected_folder])
        except:
            pass
    for song in songs[selected_folder]:
        song_list.insert('end', song.replace('.mp3', ''))
    try:
        if shuffle_flag_dict[selected_folder]:
            shuffle_button.config(image=root.shuffle_btn_image)
        else:
            shuffle_button.config(image=root.unshuffle_btn_image)
    except:
        shuffle_button.config(image=root.unshuffle_btn_image)
    try:
        song_list.selection_set(songs[selected_folder].index(current_playing_song['song']))
        song_list.see(songs[selected_folder].index(current_playing_song['song']))
    except:
        song_list.selection_set(0)
        song_list.see(0)


def lock_progressbar(event):
    global progressbar_locked
    progressbar_locked = True


def progress(event):
    global current_time, progress_info, progressbar, current_time_static, paused, playing, progressbar_locked
    try:
        value = progressbar.get()
        current_time_static = float(value) * 1000
        current_time = current_time_static
        pygame.mixer.music.play(start=current_time/1000)
        if paused:
            paused = False
            playing = True
            play_music()
        progressbar.config(from_=0, to=song_length-1, value=float(value))
        progress_info.config(text=f'{str(time.strftime('%M:%S', time.gmtime(float(value))))}/{str(time.strftime('%M:%S', time.gmtime(song_length-1)))}')
        progressbar_locked = False
    except:
        pass


def play_time():
    global current_time, progress_info, progressbar, song_length, current_time_static
    if playing:
        current_time = current_time_static + pygame.mixer.music.get_pos()
        progress_info.config(text=f'{str(time.strftime('%M:%S', time.gmtime(current_time/1000)))}/{str(time.strftime('%M:%S', time.gmtime(song_length-1)))}')
        if not progressbar_locked:
            progressbar.config(from_=0, to=song_length-1, value=current_time / 1000)
        if str(time.strftime('%M:%S', time.gmtime(current_time/1000))) == str(time.strftime('%M:%S', time.gmtime(song_length-1))):
            if playing and not paused and repeat_flag.get():
                pygame.mixer.music.load(os.path.join(f'Songs/{current_playing_song['folder']}', current_playing_song['song']))
                pygame.mixer.music.play(loops=0)
                song_length = MP3(f'Songs/{current_playing_song['folder']}/{current_playing_song['song']}').info.length
                current_time_static = 0
                play_time()
            else:
                next_music()
        progress_info.after(1000, play_time)


def volume_change(value):
    global vol_tmp, volume_info
    if not muted:
        if not pygame.mixer.music.get_busy():
            vol_tmp = float(value) / 100
        pygame.mixer.music.set_volume(float(value)/100)
        vol_tmp = float(value)/100

    else:
        vol_tmp = float(value)/100
    volume_info.config(text=f'Vol: {int(vol_tmp * 100)}')


def on_focus_in(event, current_entry=None):
    global entry
    if not current_entry:
        current_entry = entry
    current_entry.focus()


if __name__ == '__main__':
    try:
        if not os.path.exists('Songs'):
            os.makedirs('Songs')
        shutil.move('_internal/Additional', 'Additional')
        shutil.move('_internal/Songs', 'Songs')
        shutil.move('_internal/awthemes-10.4.0', 'awthemes-10.4.0')
    except:
        pass
    root = tk.Tk()
    root.resizable(False, False)
    root.geometry('1080x820+10+10')
    main_GUI()
    root.mainloop()
