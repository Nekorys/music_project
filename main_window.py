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

current_song = ''
current_folder = ''
paused = False
playing = False
muted = False
progressbar_locked = False
trash_thread = False
shuffle_flag = False
refresh_songs_after_update = False
folder_list = None
entry = None
progress_info = None
progressbar = None
song_list = []
songs = {}
song_length = 0
current_time = 0
current_time_static = 0
vol_tmp = 0.5
pygame.mixer.init()


def main_GUI():
    global song_list, progress_info, progressbar, folder_list, songs

    root.title('Music Project')
    root.iconbitmap('Additional/icons/music-player.ico')

    root.tk.call('lappend', 'auto_path', os.getcwd())
    root.tk.call('package', 'require', 'awdark')
    Style().theme_use('awdark')
    style = Style()
    style.theme_use('awdark')
    style.configure('My.TButton', font=('Miriam Libre', 14, 'bold'), borderwidth='0')
    style.map('My.TButton', foreground=[('active', '!disabled', 'blue'), ('!disabled', 'lime')], background=[('active', 'black')])

    upper_main_frame = LabelFrame(root)
    upper_main_frame.place(relx=0, rely=0, relwidth=1, relheight=.15)

    middle_left_frame = LabelFrame(root, text='Folders', padding=5)
    middle_left_frame.place(relx=0, rely=.15, relwidth=.3, relheight=.75)

    middle_right_frame = LabelFrame(root, text='Songs', padding=5)
    middle_right_frame.place(relx=.3, rely=.15, relwidth=.7, relheight=.75)

    middle_left_frame.columnconfigure(0, weight=1)
    middle_left_frame.rowconfigure(0, weight=1)

    middle_right_frame.columnconfigure(0, weight=1)
    middle_right_frame.rowconfigure(0, weight=1)

    lower_main_frame = LabelFrame(root)
    lower_main_frame.place(relx=0, rely=.9, relwidth=1, relheight=.1)

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
    delete_song_image = Image.open('Additional/icons/delete-track.png').resize((60, 60))
    move_song_image = Image.open('Additional/icons/move-track.png').resize((60, 60))
    new_folder_image = Image.open('Additional/icons/add-folder.png').resize((60, 60))
    delete_folder_image = Image.open('Additional/icons/delete-folder.png').resize((60, 60))
    sync_image = Image.open('Additional/icons/data-synchronization.png').resize((60, 60))

    previous_image = Image.open('Additional/icons/previous-track.png').resize((40, 40))
    play_image = Image.open('Additional/icons/pause-play.png').resize((40, 40))
    next_image = Image.open('Additional/icons/next-track.png').resize((40, 40))
    volume_image = Image.open('Additional/icons/sound-button.png').resize((40, 40))

    root.add_new_song_btn_image = ImageTk.PhotoImage(add_new_song_image)
    root.delete_song_btn_image = ImageTk.PhotoImage(delete_song_image)
    root.move_song_btn_image = ImageTk.PhotoImage(move_song_image)
    root.new_folder_btn_image = ImageTk.PhotoImage(new_folder_image)
    root.delete_folder_btn_image = ImageTk.PhotoImage(delete_folder_image)
    root.sync_btn_image = ImageTk.PhotoImage(sync_image)

    root.previous_btn_image = ImageTk.PhotoImage(previous_image)
    root.play_btn_image = ImageTk.PhotoImage(play_image)
    root.next_btn_image = ImageTk.PhotoImage(next_image)
    root.volume_btn_image = ImageTk.PhotoImage(volume_image)

    add_new_song_btn = Button(upper_main_frame, image=root.add_new_song_btn_image, command=lambda: download_song_window())
    delete_song_btn = Button(upper_main_frame, image=root.delete_song_btn_image, command=delete_song)
    move_song_btn = Button(upper_main_frame, image=root.move_song_btn_image, command=move_song_window)
    new_folder_btn = Button(upper_main_frame, image=root.new_folder_btn_image, command=lambda: create_directory_window())
    delete_folder_btn = Button(upper_main_frame, image=root.delete_folder_btn_image, command=delete_folder)
    sync_btn = Button(upper_main_frame, image=root.sync_btn_image, command=cloud_sync_window)

    previous_btn = Button(lower_main_frame, image=root.previous_btn_image, command=prev_music)
    next_btn = Button(lower_main_frame, image=root.next_btn_image, command=next_music)
    play_btn = Button(lower_main_frame, image=root.play_btn_image, command=play_music)
    volume_btn = Button(lower_main_frame, image=root.volume_btn_image, command=mute_song)

    add_new_song_btn.grid(row=0, column=0, padx=10, pady=10)
    delete_song_btn.grid(row=0, column=1, padx=10, pady=10)
    move_song_btn.grid(row=0, column=2, padx=10, pady=10)
    new_folder_btn.grid(row=0, column=3, padx=10, pady=10)
    delete_folder_btn.grid(row=0, column=4, padx=10, pady=10)
    sync_btn.grid(row=0, column=5, padx=10, pady=10)

    previous_btn.grid(row=0, column=0, padx=0, pady=0)
    next_btn.grid(row=0, column=2, padx=0, pady=0)
    play_btn.grid(row=0, column=1, padx=0, pady=0)
    volume_btn.grid(row=0, column=3, padx=10, pady=0)

    progress_info = Label(lower_main_frame, text='00:00/00:00', foreground='lime', font=('Miriam Libre', 10))
    progress_info.grid(row=0, column=5, padx=10, pady=0, sticky='s')

    progressbar = Scale(lower_main_frame, from_=0, to=100, orient=HORIZONTAL, value=0, length=570)
    progressbar.bind("<Button-1>", lock_progressbar)
    progressbar.bind("<ButtonRelease-1>", progress)
    progressbar.grid(row=0, column=6, padx=10, pady=3, sticky='s')

    vol = Scale(lower_main_frame, from_=0, to=100, orient=HORIZONTAL, value=50, length=140, command=lambda value: volume_change(value))
    vol.grid(row=0, column=4, padx=0, pady=3, sticky='s')

    lower_main_frame.columnconfigure(5, weight=1)


