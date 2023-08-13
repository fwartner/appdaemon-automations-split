"""Splits automation.yaml into seperate automation files.

# Example `apps.yaml` config:
```
split_automation:
  module: split_automations
  class: SplitAutomation
  schedule_type: time  # Use "time" or "cron"
  schedule_value: 16:30  # Specify the time in "HH:MM" format or a cron expression
```
"""

import hassapi as hass
import os
import yaml
import datetime
import unicodedata
import re

class SplitAutomation(hass.Hass):

    def initialize(self):
        self.split_dir = "/config/custom_configs/automations"
        self.automations_file = "/config/automations.yaml"

        # Get configuration values or use defaults
        self.schedule_type = self.args.get("schedule_type", "time")  # "time" or "cron"
        self.schedule_value = self.args.get("schedule_value", "16:41")  # Time or cron expression

        if not os.path.exists(self.split_dir):
            os.makedirs(self.split_dir)

        self.setup_schedule()

    def setup_schedule(self):
        if self.schedule_type == "time":
            schedule_time = datetime.datetime.strptime(self.schedule_value, "%H:%M").time()
            self.run_daily(self.split_and_update_automations, schedule_time)
        elif self.schedule_type == "cron":


    def split_and_update_automations(self, kwargs):
        self.log("Splitting and updating automations...")

        automations = self._read_yaml_file(self.automations_file)
        split_automation_names = []

        for automation in automations:
            automation_name = self._get_normalized_name(automation)
            split_filename = os.path.join(self.split_dir, f"{automation_name}.yaml")

            existing_automation = self._read_yaml_file(split_filename) if os.path.exists(split_filename) else None

            if existing_automation != automation:
                automation_with_name = {"name": automation.get("alias", "Unnamed_Automation"), **automation}
                self._write_yaml_file(split_filename, automation_with_name)
                split_automation_names.append(automation_name)

        updated_automations = [automation for automation in automations if self._get_normalized_name(automation) not in split_automation_names]
        self._write_yaml_file(self.automations_file, updated_automations)

        self.log("Automations split and updated successfully.")

    def _read_yaml_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def _write_yaml_file(self, file_path, data):
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, default_flow_style=False, allow_unicode=True)

    def _get_normalized_name(self, item):
        alias = item.get("alias", "Unnamed_Automation")
        normalized_alias = self._normalize_string(alias)
        return re.sub(r'[^a-zA-Z0-9_]', '_', normalized_alias).lower()

    def _normalize_string(self, text):
        normalized_text = unicodedata.normalize("NFKD", text)
        return normalized_text.encode("ascii", "ignore").decode("utf-8")
