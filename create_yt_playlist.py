import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# API 정보
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
# 이 스코프는 재생목록을 만들고 수정할 수 있는 권한을 요청합니다.
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
CLIENT_SECRETS_FILE = "client_secret.json"

import google.auth.transport.requests
from google.oauth2.credentials import Credentials


# 기존 재생목록 ID를 하드코딩합니다.
EXISTING_PLAYLIST_ID = "PLUaAQuzI7YgGUaza7B8Ilf_-nm2k44GiE"

def get_playlist_id(youtube):
    """항상 기존 재생목록 ID를 반환합니다."""
    return EXISTING_PLAYLIST_ID

def get_existing_video_ids(youtube, playlist_id):
    """기존 재생목록에 이미 포함된 videoId 목록을 반환."""
    video_ids = set()
    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        for item in response.get("items", []):
            resource = item["snippet"]["resourceId"]
            if resource["kind"] == "youtube#video":
                video_ids.add(resource["videoId"])
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    return video_ids

def get_authenticated_service():
    """OAuth 2.0 흐름을 통해 인증하고 API 클라이언트를 반환합니다. (토큰 캐싱 적용)"""
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"오류: '{CLIENT_SECRETS_FILE}' 파일을 찾을 수 없습니다.")
        print("Google Cloud Console에서 다운로드하여 이 스크립트와 같은 디렉토리에 저장하세요.")
        return None

    creds = None
    token_path = "token.json"
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=creds)

def search_video(youtube, query):
    """주어진 쿼리로 YouTube를 검색하고 첫 번째 결과의 비디오 ID를 반환합니다."""
    try:
        search_response = youtube.search().list(
            q=query,
            part="snippet",
            maxResults=1,
            type="video"
        ).execute()

        if not search_response["items"]:
            print(f"  -> '{query}'에 대한 검색 결과 없음")
            return None

        video_id = search_response["items"][0]["id"]["videoId"]
        video_title = search_response["items"][0]["snippet"]["title"]
        print(f"  -> 찾은 영상: {video_title}")
        return video_id
    except googleapiclient.errors.HttpError as e:
        print(f"  -> 검색 중 오류 발생: {e}")
        return None


def create_playlist(youtube, title, description):
    """새로운 비공개 재생목록을 생성하고 ID를 반환합니다."""
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "defaultLanguage": "ko"
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )
    response = request.execute()
    print(f"재생목록 '{response['snippet']['title']}' 생성 완료 (ID: {response['id']})")
    return response["id"]

def add_video_to_playlist(youtube, playlist_id, video_id):
    """지정된 재생목록에 비디오를 추가합니다."""
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    try:
        response = request.execute()
        print(f"  -> 재생목록에 추가 완료: {response['snippet']['title']}")
    except googleapiclient.errors.HttpError as e:
        print(f"  -> 재생목록 추가 중 오류 발생: {e}")


def main():
    youtube = get_authenticated_service()
    if not youtube:
        return

    try:
        with open('playlist.txt', 'r', encoding='utf-8') as f:
            songs = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("오류: 'playlist.txt' 파일을 찾을 수 없습니다.")
        return

    playlist_id = get_playlist_id(youtube)
    if not playlist_id:
        return

    # 추가된 곡 기록 파일
    added_songs_file = "added_songs.txt"
    added_songs = set()
    if os.path.exists(added_songs_file):
        with open(added_songs_file, 'r', encoding='utf-8') as f:
            added_songs = set(line.strip() for line in f if line.strip())

    # 기존 재생목록에 이어서 추가하는 경우, 이미 추가된 영상은 건너뜀
    existing_video_ids = set()
    existing_video_ids = get_existing_video_ids(youtube, playlist_id)

    # 이미 추가된 곡(added_songs)에 없는 곡만 처리
    songs_to_add = [song for song in songs if song not in added_songs]

    for i, song in enumerate(songs_to_add):
        print(f"\n[{i+1}/{len(songs_to_add)}] '{song}' 처리 중...")
        video_id = search_video(youtube, song)
        if video_id:
            if video_id in existing_video_ids:
                print(f"  -> 이미 재생목록에 포함된 영상입니다. 건너뜁니다.")
                continue
            add_video_to_playlist(youtube, playlist_id, video_id)
            # 추가된 곡 기록
            with open(added_songs_file, 'a', encoding='utf-8') as f:
                f.write(song + '\n')

    print("\n모든 노래 처리가 완료되었습니다!")


if __name__ == "__main__":
    main()
