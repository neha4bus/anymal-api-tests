INSPECTIONS_PATH = "inspections"
REQUESTS_PATH = INSPECTIONS_PATH + "/requests"

# Description from https://code.anymal.com/anymal/code_examples/-/blob/release-25.06/api_examples/anymal_api_proto/proto/anymal_api_proto/task.proto?ref_type=heads#L267
AD_HOC_TASK_LIST_OPTIONS = {"1" : ["Navigation", "navigation"],
                            "2" : ["Visual", "image"],
                            "3" : ["Thermal", "thermal_assessment"],
                            "4" : ["Video Recording", "video_recording"],
                            "5" : ["Audio Recording", "audio_recording"],
                            "6" : ["Frequency", "frequency_assessment"],
                            "7" : ["Gauge Reading", "gauge_assessment"]
                            }