import math
import logging
from pathlib import Path

import anymal_api_proto as api

from anymal_sdk import (
    convertInteractMissionStatusToString,
    convertServiceCallStatusToString,
    InteractMissionStatus,
    MissionPlan,
    MissionTask,
    MissionTaskInspection,
    MissionTaskOperationalMode,
    OperationalMode,
    ServiceCallStatus,
)

from .auditive_helpers import play_audio

from .config import (
    REQUESTS_PATH,
    AD_HOC_TASK_LIST_OPTIONS
)

from .spatial_helpers import (
    create_pose,
    quaternion_to_euler,
)


def eval_result(result, anymal_name, service_name) -> bool:
    """Evaluate the result of a service call."""
    if not result:
        logging.error(f"{service_name} service on ANYmal {anymal_name} could not be called successfully.")
        return False
    elif result.status != api.ServiceCallStatus.SCS_OK:
        logging.error(f"{service_name} service call failed. Error: {result.message}")
        return False
    else:
        logging.info(f"{service_name} service successful.")
        return True


def eval_result_anymal(result, anymal_name, service_name) -> bool:
    """Evaluate the result of a service call."""
    if not result:
        logging.error(f"{service_name} service on ANYmal {anymal_name} could not be called successfully.")
        return False
    elif result.header.service_call_status != api.AnymalServiceCallStatus.ASCS_OK:
        logging.error(f"{service_name} service call failed. Error: {result.header.message}")
        return False
    else:
        logging.info(f"{service_name} service successful.")
        return True


def eval_mission_response(response, action: str):
    header = response.header
    if header.service_call_status != api.AnymalServiceCallStatus.ASCS_OK:
        logging.error(
            f"Could not {action} mission. Connection status is '{api.AnymalServiceCallStatus.Name(header.service_call_status)}' and message '{header.message}'."
            f"This might be caused by an unestablished server connection."
        )
        return False
    mission_status = response.control_mission_status
    if mission_status != api.ControlMissionStatus.CMS_OK:
        logging.error(
            f"Could not {action} mission.\n"
            f"mission status is '{api.ControlMissionStatus.Name(mission_status)}' and message '{response.message}'."
        )
        return False
    return True


def eval_mission_response_old(response, action: str):
    start_status = response.getStatus()
    mission_start_status = response.getInteractMissionStatus()
    if start_status != ServiceCallStatus.SCS_OK or mission_start_status != InteractMissionStatus.OK:
        mission_start_status_string = convertInteractMissionStatusToString(mission_start_status)
        start_status_string = convertServiceCallStatusToString(start_status)
        logging.error(
            f"Could not {action} mission. Connection status is '{start_status_string}' and "
            f"mission status is '{mission_start_status_string}' and message '{response.getMessage()}'."
            f"This might be caused by an unestablished server connection."
        )
        return False
    return True


def anymal_state_callback(
    event: api.AnymalStateEvent,
) -> api.AnymalStateEvent:
    """Callback to be executed on ANYmal State Event. Returns current pose (x, y, z) of the ANYmal."""
    # Extract the pose from the event.
    robot_pose = event.pose.pose.value
    # Extract the relevant timestamp for the event.
    timestamp = event.timestamp
    # The timestamp value is given in nanoseconds since Unix epoch.
    # We can convert it into seconds for user-friendliness.
    timestamp_secs = timestamp.value / 1e9
    # Extract the x,y,z components of the robot position.
    pose_x = robot_pose.position.x
    pose_y = robot_pose.position.y
    pose_z = robot_pose.position.z
    # Extract the robot orientation (as a quaternion).
    rot_qx = robot_pose.orientation.qx
    rot_qy = robot_pose.orientation.qy
    rot_qz = robot_pose.orientation.qz
    rot_qw = robot_pose.orientation.qw
    # Convert the quaternion values into euler angles.
    _, _, yaw = quaternion_to_euler(rot_qx, rot_qy, rot_qz, rot_qw)
    # Convert the yaw value into degrees for user-friendliness.
    yaw_degrees = math.degrees(yaw)
    # Extract the pose frame.
    # frame_id = robot_pose.pose.frame_id
    # Extract the joint names and positions.
    joints = event.joints
    example_joint_name = joints[0].name
    example_joint_position = joints[0].position
    # Convert the joint position into degrees for user-friendliness.
    example_joint_position_degrees = math.degrees(example_joint_position)
    # Joints publish information at higher rates than the localization system, so they also carry their own timestamp.
    # example_joint_stamp = joints[0].timestamp
    # logging.info relevant information about the robot state.
    logging.info(
        f"Stamp: {timestamp_secs} - Robot {event.metadata.robot_name}. Position is X:{pose_x:.4f}, Y:{pose_y:.4f}, "
        f"Z:{pose_z:.4f}. Yaw: {yaw_degrees:.4f} deg. Joint '{example_joint_name}' is at position {example_joint_position_degrees:.4f} "
        f"deg. State estimator status: {event.state_estimator_state}"
    )
    return event


