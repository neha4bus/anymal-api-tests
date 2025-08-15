import logging
import requests
from pathlib import Path
from PIL import Image
from argparse import Namespace
from typing import Tuple, Callable
import anymal_api_proto as api

from anymal_sdk import (
    Client,
    ISession,
    CommunicationInterface,
    LiveViewInterface,
    MissionInterface,
    MissionPlan,
)

from .example_helpers import (
    anymal_state_callback,
    anymal_physical_condition_callback,
    control_status_callback,
    eval_mission_response,
    eval_mission_response_old,
    eval_result,
    eval_result_anymal,
    inspection_callback,
    mission_callback,
)

from .spatial_helpers import deg_to_rad

from .config import (
    INSPECTIONS_PATH,
    REQUESTS_PATH
)

class ANYmalExampleHandler:
    """All logic used in the Python SDK examples."""

    def __init__(self, client_name: str, anymal_name: str, args: Namespace) -> None:
        logging.basicConfig(level=logging.INFO)
        self.client: Client = None
        self.session: ISession = None
        self.server_url: str = args.server.strip("api-")
        self.user_email: str = args.email
        self.user_password: str = args.password
        self.anymal_name: str = anymal_name
        self.client_name: str = client_name
        self.communication_interface: CommunicationInterface = None
        self.liveview_interface: LiveViewInterface = None
        self.liveview_running: bool = False
        self.mission_interface: MissionInterface = None
        self.initialize_session(client_name, args)

        # helper member to check if the callbacks were executed
        self.last_connection_event: api.ConnectionEvent = None
        self.last_mission_event: api.MissionEvent = None
        self.last_anymal_state_event: api.AnymalStateEvent = None
        self.last_anymal_physical_condition_event: api.AnymalPhysicalConditionEvent = None
        self.last_control_status_event: api.ControlStatus = None

        self.control_authority_status: Tuple[str, str] = ("", "")

        # Create directories for inspection requests and inspections if they do not exist.
        request_directory = Path(REQUESTS_PATH)
        request_directory.mkdir(parents=True, exist_ok=True)

    def get_current_control_authority_status(self) -> Tuple[str, str]:
        return self.control_authority_status

    def is_pstop_engaged(self) -> bool:
        if self.last_control_status_event is None:
            return False
        return self.last_control_status_event.protective_stop.is_engaged

    def is_pstop_disengaged(self) -> bool:
        if self.last_control_status_event is None:
            return False
        return not self.last_control_status_event.protective_stop.is_engaged

    def in_control(self) -> bool:
        return self.lease_id is not None

    def initialize_session(self, client_name: str, args: Namespace) -> None:
        """
        Initialize the client with an id that uniquely identifies it. Open a new session with given arguments.
        :param client name
        :param args: arguments for the session
        """
        self.client = Client(client_name)
        if args.preauth:
            self.client.preauthenticate(*args.preauth.split(":"))
        self.session = self.client.openSession(
            args.server,
            args.keepalive_period,
            args.root_certificate,
            args.client_certificate,
            args.token,
        )

    def create_communication_interface(self) -> None:
        """Initialize communicatopm interface based on the existing session."""
        self.communication_interface = CommunicationInterface(self.session)

    def create_liveview_interface(self) -> None:
        """Initialize liveview interface based on the existing session."""
        self.liveview_interface = LiveViewInterface(self.session, self.anymal_name)

    # Maintain while we finish mission API 1.0 work
    def create_mission_interface(self) -> None:
        """Initialize mission interface based on the existing session."""
        self.mission_interface = MissionInterface(self.session)

    def register_connection_callbacks(self) -> bool:
        """Register callbacks on connection events."""
        if not self.communication_interface:
            return False

        def event_callback(event: api.ConnectionEvent):
            logging.info(f"ANYmal {event.anymal_name} has status {api.ConnectionStatus.Name(event.connected)}.")
            self.last_connection_event = event

        def completion_callback(ec):
            logging.info(f"ANYmal connection completed with error code {ec.message()}.")

        request = api.SubscribeConnectionRequest()
        request.anymal_name = self.anymal_name
        logging.info("Registering callback on connection events.")
        self.communication_interface.subscribeToEvents(request, event_callback, completion_callback)
        logging.info("Waiting for the events...")
        return True

    def register_inspection_callbacks(self) -> bool:
        """Register callbacks on inspection events."""
        if not self.communication_interface:
            return False

        def completion_callback(ec):
            logging.info(f"ANYmal inspection completed with error code {ec.message()}.")

        request = api.SubscribeInspectionRequest()
        request.anymal_name = self.anymal_name
        logging.info("Registering callback on inspection events.")
        self.communication_interface.subscribeToEvents(request, inspection_callback, completion_callback)
        logging.info("Waiting for the events...")
        return True

    def register_mission_callbacks(self) -> bool:
        """Register callbacks on mission events."""
        if not self.communication_interface:
            return False

        def event_callback(event: api.MissionEvent):
            self.last_mission_event = mission_callback(event)

        def completion_callback(ec):
            logging.info(f"ANYmal mission completed with error code {ec.message()}.")

        request = api.SubscribeMissionRequest()
        request.anymal_name = self.anymal_name
        logging.info("Registering callback on mission events.")
        self.communication_interface.subscribeToEvents(request, event_callback, completion_callback)
        logging.info("Waiting for the events...")
        return True

    def register_anymal_state_callbacks(self) -> bool:
        """Register callbacks on ANYmal state events."""
        if not self.communication_interface:
            return False

        def event_callback(event: api.AnymalStateEvent):
            self.last_anymal_state_event = anymal_state_callback(event)

        def completion_callback(ec):
            logging.info(f"ANYmal state update completed with error code {ec.message()}.")

        request = api.SubscribeAnymalStateRequest()
        request.anymal_name = self.anymal_name
        logging.info("Registering callback on ANYmal state events.")
        self.communication_interface.subscribeToEvents(request, event_callback, completion_callback)
        logging.info("Waiting for the events...")
        return True

    def register_anymal_physical_condition_callbacks(self) -> bool:
        """Register callbacks on ANYmal physical condition events."""
        if not self.communication_interface:
            return False

        def event_callback(event: api.AnymalPhysicalConditionEvent):
            self.last_anymal_physical_condition_event = anymal_physical_condition_callback(event)

        def completion_callback(ec):
            logging.info(f"ANYmal physical condition update completed with error code {ec.message()}.")

        request = api.SubscribeAnymalPhysicalConditionRequest()
        request.anymal_name = self.anymal_name
        logging.info("Registering callback on ANYmal physical condition events.")
        self.communication_interface.subscribeToEvents(request, event_callback, completion_callback)
        logging.info("Waiting for the events...")
        return True

    def register_control_status_callbacks(self) -> bool:
        """Register callbacks on control status events."""
        if not self.communication_interface:
            return False

        def event_callback(event: api.ControlStatus):
            self.last_control_status_event = control_status_callback(event)

        def completion_callback(ec):
            logging.info(f"ANYmal control status update completed with error code {ec.message()}.")

        request = api.SubscribeControlStatusRequest()
        request.anymal_name = self.anymal_name
        logging.info("Registering callback on control status events.")
        self.communication_interface.subscribeToEvents(request, event_callback, completion_callback)
        logging.info("Waiting for the events...")
        return True

    def register_liveview_callbacks(self, event_callback: Callable) -> bool:
        """Register callbacks on liveview events."""
        if not self.liveview_interface:
            return False
        self.liveview_running = True

        def disconnect_callback(ec):
            logging.info(f"Liveview disconnected with code {ec.message()}.")
            self.liveview_running = False

        logging.info("Registering callback on liveview events.")
        self.liveview_interface.subscribeToEvents(event_callback, disconnect_callback)
        logging.info("Waiting for the events...")
        return True

    def take_control(self) -> bool:
        """Attempt to take control of the given ANYmal."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't take control.")
            return False

        def control_error_callback(event: api.ControlAuthorityServerMsg):
            if event.status != api.ServiceCallStatus.SCS_OK:
                logging.error(f"Control Error: {event.message}")
                self.lease_id = None

        logging.info("Leasing control...")
        request = api.TakeControlRequestSdk()
        request.anymal_name = self.anymal_name
        request.client_type = api.ControlAuthorityClientType.CLCT_AUTOMATED
        response = self.communication_interface.takeControl(request, control_error_callback)
        if not response:
            logging.error("Could not take control. Unknown error.")
            return False
        if response.status == api.ServiceCallStatus.SCS_ERROR_UNKNOWN:
            logging.error(f"Could not take control. {response.message}")
            return False
        self.lease_id = response.lease_id
        logging.info(f"Successfully taken control. lease_id: {self.lease_id}")
        return True

    def release_control(self) -> bool:
        """Attempt to release control of the given ANYmal."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't release control.")
            return False

        logging.info("Releasing control...")
        request = api.ReleaseControlRequestSdk()
        request.anymal_name = self.anymal_name
        response = self.communication_interface.releaseControl(request)
        if not response:
            logging.error("Could not release control. Unknown error.")
            return False
        if response.status == api.ServiceCallStatus.SCS_ERROR_UNKNOWN:
            logging.error(f"Could not release control. {response.message}")
            return False
        logging.info(f"Release control successful. {response.message}")
        self.lease_id = None
        return True

    def engage_protective_stop(self) -> bool:
        """Engage protective stop."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't engage protective stop.")
            return False
        request = api.ProtectiveStopRequest()
        request.anymal_name = self.anymal_name
        request.command = api.SafetyCommand.SCMD_ENGAGE

        response = self.communication_interface.sendRequest(request)
        return eval_result(response, self.anymal_name, "Engage P-Stop")

    def disengage_protective_stop(
        self,
    ) -> bool:
        """Take control, disengage protective stop, release control."""
        if not self.take_control():
            return False

        request = api.ProtectiveStopRequest()
        request.anymal_name = self.anymal_name
        request.command = api.SafetyCommand.SCMD_DISENGAGE

        result = eval_result(
            self.communication_interface.sendRequest(request),
            self.anymal_name,
            "Disengage P-Stop",
        )
        result &= self.release_control()
        return result

    def engage_power_cut(
        self,
    ) -> bool:
        """Engage power cut."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't engage power cut.")
            return False

        request = api.PowerCutRequest()
        request.anymal_name = self.anymal_name
        request.command = api.SafetyCommand.SCMD_ENGAGE

        response = self.communication_interface.sendRequest(request)
        return eval_result(response, self.anymal_name, "Engage power cut")

    def disengage_power_cut(
        self,
    ) -> bool:
        """Take control, disengage power cut, release control."""
        if not self.take_control():
            return False

        request = api.PowerCutRequest()
        request.anymal_name = self.anymal_name
        request.command = api.SafetyCommand.SCMD_DISENGAGE

        result = eval_result(
            self.communication_interface.sendRequest(request),
            self.anymal_name,
            "Disengage power cut",
        )
        result &= self.release_control()
        return result

    def get_control_authority_status(self) -> None:
        """Get control authority status on robot 'anymal_name'."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't get authority status.")
            return
        request = api.GetControlAuthorityStatusRequest()
        request.anymal_name = self.anymal_name

        response = self.communication_interface.sendRequest(request)
        if not response:
            logging.error(
                f"Get control authority owner service on ANYmal {self.anymal_name} could not be called successfully."
            )
        elif response.status != api.ServiceCallStatus.SCS_OK:
            logging.error(f"Get control authority owner service call failed.")
        else:
            control_authority_status = response.control_authority_status
            if control_authority_status:
                lease_id = control_authority_status.lease_id
                client_name = control_authority_status.client_name
                self.control_authority_status = (lease_id, client_name)
                logging.info(
                    f"Current control authority owner of ANYmal {self.anymal_name}:\n"
                    f"  Client name: {client_name}\n"
                    f"  Lease id: {lease_id}\n"
                )
            else:
                logging.info(f"Control authority of ANYmal {self.anymal_name} is free.")

    def get_user_interaction_mode(self) -> api.UserInteractionMode:
        """Get user interaction mode on robot 'anymal_name'."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't get user interaction mode.")
            return api.UserInteractionMode.UIM_UNDEFINED
        request = api.GetUserInteractionModeRequest()
        request.anymal_name = self.anymal_name

        response = self.communication_interface.sendRequest(request)
        if not response:
            logging.error(
                f"Get user interaction mode service on ANYmal {self.anymal_name} could not be called successfully."
            )
        elif response.header.service_call_status != api.AnymalServiceCallStatus.ASCS_OK:
            logging.error(f"Get user interaction mode service call failed. {response.message}")
        else:
            user_interaction_mode = response.user_interaction_mode
            logging.info(f"User interaction mode of ANYmal {self.anymal_name}:\n" f"  {user_interaction_mode}")
            return user_interaction_mode
        return api.UserInteractionMode.UIM_UNDEFINED

    def set_user_interaction_mode(self, user_interaction_mode: api.UserInteractionMode) -> bool:
        """Set user interaction mode on robot 'anymal_name'. Requires control authority. Return True if success."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't set user interaction mode.")
            return False
        request = api.SetUserInteractionModeRequest()
        request.anymal_name = self.anymal_name
        request.user_interaction_mode = user_interaction_mode

        response = self.communication_interface.sendRequest(request)
        return eval_result_anymal(response, self.anymal_name, "Set user interaction mode")

    def get_predefined_missions(self) -> None:
        """Get available predefined missions on robot 'anymal_name'."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't get predefined missions.")
            return False
        request = api.GetPredefinedMissionsRequest()
        request.anymal_name = self.anymal_name

        response = self.communication_interface.sendRequest(request)
        if not response:
            logging.error(
                f"Get predefined missions service on ANYmal {self.anymal_name} could not be called successfully."
            )
            return False
        elif response.header.service_call_status != api.AnymalServiceCallStatus.ASCS_OK:
            logging.error(f"Get predefined missions service call failed. {response.header.message}")
            return False
        else:
            logging.info(f"Predefined missions on ANYmal {self.anymal_name}:\n" f"  {response.missions_metadata}")
            return True

    def start_mission_description(self, mission_description: api.AnyMissionDescription) -> str:
        """Start mission from a given mission description. Return mission run ID"""
        uim = self.get_user_interaction_mode()
        if uim != api.UserInteractionMode.UIM_AUTONOMOUS:
            if not self.set_user_interaction_mode(api.UserInteractionMode.UIM_AUTONOMOUS):
                raise RuntimeError(f"Failed to set user interaction mode to UIM_AUTONOMOUS")

        request = api.ControlMissionRequest()
        request.anymal_name = self.anymal_name
        request.start.mission_description.CopyFrom(mission_description)
        response = self.communication_interface.sendRequest(request)
        if not response or not eval_mission_response(response, "start"):
            raise RuntimeError(f"Mission on ANYmal '{self.anymal_name}' could not be started. {response.message}")
        logging.info(f"Mission {response.run_uid} started successfully.")
        return str(response.run_uid)

    def start_mission(
        self,
        anymal_name: str,
        mission_id: str,
        initial_task: str,
        mission_plan: MissionPlan = None,
    ) -> str:
        """Start mission. If a mission_plan is provided, then an ad-hoc mission is started.
        Will raise a RunTime error in case of a failure to start. Return mission run ID
        """
        uim = self.get_user_interaction_mode()
        if uim != api.UserInteractionMode.UIM_AUTONOMOUS:
            if not self.set_user_interaction_mode(api.UserInteractionMode.UIM_AUTONOMOUS):
                raise RuntimeError(f"Failed to set user interaction mode to UIM_AUTONOMOUS")

        if mission_plan:
            logging.info(f"Starting ad-hoc mission '{mission_id}' on ANYmal '{anymal_name}'.")
            start_response = self.mission_interface.startMission(anymal_name, mission_id, mission_plan, initial_task)
        else:
            logging.info(f"Starting pre-defined mission '{mission_id}' on ANYmal '{anymal_name}'.")
            start_response = self.mission_interface.startMission(anymal_name, mission_id, initial_task)

        if not start_response or not eval_mission_response_old(start_response, "start"):
            raise RuntimeError(f"Mission '{mission_id}' on ANYmal '{anymal_name}' could not be started.")

        logging.info("Mission started successfully.")
        return start_response.getMissionRunId()

    def pause_mission(self, run_uid: str) -> bool:
        """Pause mission. Return True if success."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't resume mission.")
            return False
        request = api.ControlMissionRequest()
        request.anymal_name = self.anymal_name
        request.pause.run_uid = run_uid
        response = self.communication_interface.sendRequest(request)
        if not response or not eval_mission_response(response, "pause"):
            logging.error(
                f"Mission with run uid '{run_uid}' on ANYmal '{self.anymal_name}' could not be paused. {response.message}"
            )
            return False

        logging.info("Mission paused successfully.")
        return True

    def resume_mission(self, run_uid: str) -> bool:
        """Resume mission. Return True if success."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't resume mission.")
            return False
        request = api.ControlMissionRequest()
        request.anymal_name = self.anymal_name
        request.resume.run_uid = run_uid
        response = self.communication_interface.sendRequest(request)
        if not response or not eval_mission_response(response, "resume"):
            logging.error(f"Mission with run uid '{run_uid}' on ANYmal '{self.anymal_name}' could not be resumed.")
            return False

        logging.info("Mission resumed successfully.")
        return True

    def set_led_intensity(self, intensity: float) -> bool:
        """Set LED intensity."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't set LED intensity.")
            return False
        request = api.InspectionPayloadRequest()
        request.anymal_name = self.anymal_name
        request.led_intensity = intensity
        response = self.communication_interface.sendRequest(request)
        return eval_result(response, self.anymal_name, "Set LED intensity")

    def set_zoom_level(self, zoom_level: float) -> bool:
        """Set zoom level."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't set zoom level.")
            return False
        request = api.InspectionPayloadRequest()
        request.anymal_name = self.anymal_name
        request.zoom_level = zoom_level
        response = self.communication_interface.sendRequest(request)
        return eval_result(response, self.anymal_name, "Set zoom level")

    def set_pan_tilt_position(self, pan_deg: float, tilt_deg: float) -> bool:
        """Set pan/tilt position."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't set pan/tilt position.")
            return False
        request = api.InspectionPayloadRequest()
        request.anymal_name = self.anymal_name
        request.pan_tilt_position.pan = deg_to_rad(pan_deg)
        request.pan_tilt_position.tilt = deg_to_rad(tilt_deg)
        response = self.communication_interface.sendRequest(request)
        return eval_result(response, self.anymal_name, "Set pan/tilt position")

    def set_zoom_rectangle(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        image_width: int,
        image_height: int,
    ) -> bool:
        """Set zoom rectangle."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't set zoom rectangle.")
            return False
        request = api.InspectionPayloadRequest()
        request.anymal_name = self.anymal_name
        request.zoom_rectangle.rectangle.x = x
        request.zoom_rectangle.rectangle.y = y
        request.zoom_rectangle.rectangle.width = width
        request.zoom_rectangle.rectangle.height = height
        request.zoom_rectangle.image_size.width = image_width
        request.zoom_rectangle.image_size.height = image_height
        response = self.communication_interface.sendRequest(request)
        return eval_result(response, self.anymal_name, "Set zoom rectangle")

    def set_acoustic_imaging_stream_frequencies(self, min_frequency: int, max_frequency: int) -> bool:
        """Set acoustic imaging stream frequencies."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't set acoustic imaging stream frequencies.")
            return False
        request = api.InspectionPayloadRequest()
        request.anymal_name = self.anymal_name
        request.acoustic_imaging_stream_frequencies.min = min_frequency
        request.acoustic_imaging_stream_frequencies.max = max_frequency
        response = self.communication_interface.sendRequest(request)
        return eval_result(response, self.anymal_name, "Set acoustic imaging stream frequencies")
    def set_acoustic_imaging_stream_sensitivity(self, sensitivity_level: int) -> bool:
        """Set acoustic imaging stream sensitivity level."""
        if not self.communication_interface:
            logging.error("Communication interface is not initiated. Can't set acoustic imaging stream sensitivity level.")
            return False
        request = api.InspectionPayloadRequest()
        request.anymal_name = self.anymal_name
        if sensitivity_level==1:
            request.acoustic_imaging_stream_sensitivity = api.AcousticImagingSensitivityLevel.AISL_LOW
        elif sensitivity_level==2:
            request.acoustic_imaging_stream_sensitivity = api.AcousticImagingSensitivityLevel.AISL_MEDIUM
        elif sensitivity_level==3:
            request.acoustic_imaging_stream_sensitivity = api.AcousticImagingSensitivityLevel.AISL_HIGH
        elif sensitivity_level==4:
            request.acoustic_imaging_stream_sensitivity = api.AcousticImagingSensitivityLevel.AISL_UNSET
        else:
            logging.error("Invalid sensitivity level. Must be 1 (Low), 2 (Medium), 3 (HIGH) or 4 (UNSET).")
            return False
        response = self.communication_interface.sendRequest(request)
        return eval_result(response, self.anymal_name, "Set acoustic imaging sensitivity level")
    
    def close_communication_interface(self) -> None:
        """Close the communication interface."""
        if self.communication_interface:
            logging.info("Closing the communication interface.")
            self.communication_interface.shutdown()

    def close_liveview_interface(self) -> None:
        """Close the liveview interface."""
        if self.liveview_interface:
            self.liveview_running = False
            logging.info("Closing the liveview interface.")
            self.liveview_interface.shutdown()

    def close_mission_interface(self) -> None:
        """Close the mission interface."""
        if self.mission_interface:
            logging.info("Closing the mission interface.")
            self.mission_interface.shutdown()

    def close_session(self) -> None:
        """Close existing session."""
        self.client.closeSession(self.session)
        logging.info("Session closed.")

    def fetch_inspection_data(self) -> None:
        """Fetching inspection data from data navigator."""
        token = self.get_token()
        header = {
            'Authorization': f'Bearer {token}'
        }

        request_directory = Path(REQUESTS_PATH)
        inspection_directory = Path(INSPECTIONS_PATH)

        for request_file in request_directory.iterdir():
            asset_id = request_file.name.split("__")[1]
            download_filename = request_file.name.split("__")[2]
            storage_filename = asset_id + "_" + download_filename
            filepath = inspection_directory / storage_filename
            data_nav_file_url = f"https://{self.server_url}/data-navigator-api/inspections/raw-data/{download_filename}"
            response = requests.get(data_nav_file_url, headers=header)
            if response.status_code == requests.codes.ok:
                self.save_inspection_data_and_delete_request(response, filepath, request_file)
                self.show_downloaded_image(filepath)
                logging.debug(f"Downloaded file {download_filename}.")
            elif response.status_code == requests.codes.not_found:
                logging.debug(f"File {download_filename} not uploaded yet.")
            else:
                logging.error(f"Request to data navigator failed with status code {response.status_code}.")
                logging.error(f"Data navigator file URL: {data_nav_file_url}")

    def get_token(self) -> str:
        login_payload = {
            "email": self.user_email,
            "password": self.user_password,
        }
        login_headers = {
            'Content-Type': 'application/json'
        }
        auth_url = f"https://{self.server_url}/authentication-service/auth/login"
        auth_response = requests.post(auth_url, headers=login_headers, json=login_payload)
        if auth_response.status_code is requests.codes.created:
            return auth_response.json()["accessToken"]
        else:
            raise Exception(auth_response.json())

    def save_inspection_data_and_delete_request(self, response, filepath, request_file) -> None:
        """Save inspection data and delete request file."""
        logging.info(f"Saving inspection data to {filepath}.")
        with open(filepath, "wb") as file:
            file.write(response.content)
        request_file.unlink()

    def show_downloaded_image(self, filepath) -> None:
        filetype = filepath.name.split(".")[1]
        if filetype == "jpg":
            image = Image.open(filepath)
            image.show()
