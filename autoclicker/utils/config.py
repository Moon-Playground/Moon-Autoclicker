import os
import sys
import tomlkit
import tomllib

class Config:
    DEFAULT_CONFIG = {
        'hotkeys': {
            'toggle_action': 'F6',
            'exit_app': 'F7'
        }
    }

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def save_settings(self, filepath="config.toml"):
        try:
            # Sync any variables if necessary before saving
            self.save_config(filepath)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def save_config(self, filepath="config.toml"):
        cfg_data = {
            'hotkeys': {
                'toggle_action': self.hk_action,
                'exit_app': self.hk_exit
            }
        }
        with open(filepath, "w") as f:
            tomlkit.dump(cfg_data, f)

    def load_config(self, filepath="config.toml"):
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                return tomllib.load(f)
        else:
            # Create config file if not exists
            try:
                with open(filepath, "w") as f:
                    tomlkit.dump(self.DEFAULT_CONFIG, f)
            except:
                pass 
            return self.DEFAULT_CONFIG