def anymal_physical_condition_callback(
    event: api.AnymalPhysicalConditionEvent,
) -> api.AnymalPhysicalConditionEvent:
    """Callback to be executed on ANYmal Physical Condition Event. Returns current State of Charge of the ANYmal."""
    # Extract the relevant timestamp for the event.
    timestamp = event.timestamp
    # The timestamp value is given in nanoseconds since Unix epoch.
    # We can convert it into seconds for user-friendliness.
    timestamp_secs = timestamp.value / 1e9
    robot_name = event.metadata.robot_name

    # Extract the battery information from the event.
    battery_soc = event.battery_state.state_of_charge.measurement  # [0-1]
    battery_voltage = event.battery_state.voltage.measurement  # [V]
    battery_status = event.battery_state.status

    # Extract the main body state
    humidity = event.main_body_state.relative_humidity.measurement  # [0-1]
    pressure = event.main_body_state.differential_pressure.measurement  # [mbar]
    temperature = event.main_body_state.temperature.measurement  # [Celsius]

    logging.info(
        f"Stamp: {timestamp_secs} - Robot {robot_name}. Battery SOC: {battery_soc*100:.2f}%, Voltage: {battery_voltage:.2f} V, Status: {api.BatteryStatus.Name(battery_status)}. "
        f"Main Body Relative Humidity: {humidity*100:.1}%, Pressure: {pressure:.4f} mbar, Temperature: {temperature:.2f} C."
    )
    return event


def control_status_callback(
    event: api.ControlStatus,
) -> api.ControlStatus:
    """Returns if the protective stop is engaged."""
    # Extract the relevant timestamp for the event.
    timestamp = event.timestamp
    # The timestamp value is given in nanoseconds since Unix epoch.
    # We can convert it into seconds for user-friendliness.
    timestamp_secs = timestamp.value / 1e9
    # Control authority.
    lease_status = event.lease
    lease_id = None
    client_name = None
    if lease_status:
        lease_id = lease_status.lease_id
        client_name = lease_status.client_name
    # Protective stop.
    protective_stop_status = event.protective_stop
    protective_stop_is_engaged = None
    protective_stop_origin = None
    if protective_stop_status:
        protective_stop_is_engaged = protective_stop_status.is_engaged
        protective_stop_origin = protective_stop_status.origin
    # logging.info relevant information about the robot state.
    logging.info(
        f"Stamp: {timestamp_secs}\n"
        f"Robot: {event.metadata.robot_name}\n"
        f"Control authority:\n"
        f"  Lease ID: '{lease_id if lease_id else 'FREE'}'\n"
        f"  Client name: '{client_name if client_name else ''}'\n"
        f"Is power cut: '{event.is_power_cut}'\n"
        f"Protective stop:\n"
        f"  Is engaged: '{'not set' if protective_stop_is_engaged is None else ('True' if protective_stop_is_engaged else 'False')}'\n"
        f"  Origin: '{'not set' if protective_stop_origin is None else protective_stop_origin}'\n"
        f"User Interaction Mode: '{api.UserInteractionMode.Name(event.user_interaction_mode)}'\n"
    )
    return event


