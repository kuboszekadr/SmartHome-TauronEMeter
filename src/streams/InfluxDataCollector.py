from datetime import datetime as dt
from typing import Dict, List, Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import logging
import os

class InfluxDataCollector(BaseSettings):
    """
    Data collector for sending Tauron EMeter data to InfluxDB
    """
    url: str
    token: str
    org: str
    bucket: str

    measurement: str = Field(default="tauron_energy", exclude=True)
    device_name: str = Field(default="tauron_emeter", exclude=True)

    client: Any = Field(default=None, exclude=True)
    write_api: Any = Field(default=None, exclude=True)

    model_config = {
        "env_prefix": "INFLUX_",
        "case_sensitive": False,
        "env_file_encoding": "utf-8",
        "arbitrary_types_allowed": True
    }

    def model_post_init(self, __context: Any) -> None:
        """Initialize InfluxDB client after model initialization"""
        self.client = InfluxDBClient(
            url=self.url, 
            token=self.token, 
            org=self.org
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def test_connection(self) -> bool:
        """Test connection to InfluxDB"""
        health = self.client.health()
        if health.status == "pass":
            logging.info("Successfully connected to InfluxDB")
            return True
        else:
            logging.error(f"InfluxDB health check failed: {health.status}")
            return False

    def _write_point(self, measurement: str, tags: Dict[str, str], fields: Dict[str, Any], timestamp: dt = None) -> None:
        """Write a point to InfluxDB"""
        point = Point(measurement)
        
        for tag_key, tag_value in tags.items():
            point = point.tag(tag_key, tag_value)
        
        for field_key, field_value in fields.items():
            point = point.field(field_key, field_value)
        
        if timestamp is not None:
            point = point.time(timestamp, WritePrecision.S)

        try:
            self.write_api.write(
                bucket=self.bucket, 
                org=self.org, 
                record=point
            )
            logging.debug(f"Successfully wrote new point to InfluxDB: {measurement}")
        except Exception as e:
            logging.error(f"Failed to write point to InfluxDB: {e}")
            raise

    def _process_energy_data(self, data: Dict[str, Any], file_path: str) -> None:
        """Process energy data and send to InfluxDB"""
        if not data.get('success', False):
            logging.warning(f"Data from {file_path} indicates failure")
            return

        energy_data = data.get('data', {})
        hourly_values = energy_data.get('values', [])
        hourly_labels = energy_data.get('labels', [])
        daily_total = energy_data.get('sum', 0)
        tariff = energy_data.get('tariff', 'unknown')
        
        # Extract date and data type from file path
        file_name = os.path.basename(file_path)
        date_str = file_name[:10]  # YYYY-MM-DD
        data_type = 'consumption' if '_consum' in file_name else 'generation'
        
        # Common tags for all points
        common_tags = {
            'device': self.device_name,
            'data_type': data_type,
            'tariff': tariff,
            'source': 'Tauron'
        }
        
        self._write_daily_total_point(date_str, daily_total, data_type, tariff)
        self._write_hourly_points(date_str, hourly_values, hourly_labels, common_tags)

    def _write_daily_total_point(self, date: str, total_value: float, data_type: str, tariff: str) -> None:
        """Write total daily point to InfluxDB"""
        point_value = {
            'daily_total': total_value,
            'unit': 'kWh'
        }
        point_tags = {
            'device': self.device_name,
            'data_type': data_type,
            'tariff': tariff,
            'aggregation': 'daily',
            'source': 'Tauron'
        }
        point_timestamp = dt.strptime(f"{date} 23:59:59", "%Y-%m-%d %H:%M:%S")

        self._write_point(
            measurement=f"{self.measurement}_daily_total",
            tags=point_tags,
            fields=point_value,
            timestamp=point_timestamp
        )

    def _write_hourly_points(self, date: str, hourly_values: Dict[str, Any], hourly_labels: List[str], common_tags: Dict[str, str]) -> None:
        point_value = {
            'value': None,
            'unit': 'kWh'
        }

        points_data = zip(hourly_labels, hourly_values)

        for hour, value in points_data:
            point_value['value'] = float(value)
            point_datetime = dt.strptime(
                f"{date} {hour-1:02d}:00:00",
                "%Y-%m-%d %H:%M:%S"
            )
            point = (
                f"{self.measurement}_hourly",
                {**common_tags, 'aggregation': 'hourly'},
                point_value,
                point_datetime
            )
            self._write_point(*point)

    def stream(self, data: Dict[str, Any], file_path: str) -> None:
        """
        Stream energy data to InfluxDB
        
        Args:
            data: The energy data dictionary from JSON files
            file_path: Optional file path to extract metadata
        """
        if not data:
            logging.info("No data to stream")
            return

        self._process_energy_data(data, file_path)
        logging.info(f"Successfully streamed data to InfluxDB")

    def close(self) -> None:
        """Close InfluxDB client connections"""
        if hasattr(self, 'write_api'):
            self.write_api.close()
        if hasattr(self, 'client'):
            self.client.close()