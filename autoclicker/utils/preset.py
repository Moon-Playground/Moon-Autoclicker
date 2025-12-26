import os
import sys
import tomlkit
import tomllib

class Presets:
    DEFAULT_PRESETS = {
        'default': {
            'hours': 0,
            'minutes': 0,
            'seconds': 0,
            'milliseconds': 100
        }
    }

    def save_new_preset(self, filepath="preset.toml", preset_name="default"):
        try:
            # Sync any variables if necessary before saving
            data = {
                preset_name: {
                    'hours': self.delay_hours,
                    'minutes': self.delay_minutes,
                    'seconds': self.delay_seconds,
                    'milliseconds': self.delay_milliseconds
                }
            }
            current = self.load_presets(filepath)
            current.update(data)
            with open(filepath, "w") as f:
                tomlkit.dump(current, f)
        except Exception as e:
            print(f"Error saving preset: {e}")

    def load_presets(self, filepath="preset.toml"):
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                return tomllib.load(f)
        else:
            # Create config file if not exists
            try:
                with open(filepath, "w") as f:
                    tomlkit.dump(self.DEFAULT_PRESETS, f)
            except:
                pass 
            return self.DEFAULT_PRESETS

    def delete_preset(self, preset_name, filepath="preset.toml"):
        if preset_name == "default":
            return False
        try:
            current = self.load_presets(filepath)
            if preset_name in current:
                current.pop(preset_name)
                with open(filepath, "w") as f:
                    tomlkit.dump(current, f)
                return True
        except Exception as e:
            print(f"Error deleting preset: {e}")
        return False