def check_concentration_event(interpretation: api.ConcentrationInterpretation, substance: str):
    if interpretation.confidence_level == api.InterpretationConfidenceLevel.ICL_HIGH:
        if interpretation.concentration_level == api.SubstanceConcentrationLevel.SCL_LOW_ALARM:
            logging.warn(f"Low concentration level of {substance} detected! Take action immediately!")
        if interpretation.concentration_level == api.SubstanceConcentrationLevel.SCL_LOW_WARNING:
            logging.warn(f"Low concentration level of {substance} detected.")
        if interpretation.concentration_level == api.SubstanceConcentrationLevel.SCL_HIGH_WARNING:
            logging.error(f"High concentration level of {substance} detected.!")
        if interpretation.concentration_level == api.SubstanceConcentrationLevel.SCL_HIGH_ALARM:
            logging.error(f"High concentration level of {substance} detected! Take action immediately!")


def parse_interpretation(interpretation: api.InspectionInterpretation):
    # React differently depending on the type of inspection interpretation.
    if interpretation.type == api.InspectionInterpretationType.IIT_VISUAL_READOUT and interpretation.HasField(
        "visual_readout"
    ):
        readout = interpretation.visual_readout
        if readout.result == api.ResultInterpretation.RI_NOT_DETECTED:
            logging.info(
                f"Failure! Could not find the target from the current pose. The {readout.asset_type} might be occluded"
            )
            logging.info(f"Confidence: {readout.confidence:.2f}, Threshold: {readout.confidence_threshold:.2f}")
        elif readout.result == api.ResultInterpretation.RI_ANOMALY:
            logging.info(
                f"Anomaly! Measured a readout of {readout.estimate:.2f} {readout.estimate_units} with confidence {readout.confidence:.2f} w.r.t threshold {readout.confidence_threshold:.2f}"
            )
            logging.info(
                f"The result of {readout.estimate:.2f} {readout.estimate_units} is outside the range [ {readout.normal_operating_range.min:.2f} {readout.estimate_units}, {readout.normal_operating_range.max:.2f} {readout.estimate_units} ]"
            )
        else:
            logging.info(
                f"Measured a readout of {readout.estimate:.2f} {readout.estimate_units} with confidence {readout.confidence:.2f} for an asset of type {readout.asset_type}"
            )
            logging.info(
                f"The result of {readout.estimate:.2f} {readout.estimate_units} is within the range [ {readout.normal_operating_range.min:.2f} {readout.estimate_units}, {readout.normal_operating_range.max:.2f} {readout.estimate_units} ]"
            )
    elif (
        interpretation.type == api.InspectionInterpretationType.IIT_VISUAL_OBJECT_DETECTION
        and interpretation.HasField("visual_object_detection")
    ):
        detection = interpretation.visual_object_detection
        if detection.result == api.ResultInterpretation.RI_ANOMALY:
            logging.info(
                f"Anomaly! Failed to detect an object of type {detection.asset_type} with low confidence {detection.confidence:.2f} w.r.t threshold {detection.confidence_threshold:.2f}"
            )
        else:
            logging.info(
                f"Detected an object of type {detection.asset_type} with confidence {detection.confidence:.2f}"
            )
    elif (
        interpretation.type == api.InspectionInterpretationType.IIT_AUDITIVE_FREQUENCY_ANALYSIS
        and interpretation.HasField("auditive_frequency_analysis")
    ):
        frequency_analysis = interpretation.auditive_frequency_analysis
        detection_str = "detected" if frequency_analysis.frequency_detected else "did not detect"
        logging.info(
            f"Frequency analysis {detection_str} the frequency {frequency_analysis.desired_frequencies} with confidence {frequency_analysis.confidence:.2f}"
        )
        logging.info(f"Signal to noise ratio: {frequency_analysis.signal_to_noise_ratio:.2f}")
        max_freq= 192000 if frequency_analysis.configuration.is_ultrasonic else 22050
        step = max_freq / len(frequency_analysis.fft_frequency)
        for frequency in frequency_analysis.configuration.desired_frequencies:
            frequency_idx = int(frequency_analysis.desired_frequency / step)
            logging.info(
                f"Frequency {frequency_analysis.fft_frequency[frequency_idx]:.2f}Hz has a power of {frequency_analysis.fft_power[frequency_idx]}"
            )
        if frequency_analysis.result == api.ResultInterpretation.RI_NORMAL:
            if frequency_analysis.configuration.frequency_expected:
                logging.info(
                    f"The expected frequency of {frequency_analysis.configuration.desired_frequencies} Hz was correctly detected"
                )
            else:
                logging.info(f"The anomalous frequency of {frequency_analysis.configuration.desired_frequencies} Hz was not detected")
        elif frequency_analysis.result == api.ResultInterpretation.RI_ANOMALY:
            if frequency_analysis.configuration.frequency_expected:
                logging.info(
                    f"Anomaly! The expected frequency of {frequency_analysis.configuration.desired_frequencies} Hz was not detected!"
                )
            else:
                logging.info(
                    f"Anomaly! The anomalous frequency of {frequency_analysis.configuration.desired_frequencies} Hz was correctly detected"
                )
    elif (
        interpretation.type == api.InspectionInterpretationType.IIT_THERMAL_HOTSPOT_DETECTION
        and interpretation.HasField("thermal_hotspot")
    ):
        hotspot = interpretation.thermal_hotspot
        tempEvaluated = 0
        if hotspot.measured_temperature_type == api.MeasureTemperatureType.MTT_MIN:
            logging.info(
                f"Measured a minimum temperature of {hotspot.min_temperature:.2f}C with confidence {hotspot.confidence:.2f}"
            )
            tempEvaluated = hotspot.min_temperature
        elif hotspot.measured_temperature_type == api.MeasureTemperatureType.MTT_MAX:
            logging.info(
                f"Measured a maximum temperature of {hotspot.max_temperature:.2f}C with confidence {hotspot.confidence:.2f}"
            )
            tempEvaluated = hotspot.max_temperature
        elif hotspot.measured_temperature_type == api.MeasureTemperatureType.MTT_SPOT:
            logging.info(
                f"Measured a spot temperature of {hotspot.spot_temperature:.2f}C with confidence {hotspot.confidence:.2f}"
            )
            tempEvaluated = hotspot.spot_temperature
        elif hotspot.measured_temperature_type == api.MeasureTemperatureType.MTT_MEDIAN:
            logging.info(
                f"Measured a median temperature of {hotspot.median_temperature:.2f}C with confidence {hotspot.confidence:.2f}"
            )
            tempEvaluated = hotspot.median_temperature
        else:
            logging.info(
                f"Thermal hotspot interpretation with unknown temperature type {hotspot.measured_temperature_type}"
            )
            logging.info(
                f"Min temperature: {hotspot.min_temperature:.2f}C, Max temperature: {hotspot.max_temperature:.2f}C, Spot temperature: {hotspot.spot_temperature:.2f}C, Median temperature: {hotspot.median_temperature:.2f}C"
            )
        if hotspot.roi_diameter >= 0:
            logging.info(f"ROI diameter: {hotspot.roi_diameter} pixels")
        if hotspot.result == api.ResultInterpretation.RI_NORMAL:
            logging.info(
                f"The result of {tempEvaluated:.2f}C was normal within the range [ {hotspot.normal_operating_range.min:.2f}C, {hotspot.normal_operating_range.max:.2f}C ]"
            )
        elif hotspot.result == api.ResultInterpretation.RI_ANOMALY:
            logging.info(
                f"Anomaly! The result of {tempEvaluated:.2f}C was an anomaly outside the range [ {hotspot.normal_operating_range.min:.2f}C, {hotspot.normal_operating_range.max:.2f}C ]"
            )
    elif interpretation.type in [
        api.InspectionInterpretationType.IIT_THERMAL_FRAME_CAPTURE,
        api.InspectionInterpretationType.IIT_ACOUSTIC_IMAGE_FRAME_CAPTURE,
        api.InspectionInterpretationType.IIT_VISUAL_FRAME_CAPTURE,
        api.InspectionInterpretationType.IIT_VIDEO,
        api.InspectionInterpretationType.IIT_AUDITIVE_SAMPLE_CAPTURE,
    ]:
        pass
    elif interpretation.type == api.InspectionInterpretationType.IIT_LEAK_DETECTION and interpretation.HasField(
        "leak_detection"
    ):
        analysis = interpretation.leak_detection
        logging.info(f"Leak Detection:")
        logging.info(
            f"SPL measured at the source: {analysis.sound_pressure_level_at_source:.2f} dB, at a estimated distance of: {analysis.distance_to_source:.2f}m"
        )
        if analysis.result == api.ResultInterpretation.RI_ANOMALY:
            logging.info(
                f"Anomaly! Leak detected with a SNR of {analysis.snr_value:.2f} db, which is above the threshold of {analysis.configuration.snr_value_threshold:.2f}db"
            )
            logging.info(f"Leak rate: {analysis.leak_rate:.2f} {analysis.leak_rate_unit}")
            logging.info(f"Leak cost: {analysis.cost:.2f} {analysis.cost_unit} per year")
            logging.info(f"Electricity usage: {analysis.electricity_usage:.2f} {analysis.electricity_usage_unit}")

        elif analysis.result == api.ResultInterpretation.RI_NORMAL:
            logging.info(
                f"Leak below the threshold, SNR of {analysis.snr_value:.2f}db is below the threshold of {analysis.configuration.snr_value_threshold:.2f}db"
            )
        elif analysis.result == api.ResultInterpretation.RI_NOT_ACCURATE:
            logging.info(f"Leak was not measured accurately!")
        else:
            logging.info(f"Leak outcome is not normal or anomaly: {analysis.result}")
    elif (
        interpretation.type == api.InspectionInterpretationType.IIT_PARTIAL_DISCHARGE_DETECTION
        and interpretation.HasField("partial_discharge_detection")
    ):
        analysis = interpretation.partial_discharge_detection
        logging.info(f"Partial Discharge Detection:")
        logging.info(
            f"SPL measured at the source: {analysis.sound_pressure_level_at_source:.2f} dB, at a distance of: {analysis.distance_to_source:.2f}m"
        )
        if analysis.result == api.ResultInterpretation.RI_ANOMALY:
            logging.info(
                f"Anomaly! Partial Discharge detected with a SNR of {analysis.snr_value:.2f}db above the threshold of {analysis.configuration.snr_value_threshold:.2f}db"
            )
            logging.info(
                f"PD type probability: External {analysis.external_probability:.2f}, Internal {analysis.internal_probability:.2f}, Surface {analysis.surface_tracking_probability:.2f}"
            )
        elif analysis.result == api.ResultInterpretation.RI_NORMAL:
            logging.info(
                f"Partial Discharge below the threshold, SNR of {analysis.snr_value:.2f}db is below the threshold of {analysis.configuration.snr_value_threshold:.2f}db"
            )
        else:
            logging.info(f"Partial Discharge outcome is not normal or anomaly: {analysis.result}")
    elif interpretation.type == api.InspectionInterpretationType.IIT_MECHANICAL_INSPECTION and interpretation.HasField(
        "mechanical_inspection"
    ):
        analysis = interpretation.mechanical_inspection
        logging.info(f"Mechanical Inspection:")
        thumbnail_acoustic_image = analysis.thumbnail_acoustic_image
        show_image(
            thumbnail_acoustic_image.image,
            f"Mechanical Inspection Image thumbnail {thumbnail_acoustic_image.frequency_range.min}-{thumbnail_acoustic_image.frequency_range.max}Hz",
        )
        logging.info(f"Image size: {thumbnail_acoustic_image.image.width}x{thumbnail_acoustic_image.image.height}")
        logging.info(
            f"SPL measured at the source: {analysis.sound_pressure_level_at_source:.2f} dB, at a distance of: {analysis.distance_to_source:.2f}m"
        )
        if analysis.result == api.ResultInterpretation.RI_ANOMALY:
            logging.info(
                f"Anomaly! Mechanical issue detected with a SNR of {analysis.snr_value:.2f}db above the threshold of {analysis.configuration.snr_value_threshold:.2f}db"
            )
        elif analysis.result == api.ResultInterpretation.RI_NORMAL:
            logging.info(
                f"Mechanical issue below the threshold, SNR of {analysis.snr_value:.2f}db is below the threshold of {analysis.configuration.snr_value_threshold:.2f}db"
            )
        else:
            logging.info(f"Mechanical Inspection outcome is not normal or anomaly: {analysis.result}")
    elif interpretation.type == api.InspectionInterpretationType.IIT_CONCENTRATION and interpretation.HasField(
        "concentration"
    ):
        pass
    else:
        logging.info(
            f"Interpretation type {api.InspectionInterpretationType.Name(interpretation.type)} not yet implemented"
        )


