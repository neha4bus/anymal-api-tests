#!/opt/ros/noetic/share/anymal_liveview_python_env/venv/bin/python

# This script can be executed by using the venv from anymal_liveview_python_env package

import os
import asyncio
import logging
import pkg_resources
from signal import SIGINT, SIGTERM
import livekit
from livekit import rtc
from aioconsole import ainput
import cv2
import numpy as np
import requests
import json
import argparse

# `livekit/python-sdks` relies on `livekit/rust-sdks` (i.e. in particular
# [`livekit/rust-sdks/livekit-ffi`](https://github.com/livekit/rust-sdks/tree/main/livekit-ffi)).
# Again, the ffi falls back on
# [`env_logger`](https://docs.rs/env_logger/latest/env_logger/) which allows to
# be configured by means of the `RUST_LOG` env variable. Note that we're relying
# on internal implementation details, here.
os.environ["RUST_LOG"] = "libwebrtc=off,livekit::rtc_engine::rtc_events=off,livekit::room=error"
HEARTBEAT_NAME = "heartbeat"
BASE_URL = None
LV_TOKEN_ENDPOINT = "/anymal-api/liveview/token"
LV_SOURCES_ENDPOINT = "/anymal-api/liveview/sources"
LV_ENABLE_TRACKS_ENDPOINT = "/anymal-api/liveview/tracks"
SERVER_TOKEN_HEADER = None
VERIFY_SSL_CERTS = True