def download_song_window():
    global entry

    if hasattr(root, 'download_song') and root.download_song:
        root.download_song.destroy()

    root.download_song = tk.Toplevel(root)
    root.download_song.title("Download Song")
    root.download_song.iconbitmap('Additional/icons/music-player.ico')
    root.download_song.geometry('500x480+200+300')
    root.download_song.resizable(False, False)

    root.download_song.tk.call('lappend', 'auto_path', os.getcwd())
    root.download_song.tk.call('package', 'require', 'awdark')

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

    playlist_checkbox = BooleanVar()
    Checkbutton(side_frame, text="Playlist?", variable=playlist_checkbox).grid(row=0, column=1, padx=250, pady=10)

    download_song_btn = Button(side_frame, text='Download', style='My.TButton', command=lambda: create_thread_youtube_audio_download(youtube_audio_download, video_url=entry.get(), download_dir=[local_dir_list, folder_list_yt.curselection()], playlist=playlist_checkbox))
    download_song_btn.grid(row=0, column=0, padx=20, pady=30)


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
            entry.insert(0, 'Threading Error')
            pass
    except Exception as e:
        print(e)
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
                full_title = info['videoDetails']['author'] + ' - ' + info['videoDetails']['title']
                downloaded_file = audio.download(f'Songs/{download_dir}')
                mp3_file = f'Songs/{download_dir}/{full_title.replace('"', '').replace('.', '').replace('*', '').replace(':', '').replace('/', '').replace('\\', '').replace('|', '').replace('<', '').replace('>', '').replace('?', '')}' + '.mp3'
                audio_clip = AudioFileClip(downloaded_file)
                audio_clip.write_audiofile(mp3_file)
                audio_clip.close()
                os.remove(downloaded_file)
                try:
                    songs[download_dir].append(full_title.replace('"', '').replace('.', '').replace('*', '').replace(':', '').replace('/', '').replace('\\', '').replace('|', '').replace('<', '').replace('>', '').replace('?', '') + '.mp3')
                    songs[download_dir] = list(set(songs[download_dir]))
                    if folder_tmp == folder_list.curselection()[0]:
                        change_folder()
                except:
                    pass
            except Exception as e:
                print(f"Failed to download audio - {e}")
    else:
        try:
            video = YouTube(video_url, use_oauth=True)
            audio = video.streams.filter(only_audio=True).order_by('abr').desc().first()
            info = video.vid_info
            full_title = info['videoDetails']['author'] + ' - ' + info['videoDetails']['title']
            downloaded_file = audio.download(f'Songs/{download_dir}')
            mp3_file = f'Songs/{download_dir}/{full_title.replace('"', '').replace('.', '').replace('*', '').replace(':', '').replace('/', '').replace('\\', '').replace('|', '').replace('<', '').replace('>', '').replace('?', '')}' + '.mp3'
            audio_clip = AudioFileClip(downloaded_file)
            audio_clip.write_audiofile(mp3_file)
            audio_clip.close()
            os.remove(downloaded_file)
            try:
                songs[download_dir].append(full_title.replace('"', '').replace('.', '').replace('*', '').replace(':', '').replace('/', '').replace('\\', '').replace('|', '').replace('<', '').replace('>', '').replace('?', '') + '.mp3')
                songs[download_dir] = list(set(songs[download_dir]))
                if folder_tmp == folder_list.curselection()[0]:
                    change_folder()
            except:
                pass
        except Exception as e:
            print(e)
            print(f"Failed to download audio - {e}")
    trash_thread = True