def inspection_callback(event: api.InspectionEvent):
    # React differently depending on the type of inspection measurement.
    if event.measurement.type == api.InspectionMeasurementType.IMT_THERMAL:
        logging.info(f"Thermal callback event for asset {event.asset_id}.")
        logging.info(f"The interpretation image for {event.asset_id} is uploaded as {event.task_run_uid}_interpretation_0.jpg")
        create_download_request(event.task_run_uid, event.asset_id, "interpretation_0.jpg")
    elif event.measurement.type == api.InspectionMeasurementType.IMT_VISUAL:
        logging.info(f"Visual callback event for asset {event.asset_id}.")
        if event.interpretations[0].type == api.InspectionInterpretationType.IIT_VISUAL_FRAME_CAPTURE:
            logging.info(f"The image for {event.asset_id} is uploaded as {event.task_run_uid}_measurement.jpg")
            create_download_request(event.task_run_uid, event.asset_id, "measurement.jpg")
        else:
            logging.info(f"The image for {event.asset_id} is uploaded as {event.task_run_uid}_measurement.jpg")
            logging.info(f"The interpretation image for {event.asset_id} is uploaded as {event.task_run_uid}_interpretation_0.jpg")
            create_download_request(event.task_run_uid, event.asset_id, "interpretation_0.jpg")
    elif event.measurement.type == api.InspectionMeasurementType.IMT_VIDEO:
        logging.info(f"Video Recording callback event for asset {event.asset_id}.")
        logging.info("Video Data:")
        video = event.measurement.video
        logging.info(f"Timestamp: {video.timestamp.value}, Frame ID: {video.frame_id}")
        logging.info(f"Digest:{video.digest}, Camera Type: {video.camera_type}")
        logging.info(f"File Size: {video.file_size}, Duration: {video.duration}, Frame Rate: {video.frame_rate}")
        logging.info(f"Width: {video.width}, Height: {video.height}, File Type: {video.file_type}")
        logging.info(
            f"Video Bitrate: {video.video_params.bit_rate}, Encoding: {video.video_params.encoding}, Pixel Format: {video.video_params.format}"
        )
        logging.info(f"Audio Bitrate: {video.audio_params.bit_rate}, Encoding: {video.audio_params.encoding}")
        if video.video_data:
            logging.info(f"Received {len(video.video_data)} bytes of video data.")
        logging.info(f"The video for {event.asset_id} is uploaded as {event.task_run_uid}_measurement.mp4")
        create_download_request(event.task_run_uid, event.asset_id, "measurement.mp4")
    elif event.measurement.type == api.InspectionMeasurementType.IMT_AUDITIVE:
        logging.info(f"Auditive callback event for asset {event.asset_id}.")
        play_audio(event.measurement.auditive)
        logging.info(f"The audio file for {event.asset_id} is uploaded as {event.task_run_uid}_measurement.wav")
        create_download_request(event.task_run_uid, event.asset_id, "measurement.wav")
    elif event.measurement.type == api.InspectionMeasurementType.IMT_ACOUSTIC_IMAGE:
        logging.info(f"Acoustic image callback event for asset {event.asset_id}.")
        logging.info(f"The image for {event.asset_id} is uploaded as {event.task_run_uid}_measurement.jpg")
        logging.info(f"The interpretation image for {event.asset_id} is uploaded as {event.task_run_uid}_interpretation_0.jpg")
        create_download_request(event.task_run_uid, event.asset_id, "interpretation_0.jpg")
    elif event.measurement.type == api.InspectionMeasurementType.IMT_CONCENTRATION:
        concentration_measurement = event.measurement.concentration
        interpretation = event.interpretations[0].concentration
        logging.info(
            f"Concentration callback event for area {event.asset_id} and substance {concentration_measurement.sensor_properties.substance}."
        )
        logging.info(
            f"Concentration value: {concentration_measurement.value.measurement:.3f} {concentration_measurement.sensor_properties.unit} with confidence {interpretation.confidence}"
        )
        check_concentration_event(interpretation, concentration_measurement.sensor_properties.substance)
    elif event.measurement.type == api.InspectionMeasurementType.IMT_CONCENTRATION_MONITORING:
        # For continuous monitoring, just check the concentration level to avoid constant logging
        check_concentration_event(
            event.interpretations[0].concentration, event.measurement.concentration.sensor_properties.substance
        )
    else:
        logging.info(f"Unknown callback event for asset {event.asset_id}.")

    # Then parse the interpretations available
    for interpretation in event.interpretations:
        parse_interpretation(interpretation)


