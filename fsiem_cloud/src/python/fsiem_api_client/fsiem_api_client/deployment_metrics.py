from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class DeploymentMetrics:
    """Class for keeping track of deployment metrics"""
    # S3 metrics
    s3_archive_bucket: str = ''
    s3_archive_dir: str = ''
    s3_archive_size_bytes: int = 0
    s3_archive_objects_count: int = 0
    s3_updated_on: datetime = datetime.utcnow()

    # Online storage metric
    online_size_bytes: int = 0
    online_metrics_json_str: str = ''


@dataclass
class DfResponseItem:
    device: str = ''
    size_unit: str = ''
    total_size: int = 0
    used_size: int = 0
    available_size: int = 0
    capacity_utilization: str = ''
    mount_point: str = ''


@dataclass
class DfResponse:
    total_size: int = 0
    size_unit: str = ''
    items: list[DfResponseItem] = field(default_factory=list)

    def to_json_str(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)
