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
        """ Get absolute path to resource, works for dev and for PyInstaller/Nuitka """
        if getattr(sys, 'frozen', False):
            # If frozen (PyInstaller, Nuitka, cx_Freeze)
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller
                base_path = sys._MEIPASS
            else:
                # Nuitka, cx_Freeze
                base_path = os.path.dirname(sys.executable)
        else:
            # Development: use the directory of the package
            # This file is in autoclicker/utils, so the package root is one level up
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        full_path = os.path.join(base_path, relative_path)
        
        # Fallback to CWD if not found, for backward compatibility
        if not os.path.exists(full_path):
            cwd_path = os.path.join(os.path.abspath("."), relative_path)
            if os.path.exists(cwd_path):
                return cwd_path
                
        return full_path

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