def create_download_request(task_id, asset_id, file_type) -> None:
    Path(REQUESTS_PATH / build_request_filename(task_id, asset_id , file_type)).touch()


def build_request_filename(task_id, asset_id, file_type) -> Path:
    return Path(f"rq__{asset_id}__{task_id}_{file_type}")


def mission_callback(
    event: api.MissionEvent,
) -> api.MissionEvent:
    """Return True if mission was completed."""
    timestamp = event.timestamp.value
    mission_summary = event.mission_summary
    logging.info(
        f"[{timestamp}]: Mission {event.metadata.mission_run_id} has status {api.MissionStatus.Name(mission_summary.status)}."
    )
    for task_summary in mission_summary.task_summaries:
        task_status = task_summary.status
        if task_status == api.TaskStatus.TS_COMPLETED:
            logging.info(
                f"[{timestamp}]: Task {task_summary.task_id} completed with outcome {api.Outcome.Name(task_summary.outcome)}."
            )
        elif task_status == api.TaskStatus.TS_ONGOING:
            task_progress = task_summary.progress
            logging.info(
                f"[{timestamp}]: Task {task_summary.task_id} has progress "
                f"{task_progress.progress}/{task_progress.target}[{task_progress.unit}]."
            )
    if mission_summary.status == api.MissionStatus.MS_COMPLETED:
        logging.info(f"[{timestamp}]: Mission has completed with outcome {api.Outcome.Name(mission_summary.outcome)}.")
    return event


