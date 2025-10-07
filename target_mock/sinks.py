"""Mock target sinks."""

import json
import hashlib
from datetime import datetime
from singer_sdk.plugin_base import PluginBase
from target_hotglue.client import HotglueBatchSink
from target_hotglue.common import HGJSONEncoder
from typing import Dict, List, Optional


class MockSink(HotglueBatchSink):
    """Base sink class for mock target."""
    
    endpoint = "/mock"
    max_size = 30  # Max records to write in one batch

    @property
    def is_full(self):
        # Checks if all records were already read
        if self.name in self._target.target_counter:
            all_records_were_read = self._total_records_read == self._target.target_counter[self.name]
        elif self.stream_name in self._target.target_counter:
            all_records_were_read = self._total_records_read == self._target.target_counter[self.stream_name]
        else:
            raise Exception(f"Stream name from record doesn't match schema. Name={self.name}, StreamName={self.stream_name}, TargetCounter={self._target.target_counter}")

        # Checks if the max batch size was reached
        max_batch_size_reached = self._total_records_read % self.max_size == 0

        return all_records_were_read or max_batch_size_reached

    @property
    def base_url(self) -> str:
        return "https://api.mock.com/v1"

    @property
    def authenticator(self):
        auth_type = self.config.get("auth_type")
        if auth_type == "oauth":
            return {"Authorization": f"Bearer {self.config.get('access_token')}"}
        elif auth_type == "api_key":
            return {"X-API-Key": self.config.get("api_key")}
        else:
            raise ValueError(f"Unsupported auth_type: {auth_type}")

    def __init__(self, target: PluginBase, stream_name: str, schema: Dict, key_properties: Optional[List[str]]) -> None:
        super().__init__(target, stream_name, schema, key_properties)

    def validate_input(self, record: dict):
        return True
    
    def parse_objs(self, obj):
        if isinstance(obj, str):
            try:
                return json.loads(obj)
            except:
                try:
                    import ast
                    return ast.literal_eval(obj)
                except:
                    return obj
        return obj

    def build_record_hash(self, record: dict):
        """Build a hash for the record to track state."""
        return hashlib.sha256(json.dumps(record, cls=HGJSONEncoder).encode()).hexdigest()

    def get_existing_state(self, hash: str):
        """Get existing state for a record hash."""
        if not self.latest_state or "bookmarks" not in self.latest_state:
            return None
            
        states = self.latest_state["bookmarks"].get(self.name, [])
        existing_state = next((s for s in states if hash == s.get("hash") and s.get("success")), None)

        if existing_state:
            if "summary" in self.latest_state and self.name in self.latest_state["summary"]:
                self.latest_state["summary"][self.name]["existing"] += 1

        return existing_state

    def start_batch(self, context: dict) -> None:
        """Initialize batch context."""
        context["records"] = []

    def process_batch_record(self, record: dict, index: int) -> dict:
        """Process a single record in the batch."""
        return record

    def process_batch(self, context: dict) -> None:
        """Process a batch of records."""
        if not self.latest_state:
            self.init_state()
        
        batch_records = context.get("records", [])
        if not batch_records:
            return

        for record in batch_records:
            self.process_single_record(record)

    def process_single_record(self, record: dict) -> None:
        """Process a single record and update state."""
        record_hash = self.build_record_hash(record)
        existing_state = self.get_existing_state(record_hash)
        
        # Check if record exists (has an ID)
        if record.get("id"):
            # Update existing record
            state = {
                "success": True,
                "id": record.get("id"),
                "externalId": record.get("externalId"),
                "hash": record_hash,
                "updated_at": datetime.now().isoformat()
            }
            self.update_state(state)
            
            # Update summary
            if "summary" in self.latest_state and self.name in self.latest_state["summary"]:
                self.latest_state["summary"][self.name]["updated"] += 1
        else:
            # Create new record
            # Generate a mock ID
            import hashlib
            mock_id = str(int(hashlib.md5(record.get("externalId", "").encode()).hexdigest()[:8], 16) % 100000)
            
            state = {
                "success": True,
                "id": mock_id,
                "externalId": record.get("externalId"),
                "hash": record_hash,
                "created_at": datetime.now().isoformat()
            }
            self.update_state(state)
            
            # Update summary
            if "summary" in self.latest_state and self.name in self.latest_state["summary"]:
                self.latest_state["summary"][self.name]["success"] += 1

    def init_state(self) -> None:
        """Initialize the state structure."""
        self.latest_state = {
            "bookmarks": {
                self.name: []
            },
            "summary": {
                self.name: {
                    "success": 0,
                    "fail": 0,
                    "existing": 0,
                    "updated": 0
                }
            }
        }

    def update_state(self, state: dict) -> None:
        """Update the state with a new record state."""
        if not self.latest_state:
            self.init_state()
        
        # Add to bookmarks
        if "bookmarks" not in self.latest_state:
            self.latest_state["bookmarks"] = {}
        if self.name not in self.latest_state["bookmarks"]:
            self.latest_state["bookmarks"][self.name] = []
        
        self.latest_state["bookmarks"][self.name].append(state)
        
        # Emit state
        self._target._write_state_message(self.latest_state)


class CustomerSink(MockSink):
    """Sink for Customer records."""
    
    name = "Customers"

    def process_record(self, record: dict, context: dict) -> None:
        """Process a customer record."""
        if not context.get("records"):
            context["records"] = []

        optional_external_id = self.config.get("optional_external_id") == True

        # Validate required fields
        if not record.get("externalId") and not optional_external_id:
            state = {
                "success": False,
                "error": "externalId is required",
                "hash": self.build_record_hash(record)
            }
            self.update_state(state)
            
            # Update summary
            if "summary" in self.latest_state and self.name in self.latest_state["summary"]:
                self.latest_state["summary"][self.name]["fail"] += 1
            return

        context["records"].append(record)

    def make_batch_request(self, batch_requests, params={}):
        """Make a batch request to the mock API."""
        # This is a mock implementation - in a real scenario, this would make HTTP requests
        # For now, we just return a mock response
        return {
            "status": "success",
            "processed": len(batch_requests),
            "results": [{"success": True, "id": f"mock_id_{i}"} for i in range(len(batch_requests))]
        } 