def delete_song():
    global current_song, song_list, playing, songs
    try:
        if playing and songs[current_folder][song_list.curselection()[0]] == current_song:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            playing = False
        answer = messagebox.askquestion(title='Delete?!', message=f'Are you sure you want to delete the track\n{songs[current_folder][song_list.curselection()[0]]}?', type=messagebox.YESNO)
        if answer == 'no':
            pygame.mixer.init()
            return
        os.remove(f'Songs/{current_folder}/{songs[current_folder][song_list.curselection()[0]]}')
        pygame.mixer.init()
        try:
            songs[current_folder].remove(songs[current_folder][song_list.curselection()[0]])
            change_folder()
        except:
            song_list.selection_set(len(songs[current_folder]) - 1)
            pass
    except:
        pass


def move_song_window():
    try:
        song_name = songs[current_folder][song_list.curselection()[0]]
        old_folder = os.listdir('Songs')[folder_list.curselection()[0]]

        if hasattr(root, 'move_song') and root.move_song:
            root.move_song.destroy()

        root.move_song = tk.Toplevel(root)
        root.move_song.title("Move Song")
        root.move_song.iconbitmap('Additional/icons/music-player.ico')
        root.move_song.geometry('400x300+200+300')
        root.move_song.resizable(False, False)

        root.move_song.tk.call('lappend', 'auto_path', os.getcwd())
        root.move_song.tk.call('package', 'require', 'awdark')

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
    root.add_dir.title("Create Directory")
    root.add_dir.iconbitmap('Additional/icons/music-player.ico')
    root.add_dir.geometry('500x250+200+300')
    root.add_dir.resizable(False, False)

    root.add_dir.tk.call('lappend', 'auto_path', os.getcwd())
    root.add_dir.tk.call('package', 'require', 'awdark')

    main_frame = Frame(root.add_dir)
    main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    label = Label(main_frame, text='Enter a folder name', font=('Miriam Libre', 14), foreground='lime')
    label.grid(row=0, column=0, padx=150, pady=30, sticky='news')

    entry_directory_window = Entry(main_frame, width=40, font=('Miriam Libre', 14), foreground='deep pink2')
    entry_directory_window.grid(row=1, column=0, padx=20, pady=10, sticky='news')

    create_dir_btn = Button(main_frame, text='Create', style='My.TButton', command=lambda: create_directory(entry_directory_window.get()))
    create_dir_btn.grid(row=2, column=0, padx=20, pady=30)