def display_mission_plan(mission_plan: MissionPlan):
    tasks = mission_plan.getTasks()
    logging.info("TaskID\tAsset\n")
    for t in tasks[:-1]:
        logging.info(f"{t.getTaskId()}\t{t.getInspectionTask().getAssetId()}")
    logging.info(f"{tasks[-1].getTaskId()}\t{tasks[-1].getOperationalMode().getOperationalMode()}")


def configure_adhoc_mission(mission_id) -> api.AnyMissionDescription:
    """
    Add tasks or start current mission. Choose the initial task. Return the mission plan and the initial task.
    """
    tasks = []
    while True:
        user_choice = input(
            "Add an inspection asset to the task list or start the current mission.\n1. Add asset.\n2. Start current mission\n"
        )
        if user_choice == "1":
            print("Select the type of asset to inspect:")
            for key in AD_HOC_TASK_LIST_OPTIONS.keys():
                print(f"{key}. {AD_HOC_TASK_LIST_OPTIONS[key][0]}")
            asset_type_number = input(f"Type: ")
            asset_id = input(f"Enter point of interest ID of type: ")
            tasks.append(create_task(asset_type_number, asset_id))
        elif user_choice == "2":
            break
        else:
            logging.info("Invalid option")
            continue

    add_dock = input("Add a docking task at the end? (y/n): ")
    if add_dock.lower() == "y":
        dock_task = api.AnyTaskDescription()
        dock_task.description.generic.uid = "Dock"
        dock_task.description.dock.docking_station = "Suggested"
        tasks.append(dock_task)

    mission_description = api.AnyMissionDescription()
    mission_description.ad_hoc.metadata.mission_uid = mission_id
    for task in tasks:
        mission_description.ad_hoc.task_descriptions.append(task)

    return mission_description