def get_server_token():
    url = f"{BASE_URL}/authentication-service/auth/login"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "email": args.email,
        "password": args.password
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, verify=VERIFY_SSL_CERTS)
        logging.debug(f"Status: {response.status_code}")
        try:
            data = response.json()
            logging.debug("Response:")
            logging.debug(json.dumps(data, indent=2))
            if "accessToken" not in data:
                print("No access token found in response.")
                return None
            return data["accessToken"]
        except ValueError:
            logging.debug(f"Json error. Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print("Request Error:", e)
        return None

def get_liveview_room_info():
    url = f"{BASE_URL}{LV_TOKEN_ENDPOINT}"
    params = {"participant": "liveview_example"}
    
    try:
        response = requests.get(url, params=params, headers=SERVER_TOKEN_HEADER, verify=VERIFY_SSL_CERTS)
        logging.debug(f"Status: {response.status_code}")
        try:
            data = response.json()
            logging.debug("Response:")
            logging.debug(json.dumps(data, indent=2))
            if "token" not in data:
                print("No token found in response.")
                return None
            if not isinstance(data["token"], dict):
                print("Expected 'token' to be a dict, but got:", type(data["token"]))
                return None
            return data["token"]
        except ValueError:
            logging.debug(f"Json error. Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print("Request Error:", e)
        return None

def get_liveview_sources(anymal_name: str):
    url = f"{BASE_URL}{LV_SOURCES_ENDPOINT}"
    params = {"anymal": anymal_name}
    try:
        response = requests.get(url, params=params, headers=SERVER_TOKEN_HEADER, verify=VERIFY_SSL_CERTS)
        logging.debug(f"Status: {response.status_code}")
        try:
            data = response.json()
            logging.debug("Response:")
            logging.debug(json.dumps(data, indent=2))
            if "sources" not in data or not data["sources"]:
                print("No sources found in response.")
                return None
            if not isinstance(data["sources"], list):
                print("Expected 'sources' to be a list, but got:", type(data["sources"]))
                return None
            return data["sources"]
        except ValueError:
            logging.debug(f"Json error. Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print("Request Error:", e)
        return None


def set_liveview_tracks(anymal_name: str, tracks):
    url = f"{BASE_URL}{LV_ENABLE_TRACKS_ENDPOINT}"
    params = {"anymal": anymal_name}

    # Renew the token periodically to ensure it is valid
    global SERVER_TOKEN_HEADER
    SERVER_TOKEN_HEADER = {"Authorization": f"Bearer {get_server_token()}"}
    
    payload_tracks_list = []
    for track in tracks:
        payload_tracks_list.append({"frameId": track})
    payload = {
        "tracks": payload_tracks_list
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        **SERVER_TOKEN_HEADER
    }
    try:
        response = requests.post(url, params=params, headers=headers, data=json.dumps(payload))
        logging.debug(f"Status: {response.status_code}")
        try:
            data = response.json()
            logging.debug("Response:")
            logging.debug(json.dumps(data, indent=2))
        except ValueError:
            logging.debug(f"Json error. Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print("Request Error:", e)
        
def setup_room(loop: asyncio.AbstractEventLoop, tasks: dict, anymal_name: str) -> livekit.rtc.Room:
    room = livekit.rtc.Room(loop=loop)

    @room.on("track_subscribed")
    def on_track_subscribed(
        track: livekit.rtc.Track,
        publication: livekit.rtc.RemoteTrackPublication,
        participant: livekit.rtc.RemoteParticipant,
    ):
        # Since we are using auto-subscribe, we will receive all the tracks from all the connected robots.
        # Filter only for the desired robot here.
        nonlocal anymal_name
        if anymal_name not in participant.identity:
            logging.info(f"Track from participant {participant.identity} is not from {anymal_name}. Ignoring.")
            return
        
        logging.info(f"Track subscribed: {track.name} from participant: {participant.identity}")
        if track.kind == livekit.rtc.TrackKind.KIND_VIDEO:
            nonlocal tasks
            noimg_task = tasks.get(f"noimage-{track.name}", None)
            if noimg_task:
                noimg_task.cancel()
            task = asyncio.create_task(receive_frames(track))
            tasks[track.name] = task
            task.add_done_callback(lambda _: receive_frames_cleanup(tasks, track.name))

    @room.on("track_unpublished")
    def on_track_unpublished(publication: livekit.rtc.RemoteTrackPublication, participant: livekit.rtc.RemoteParticipant):
        logging.info(f"Track unpublished: {publication.name} from participant: {participant.identity}")
        nonlocal tasks
        task = tasks.get(publication.name, None)
        if task is not None:
            try:
                task.cancel()
            except:
                pass

    @room.on("track_published")
    def on_track_published(publication: livekit.rtc.RemoteTrackPublication, participant: livekit.rtc.RemoteParticipant):
        logging.info(f"Track published: {publication.name} from participant: {participant.identity}")

    return room

def receive_frames_cleanup(tasks, name):
    del tasks[name]
    try:
        # Check if the window exists before destroying it
        if cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE) >= 0:
            cv2.destroyWindow(name)
    except cv2.error as e:
        print(f"Error destroying window '{name}': {e}")

async def receive_frames(track: livekit.rtc.Track) -> None:
    if not track.name:
        # All tracks that are sent from the ANYmal have names.
        return
    video_stream = livekit.rtc.VideoStream(track)
    cv2.namedWindow(track.name, cv2.WINDOW_NORMAL)
    cv2.startWindowThread()

    async for frameEvent in video_stream:
        frame = frameEvent.frame

        frame = frame.convert(livekit.rtc.VideoBufferType.BGRA)
        arr = np.frombuffer(frame.data, dtype=np.uint8)

        # Reshape the array to match the frame's dimensions (height, width, channels)
        arr = arr.reshape((frame.height, frame.width, 4))

        # Directly display the BGR frame
        cv2.imshow(track.name, arr)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

async def show_noimage(track: str) -> None:
    # Using a Creative Commons image, with transparent background removed (and set to white)
    # License:
    # https://commons.wikimedia.org/wiki/File:No_photo_%282067963%29_-_The_Noun_Project.svg#filelinks
    noimage = cv2.imread(pkg_resources.resource_filename('anymal_sdk_example',
                                                         'resources/no-image.png'))
    
    # uncomment the following line to test locally without installing the package. Comment the above line.
    # noimage = cv2.imread('/home/ggiannakaras/workspace/source/anybotics/anymal/anymal_api/anymal_sdk_python_example/src/anymal_sdk_example/resources/no-image.png')

    while True:
        cv2.imshow(track, noimage)
        cv2.waitKey(1)
        await asyncio.sleep(0.5)

def stop_heartbeat(tasks):
    # Cancel existing heartbeat task if it exists and is running
    if HEARTBEAT_NAME in tasks and tasks[HEARTBEAT_NAME] and not tasks[HEARTBEAT_NAME].done():
        tasks[HEARTBEAT_NAME].cancel()
        del tasks[HEARTBEAT_NAME]

async def user_input(anymal_name: str, sources: set, tasks: dict):
    tracks = set()
    once = True
    while True:
        if sources:
            if once:
                once = False
                print("You can now input tracks you want to watch.")
                print("* Prefix with '+' to add to list")
                print("* Prefix with '-' to remove from list")
                print("* Other valid input replaces the current set.")

            frame_ids = set()
            for source in sources:
                if isinstance(source, dict) and "frameId" in source:
                    frame_ids.add(source["frameId"])
                    
            print(f"Available Sources: {', '.join(frame_ids)}")
            print("To exit, type 'exit'.")
            
            track_name = await ainput("Name of the track you would like to consume: ")
            if track_name == "exit":
                print("Exiting.")
                for task in tasks.values():
                    if not task.done():
                        task.cancel()
                return
            if not track_name:
                tracks.clear()
            elif track_name[0] == "+":
                tracks.add(track_name[1:])
            elif track_name[0] == "-":
                tracks.discard(track_name[1:])
            else:
                tracks = {track_name}
            invalid = tracks - frame_ids
            if invalid:
                tracks -= invalid
                print(
                    "The following track names are not currently available and will be ignored:"
                )
                for track in invalid:
                    print(f"- '{track}'")
            print(f"Sending the following list of tracks: {', '.join(tracks)}")
            for track in tracks:
                window_exists = False
                try:
                    window_exists = (cv2.getWindowProperty(track, cv2.WND_PROP_VISIBLE) >= 0)
                except cv2.error:
                    pass
                if not window_exists:
                    task = asyncio.create_task(show_noimage(track))
                    tasks[f"noimage-{track}"] = task
            stop_heartbeat(tasks)
            # As a heartbeat we set the liveview tracks. Otherwise the liveview streams will stop
            tasks[HEARTBEAT_NAME] = asyncio.create_task(heartbeat(anymal_name, tracks))
        else:
            await asyncio.sleep(1)
            
async def heartbeat(anymal_name, tracks):
    while True:
        set_liveview_tracks(anymal_name, tracks)
        await asyncio.sleep(3)
    

async def main(loop: asyncio.AbstractEventLoop, args) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    
    server_token = get_server_token()
    if server_token is None:
        print("Failed to retrieve server token.")
        if loop.is_running():
            loop.stop()
        return
    global SERVER_TOKEN_HEADER
    SERVER_TOKEN_HEADER = {"Authorization": f"Bearer {server_token}"}

    # We'll operate on the following sets
    tasks = dict()
    
    anymal_name = input("Name of your ANYmal: ")
    room = setup_room(loop, tasks, anymal_name)
    
    sources = get_liveview_sources(anymal_name)
    if sources is None:
        print("Failed to retrieve liveview sources.")
        if loop.is_running():
            loop.stop()
        return
    
    async def cleanup():
        print("Exit by typing 'exit' and pressing enter.")

    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, lambda: asyncio.ensure_future(cleanup()))
        
    roomInfo = get_liveview_room_info()
    if roomInfo is None:
        print("Failed to retrieve liveview room info.")
        if loop.is_running():
            loop.stop()
        return
    
    print(f"LiveView Token:\n  url: {roomInfo['url']}\n  token: {roomInfo['token']}")

    # "conneceted" callback doesn't work, so block here and check the result
    # For now we use auto-subscribe to keep things simple. This means we will receive all the available streams in the room.
    # If we need to refine this we can set options parameter to options = {"auto_subscribe": False}
    await room.connect(roomInfo['url'], roomInfo['token'])
    if not room.isconnected():
        print("Failed to connect to the room.")
        if loop.is_running():
            loop.stop()
        return
    print(f"Connected to room {room.name}.")

    tasks["user_input"] = asyncio.create_task(user_input(anymal_name, sources, tasks))
    await asyncio.gather(*tasks.values(), return_exceptions=True)

    # Shutdown
    print("Shut down livekit connection")
    await room.disconnect()

    print("Session closed.")
    loop.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Liveview Example")
    parser.add_argument("--server", required=True, type=str, help="The server URL to connect to (mandatory)")
    parser.add_argument("--email", required=True, type=str, help="The email used for authentication (mandatory)")
    parser.add_argument("--password", required=True, type=str, help="The password used for authentication (mandatory)")
    parser.add_argument("--no-verify", required=False, action='store_true', help="Do not verify SSL certificates (default: False)")
    args = parser.parse_args()
    print("Starting liveview example.")

    BASE_URL = "https://" + args.server.strip("api-")
    VERIFY_SSL_CERTS = not args.no_verify
    print(f"Using server URL: {BASE_URL}")

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main(loop, args))

    try:
        loop.run_forever()
    finally:
        print("Closing loop.")
        loop.close()