def create_directory(path):
    global folder_list, songs
    directory = f'Songs/{path}'
    if not os.path.exists(directory):
        os.makedirs(directory)
        songs[path] = []
        folder_list.delete(0, 'end')
        for folder in os.listdir('Songs'):
            folder_list.insert('end', folder)
    root.add_dir.destroy()


def delete_folder():
    global folder_list, current_folder, playing
    if current_folder != '':
        answer = messagebox.askquestion(title='Delete?!', message=f'Are you sure you want to delete the folder\n{current_folder}?', type=messagebox.YESNO)
        if answer == 'yes':
            folder_list.delete(0, 'end')
            try:
                shutil.rmtree(f'Songs/{current_folder}')
            except:
                pygame.mixer.music.stop()
                playing = False
                pygame.mixer.quit()
                shutil.rmtree(f'Songs/{current_folder}')
                pygame.mixer.init()
            for folder in os.listdir('Songs'):
                folder_list.insert('end', folder)
            try:
                folder_list.selection_set(0)
                current_folder = folder_list.get(folder_list.curselection()[0])
                change_folder()
            except:
                current_folder = ''


def cloud_sync_window():
    delete_flag = BooleanVar()

    if hasattr(root, 'cloud_sync') and root.cloud_sync:
        root.cloud_sync.destroy()

    root.cloud_sync = tk.Toplevel(root)
    root.cloud_sync.title("Download Song")
    root.cloud_sync.iconbitmap('Additional/icons/music-player.ico')
    root.cloud_sync.geometry('450x220+200+300')
    root.cloud_sync.resizable(False, False)

    root.cloud_sync.tk.call('lappend', 'auto_path', os.getcwd())
    root.cloud_sync.tk.call('package', 'require', 'awdark')
    style = Style()
    style.theme_use('awdark')
    bg_color = style.lookup('TFrame', 'background')

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

    cloud_upload_bnt = Button(main_frame, image=root.cloud_upload_bnt_image, command=lambda: create_thread_drive_sync(drive_sync.upload_list, wind=root.cloud_sync, delete_flag=delete_flag.get(), folder_list=folder_list, song_list=song_list))
    cloud_download_btn = Button(main_frame, image=root.cloud_download_btn_image, command=lambda: create_thread_drive_sync(drive_sync.download_list, wind=root.cloud_sync, delete_flag=delete_flag.get(), folder_list=folder_list, song_list=song_list))
    delete_checkbox = tk.Checkbutton(main_frame, image=root.off_btn_image, selectimage=root.on_bnt_image, indicatoron=False, onvalue=1, offvalue=0, variable=delete_flag, relief='flat', bd=0, bg=bg_color, activebackground=bg_color, selectcolor=bg_color)

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
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                playing = False
                thread = threading.Thread(target=target_script, args=kwargs.values(), daemon=True)
                thread.start()
                pygame.mixer.init()
            except:
                pass
        else:
            pass
        refresh_songs_after_update = True
    except Exception as e:
        print(e)


def prev_music():
    global song_list, current_song, song_length, current_time_static
    try:
        try:
            song_list.selection_set(song_list.curselection()[0] - 1)
            song_list.selection_clear(song_list.curselection()[0] + 1)
            current_song = songs[current_folder][song_list.curselection()[0]]
        except:
            pass
        if playing and not paused:
            pygame.mixer.music.load(os.path.join(f'Songs/{current_folder}', current_song))
            pygame.mixer.music.play(loops=0)
            song_length = MP3(f'Songs/{current_folder}/{current_song}').info.length
            current_time_static = 0
            play_time()
    except:
        pass