def create_task(asset_type_number, asset_id) -> api.AnyTaskDescription:
    """
    Create a task description for the mission.
    """
    task = api.AnyTaskDescription()
    if AD_HOC_TASK_LIST_OPTIONS[asset_type_number][1] == "navigation":
        task.description.navigation.navigation_goal.uid = asset_id
        task.description.navigation.path_planning_type = api.PathPlanningType.PPT_ALONG_WAYPOINTS
    elif AD_HOC_TASK_LIST_OPTIONS[asset_type_number][1] == "image":
        task.description.image.poi.uid = asset_id
    elif AD_HOC_TASK_LIST_OPTIONS[asset_type_number][1] == "thermal_assessment":
        task.description.thermal_assessment.poi.uid = asset_id
    elif AD_HOC_TASK_LIST_OPTIONS[asset_type_number][1] == "video_recording":
        task.description.video_recording.poi.uid = asset_id
    elif AD_HOC_TASK_LIST_OPTIONS[asset_type_number][1] == "audio_recording":
        task.description.audio_recording.poi.uid = asset_id
    elif AD_HOC_TASK_LIST_OPTIONS[asset_type_number][1] == "frequency_assessment":
        task.description.frequency_assessment.poi.uid = asset_id
    elif AD_HOC_TASK_LIST_OPTIONS[asset_type_number][1] == "gauge_assessment":
        task.description.gauge_assessment.poi.uid = asset_id
    else:
        logging.error(f"Unknown asset type {asset_type_number}.")
        raise ValueError(f"Unknown asset type {asset_type_number}.")
    task.description.generic.uid = f"Ad-Hoc Inspect {asset_id}"

    print(f"Added task: {task.description.generic.uid} of type {AD_HOC_TASK_LIST_OPTIONS[asset_type_number][0]}")
    return task


