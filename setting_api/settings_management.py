import json
import os

# Path to the settings file
SETTINGS_FILE_PATH = "application_settings.json"

def create_preference_file_if_not_exists():
    """Create the settings file if it doesn't exist"""
    if not is_preference_file_exists():
        with open(SETTINGS_FILE_PATH, 'w') as f:
            json.dump({}, f)
        return True
    return False

def is_preference_file_exists():
    """Check if the settings file exists"""
    return os.path.exists(SETTINGS_FILE_PATH)

def add_setting(key, value):
    """Add a new setting"""
    create_preference_file_if_not_exists()
    with open(SETTINGS_FILE_PATH, 'r') as f:
        settings = json.load(f)
    
    settings[key] = value
    
    with open(SETTINGS_FILE_PATH, 'w') as f:
        json.dump(settings, f, indent=4)
    
    return True

def get_setting(key):
    """Get a setting by key"""
    create_preference_file_if_not_exists()
    with open(SETTINGS_FILE_PATH, 'r') as f:
        settings = json.load(f)
    
    return settings.get(key)

def remove_setting(key):
    """Remove a setting by key"""
    create_preference_file_if_not_exists()
    with open(SETTINGS_FILE_PATH, 'r') as f:
        settings = json.load(f)
    
    if key in settings:
        del settings[key]
        
        with open(SETTINGS_FILE_PATH, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    
    return False

def update_setting(key, value):
    """Update an existing setting"""
    create_preference_file_if_not_exists()
    with open(SETTINGS_FILE_PATH, 'r') as f:
        settings = json.load(f)
    
    if key in settings:
        settings[key] = value
        
        with open(SETTINGS_FILE_PATH, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    
    return False

def add_or_update_setting(key, value):
    """Add a new setting or update existing one"""
    create_preference_file_if_not_exists()
    with open(SETTINGS_FILE_PATH, 'r') as f:
        settings = json.load(f)
    
    settings[key] = value
    
    with open(SETTINGS_FILE_PATH, 'w') as f:
        json.dump(settings, f, indent=4)
    
    return True

def is_settings_exists(key):
    """Check if a setting exists"""
    create_preference_file_if_not_exists()
    with open(SETTINGS_FILE_PATH, 'r') as f:
        settings = json.load(f)
    
    return key in settings

def get_all_settings():
    """Get all settings"""
    create_preference_file_if_not_exists()
    with open(SETTINGS_FILE_PATH, 'r') as f:
        settings = json.load(f)
    
    return settings

def clean_all_settings_():
    """Remove all settings"""
    with open(SETTINGS_FILE_PATH, 'w') as f:
        json.dump({}, f)
    return True

def is_settings_api_undefined():
    """Check if settings API is undefined (file doesn't exist or empty)"""
    return not is_preference_file_exists() or os.path.getsize(SETTINGS_FILE_PATH) == 0