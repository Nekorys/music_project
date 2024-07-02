import io
import os.path
import shutil
from tkinter import END
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']
parent_folder = '18rEhC3BYiG1HiasOAZnzP0GaYN9-1cW3'
# parent_folder = '1hErDnVAjTTeyaheYksh8aEO5jAvy7nPw'


def get_google_drive_folders():
    list_of_folders_and_songs = []
    creds = None
    if os.path.exists('Additional/token.json'):
        creds = Credentials.from_authorized_user_file('Additional/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'Additional/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('Additional/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        results = service.files().list(
            q=f"'{parent_folder}' in parents",
            pageSize=100,  # Збільшити кількість файлів за запит
            fields="nextPageToken, files(id, name)"
        ).execute()

        items = results.get('files', [])
        nextPageToken = results.get('nextPageToken')

        while nextPageToken:
            results = service.files().list(
                q=f"'{parent_folder}' in parents",
                pageSize=100,
                fields="nextPageToken, files(id, name)",
                pageToken=nextPageToken
            ).execute()
            items.extend(results.get('files', []))
            nextPageToken = results.get('nextPageToken')

        if not items:
            print('No files found.')
            return [], service

        for item in items:
            song_list = []
            results = service.files().list(
                q=f"'{item['id']}' in parents",
                pageSize=100,  # Збільшити кількість файлів за запит
                fields="nextPageToken, files(id, name)"
            ).execute()

            song_items = results.get('files', [])
            nextPageToken = results.get('nextPageToken')

            while nextPageToken:
                results = service.files().list(
                    q=f"'{item['id']}' in parents",
                    pageSize=100,
                    fields="nextPageToken, files(id, name)",
                    pageToken=nextPageToken
                ).execute()
                song_items.extend(results.get('files', []))
                nextPageToken = results.get('nextPageToken')
            for si in song_items:
                song_list.append({
                    'name': si['name'],
                    'id': si['id']
                })

            list_of_folders_and_songs.append(
                {
                    'folder': item['name'],
                    'folder_id': item['id'],
                    'songs': song_list
                }
            )
        return list_of_folders_and_songs, service
    except HttpError as error:
        print(f'An error occurred: {error}')


def get_local_folders():
    list_of_folders_and_songs = []
    folders = os.listdir('Songs')
    for folder in folders:
        songs = os.listdir(f'Songs/{folder}')
        list_of_folders_and_songs.append(
            {
                'folder': folder,
                'songs': songs
            }
        )
    return list_of_folders_and_songs


def download_files(service, folder_id, folder_name):
    results = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
    items = results.get('files', [])
    if items:
        for item in items:
            download_file(service, item['id'], item['name'], folder_name)
    else:
        print('Directory on drive is empty...')


def download_file(service, file_id, file_name, folder_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(f'Songs/{folder_name}/{file_name}', 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()


def download_list(wind, delete_flag, folder_list, songs_list, log_field):
    remote_list, service = get_google_drive_folders()
    local_list = get_local_folders()
    folders_to_remove = [a['folder'] for a in local_list]
    songs_to_remove = []
    for r_list in remote_list:
        try:
            folders_to_remove.remove(r_list['folder'])
        except:
            pass

        if r_list['folder'] in [a['folder'] for a in local_list]:
            if r_list['songs']:
                songs_in_folder = next((item['songs'] for item in local_list if item['folder'] == r_list['folder']), None)
                songs_to_remove_tmp = {
                    r_list['folder']: songs_in_folder.copy()
                }
                song_list = [a['name'] for a in r_list['songs']]
                for song in song_list:
                    if song not in songs_in_folder:
                        download_file(service, next((item['id'] for item in r_list['songs'] if item['name'] == song), None), song, r_list['folder'])
                    try:
                        songs_to_remove_tmp[r_list['folder']].remove(song)
                    except:
                        pass
                songs_to_remove.append(songs_to_remove_tmp)
        else:
            if not os.path.exists(f'Songs/{r_list['folder']}'):
                os.makedirs(f'Songs/{r_list['folder']}')
            download_files(service, r_list['folder_id'], r_list['folder'])

    log_field.insert('end', f'Download from drive has been completed\n\n', 'green_text')
    log_field.see(END)
    if delete_flag:
        for folder_to_remove in folders_to_remove:
            shutil.rmtree(f'Songs/{folder_to_remove}')
        for song_to_remove in [d for d in songs_to_remove if d[list(d.keys())[0]]]:
            for s_to_remove in song_to_remove[list(song_to_remove)[0]]:
                os.remove(f'Songs/{list(song_to_remove)[0]}/{s_to_remove}')
        log_field.insert('end', f'Not matched files have been deleted\n\n', 'green_text')
        log_field.see(END)
    wind.destroy()
    folder_list.delete(0, 'end')
    songs_list.delete(0, 'end')
    for folder in os.listdir('Songs'):
        folder_list.insert('end', folder)


def upload_list(wind, delete_flag, folder_list, songs_list, log_field):
    remote_list, service = get_google_drive_folders()
    local_list = get_local_folders()
    folders_to_remove = [a['folder'] for a in remote_list]
    songs_to_remove = []
    list_for_upload_dirs = []
    list_for_upload_songs = []
    for l_list in local_list:
        try:
            folders_to_remove.remove(l_list['folder'])
        except:
            pass

        if l_list['folder'] in [a['folder'] for a in remote_list]:
            if l_list['songs']:
                songs_in_folder = next((item['songs'] for item in remote_list if item['folder'] == l_list['folder']), None)
                songs_to_remove_tmp = songs_in_folder.copy()
                for song in l_list['songs']:
                    songs_to_remove_tmp = [song_l for song_l in songs_to_remove_tmp if song_l['name'] != song]
                    if song not in [a['name'] for a in songs_in_folder]:
                        upload_file(service, f'Songs/{l_list['folder']}/{song}', folder_id=next((item['folder_id'] for item in remote_list if item['folder'] == l_list['folder']), None))
                        list_for_upload_songs.append({
                            'name': song,
                            'folder': l_list['folder']
                        })
                songs_to_remove.extend(songs_to_remove_tmp)
        else:
            new_folder_id = create_folder(service, f'{l_list['folder']}')
            if l_list['songs']:
                for song in l_list['songs']:
                    upload_file(service, f'Songs/{l_list['folder']}/{song}', folder_id=new_folder_id)
            list_for_upload_dirs.append(l_list['folder'])
    log_field.insert('end', f'Upload to drive has been completed\n\n', 'green_text')
    log_field.see(END)
    if delete_flag:
        for file_to_delete in [a['folder_id'] for a in remote_list if a['folder'] in folders_to_remove]:
            delete_from_drive(service, file_to_delete)
        for file_to_delete in songs_to_remove:
            delete_from_drive(service, file_to_delete['id'])
        log_field.insert('end', f'Not matched files have been deleted\n\n', 'green_text')
        log_field.see(END)
    wind.destroy()
    folder_list.delete(0, 'end')
    songs_list.delete(0, 'end')
    for folder in os.listdir('Songs'):
        folder_list.insert('end', folder)


def upload_file(service, file_path, folder_id=parent_folder):
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()


def create_folder(service, folder_name, parent_id=parent_folder):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]

    try:
        file = service.files().create(body=file_metadata, fields='id').execute()
        return file.get("id")
    except Exception as e:
        print(f'An error occurred: {e}')


def delete_from_drive(service, file_id):
    try:
        service.files().delete(fileId=file_id).execute()
    except HttpError as error:
        print(f"An error occurred: {error}")


