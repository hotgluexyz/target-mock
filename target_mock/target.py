"""Mock target class."""

from hotglue_singer_sdk import typing as th
from hotglue_singer_sdk.target_sdk.target import TargetHotglue
import atexit
import json
import logging
import os

from target_mock.sinks import CustomerSink


class TargetMock(TargetHotglue):
    """Mock target for testing purposes."""

    name = "target-mock"
    target_counter = {}
    MAX_PARALLELISM = 1
    
    config_jsonschema = th.PropertiesList(
        th.Property("auth_type", th.StringType, required=True),
        th.Property("client_id", th.StringType, required=False),
        th.Property("client_secret", th.StringType, required=False),
        th.Property("refresh_token", th.StringType, required=False),
        th.Property("rotate_refresh_token", th.BooleanType, required=False, default=False),
        th.Property("next_refresh_token", th.StringType, required=False),
        th.Property("access_token", th.StringType, required=False),
        th.Property("api_key", th.StringType, required=False),
    ).to_dict()
    
    SINK_TYPES = [
        CustomerSink,
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log_authentication()
        self._handle_refresh_token_rotation()

    def _log_authentication(self):
        """Log the authentication method being used."""
        auth_type = self.config.get("auth_type")
        if auth_type == "oauth":
            logging.info("Authenticating with OAuth...")
            access_token = self.config.get("access_token")
            if access_token:
                logging.info(f"Using access token: {access_token[:10]}...")
            else:
                logging.info("No access token provided")
            logging.info("OAuth authentication successful")
        elif auth_type == "api_key":
            logging.info("Authenticating with API key...")
            api_key = self.config.get("api_key")
            if api_key:
                logging.info(f"Using API key: {api_key[:10]}...")
            else:
                logging.info("No API key provided")
            logging.info("API key authentication successful")
        else:
            logging.warning(f"Unknown auth_type: {auth_type}")

    def _handle_refresh_token_rotation(self):
        """Handle refresh token rotation if enabled in config (OAuth only)."""
        config = self.config
        if config.get("auth_type") == "oauth" and config.get("rotate_refresh_token", False):
            logging.info("Rotating refresh token...")
            next_refresh_token = config.get("next_refresh_token")
            if not next_refresh_token:
                raise ValueError("rotate_refresh_token is true but next_refresh_token is not provided in config")
            original_refresh_token = config.get("refresh_token")
            # Update config file if possible
            config_file_path = getattr(self, "_config_file_path", None)
            if config_file_path and os.path.exists(config_file_path):
                import json
                with open(config_file_path, "r") as f:
                    config_data = json.load(f)
                config_data["refresh_token"] = next_refresh_token
                if original_refresh_token:
                    config_data["original_refresh_token"] = original_refresh_token
                    logging.info("Stored original refresh token in config file")
                with open(config_file_path, "w") as f:
                    json.dump(config_data, f, indent=2)
                logging.info(f"Updated config file: {config_file_path}")
            logging.info("Refresh token rotated successfully")
            logging.info(f"New refresh token: {next_refresh_token}")

    def _process_lines(self, file_input):
        """
        Custom _process_lines method that enables single sink processing,
        adding a counter dictionary to the target.
        """
        lines = []
        for line in file_input:
            lines.append(line)
            line_dict = json.loads(line)
            if line_dict.get("type") != "RECORD":
                continue
            self.target_counter[line_dict["stream"]] = self.target_counter.get(
                line_dict["stream"], 0
            ) + 1

        super()._process_lines(lines)
    
    def _process_record_message(self, message_dict: dict) -> None:
        if message_dict["stream"] not in self.mapper.stream_maps:
            sink = self.get_sink_class(message_dict["stream"])
            message_dict["stream"] = sink.name
        return super()._process_record_message(message_dict)

    def get_sink_class(self, stream_name: str):
        for sink_class in self.SINK_TYPES:
            if sink_class.name.lower() == stream_name.lower():
                return sink_class


if __name__ == "__main__":
    TargetMock.cli() 