# The ANYmal API allows to send the robot to arbitrary locations.
# NOTE: this is just an example, which is dependent on the environment used. Some details below.
# The robot might not be able to reach that location safely!
# The docking station might not be defined in the environment.
# The robot might not be able to reach the docking station from this location, impairing the automatic reactions to low battery and low main body pressure!
# Usage at your own risk.
def example_adhoc_navigation_mission() -> api.AnyMissionDescription:
    task1 = api.AnyTaskDescription()
    task1.description.generic.uid = "Go-To Predefined"
    task1.description.navigation.navigation_goal.uid = "DockingStationNavigationGoal"
    task1.description.navigation.path_planning_type = api.PathPlanningType.PPT_ALONG_WAYPOINTS

    task2 = api.AnyTaskDescription()
    task2.description.generic.uid = "Go-To Ad-Hoc Pose #1"
    task2.description.navigation.navigation_goal.detailed.pose.CopyFrom(
        create_pose("map", -3.43, 1.03, 0.54, 0.0, 0.0, 0.0, 1.0)
    )
    task2.description.navigation.path_planning_type = api.PathPlanningType.PPT_DIRECT

    task3 = api.AnyTaskDescription()
    task3.description.generic.uid = "Go-To Ad-Hoc Pose #2"
    task3.description.navigation.navigation_goal.detailed.pose.CopyFrom(
        create_pose("map", 3.43, 1.03, 0.54, 0.0, 0.0, 1.0, 0.0)
    )
    task3.description.navigation.path_planning_type = api.PathPlanningType.PPT_ALONG_WAYPOINTS

    task4 = api.AnyTaskDescription()
    task4.description.generic.uid = "Dock To Suggested"
    task4.description.dock.docking_station = (
        ""  # or "Suggested" -- Empty string implicitly implies to use the suggested docking station.
    )
    # Alternatively, define explicity which docking station (ID) to use.
    # task4.description.dock.docking_station="DockingStation"

    mission_description = api.AnyMissionDescription()
    mission_description.ad_hoc.metadata.mission_uid = "Testing Mission"
    for task in [task1, task2, task3, task4]:
        mission_description.ad_hoc.task_descriptions.append(task)

    return mission_description


def create_predefined_mission() -> api.AnyMissionDescription:
    mission_id = input("Id of the mission: ")
    initial_task = input("Execute mission from this task (leave empty to execute from the start): ")
    if not initial_task:
        initial_task = ""

    mission_description = api.AnyMissionDescription()
    mission_description.predefined.mission_uid = mission_id
    mission_description.predefined.starting_task_uid = initial_task
    return mission_description