def play_music(event=None):
    global current_song, paused, playing, song_length, current_time_static
    try:
        if playing and not paused and current_song == songs[current_folder][song_list.curselection()[0]]:
            pygame.mixer.music.pause()
            playing = False
            paused = True
        elif not playing and paused and current_song == songs[current_folder][song_list.curselection()[0]]:
            pygame.mixer.music.unpause()
            paused = False
            playing = True
            play_time()
        else:
            current_time_static = 0
            current_song = songs[current_folder][song_list.curselection()[0]]
            pygame.mixer.music.load(os.path.join(f'Songs/{current_folder}', current_song))
            pygame.mixer.music.play(loops=0)
            if not muted:
                pygame.mixer.music.set_volume(vol_tmp)
            song_length = MP3(f'Songs/{current_folder}/{current_song}').info.length
            playing = True
            paused = False
            play_time()
    except Exception as e:
        print(e)
        pass


def next_music():
    global song_list, current_song, song_length, current_time_static
    try:
        if songs[current_folder][song_list.curselection()[0]] == songs[current_folder][-1]:
            try:
                song_list.selection_clear(song_list.curselection()[0])
                song_list.selection_set(0)
                current_song = songs[current_folder][song_list.curselection()[0]]
            except:
                song_list.selection_set(len(songs[current_folder])-1)
                pass
        else:
            try:
                song_list.selection_set(song_list.curselection()[0] + 1)
                song_list.selection_clear(song_list.curselection()[0])
                current_song = songs[current_folder][song_list.curselection()[0]]
            except:
                song_list.selection_set(len(songs[current_folder])-1)
                pass
        if playing and not paused:
            pygame.mixer.music.load(os.path.join(f'Songs/{current_folder}', current_song))
            pygame.mixer.music.play(loops=0)
            song_length = MP3(f'Songs/{current_folder}/{current_song}').info.length
            current_time_static = 0
            play_time()
    except:
        pass


def mute_song():
    global vol_tmp, muted, songs, shuffle_flag
    if not shuffle_flag:
        random.shuffle(songs[current_folder])
        shuffle_flag = True
        change_folder()
    else:
        songs_tmp = []
        for song in os.listdir(f'Songs/{current_folder}'):
            name, ext = os.path.splitext(song)
            if ext == '.mp3':
                songs_tmp.append(song)
        songs[current_folder] = songs_tmp
        shuffle_flag = False
        change_folder()
    if not muted:
        vol_tmp = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(0)
        muted = True
    else:
        pygame.mixer.music.set_volume(vol_tmp)
        muted = False


def change_folder(evt=None):
    global songs, song_list, current_folder, refresh_songs_after_update
    song_list.delete(0, 'end')
    if evt:
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        current_folder = value

    if refresh_songs_after_update:
        for folder in os.listdir('Songs'):
            songs_tmp = []
            for song in os.listdir(f'Songs/{folder}'):
                name, ext = os.path.splitext(song)
                if ext == '.mp3':
                    songs_tmp.append(song)
            songs[folder] = songs_tmp

    for song in songs[current_folder]:
        song_list.insert('end', song.replace('.mp3', ''))
    try:
        song_list.selection_set(songs[current_folder].index(current_song))
    except:
        song_list.selection_set(0)


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
        progressbar.config(from_=0, to=song_length, value=float(value))
        progress_info.config(text=f'{str(time.strftime('%M:%S', time.gmtime(float(value))))}/{str(time.strftime('%M:%S', time.gmtime(song_length-1)))}')
        progressbar_locked = False
    except:
        pass


def play_time():
    global current_time, progress_info, progressbar
    if playing:
        current_time = current_time_static + pygame.mixer.music.get_pos()
        progress_info.config(text=f'{str(time.strftime('%M:%S', time.gmtime(current_time/1000)))}/{str(time.strftime('%M:%S', time.gmtime(song_length-1)))}')
        if not progressbar_locked:
            progressbar.config(from_=0, to=song_length, value=current_time / 1000)
        if str(time.strftime('%M:%S', time.gmtime(current_time/1000))) == str(time.strftime('%M:%S', time.gmtime(song_length-1))):
            next_music()
        progress_info.after(1000, play_time)


def volume_change(value):
    global vol_tmp
    if not muted:
        if not pygame.mixer.music.get_busy():
            vol_tmp = float(value) / 100
        pygame.mixer.music.set_volume(float(value)/100)
        vol_tmp = float(value)/100

    else:
        vol_tmp = float(value)/100


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
