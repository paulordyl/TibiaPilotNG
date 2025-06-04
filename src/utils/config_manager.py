import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

USER_CONFIG_PATH = 'config.json'
DEFAULT_CONFIG_PATH = 'config.default.json'

config_data = {}

def get_initial_defaults():
    """Returns the initial in-memory default configuration."""
    return {
        "profile_file_path": "file.json",
        "backpacks": [
            "25 Years Backpack", "Anniversary Backpack", "Beach Backpack", "Birthday Backpack",
            "Brocade Backpack", "Buggy Backpack", "Cake Backpack", "Camouflage Backpack",
            "Crown Backpack", "Crystal Backpack", "Deepling Backpack", "Demon Backpack",
            "Dragon Backpack", "Expedition Backpack", "Fur Backpack", "Glooth Backpack",
            "Heart Backpack", "Minotaur Backpack", "Moon Backpack", "Mushroom Backpack",
            "Pannier Backpack", "Pirate Backpack", "Raccoon Backpack", "Santa Backpack",
            "Wolf Backpack"
        ],
        "npc_keywords": {
            "hi": "hi",
            "potions": "potions",
            "trade": "trade",
            "yes": "yes",
            "no": "no"
        },
        "combat_thresholds": {
            "no_monster_stop_attack_threshold": 70
        },
        "keyboard_delays": {
            "write_interval_min": 0.03,
            "write_interval_max": 0.12,
            "default_random_min": 0.2,
            "default_random_max": 0.5,
            "say_task_min": 0.3,
            "say_task_max": 0.6
        },
        "refill_delays": {
            "before_start": 1.0,
            "after_complete": 1.0,
            "use_hotkey_min": 0.8,
            "use_hotkey_max": 1.2
        },
        "hotkeys": {
            "eat_food": "f",
            "shovel": "p",
            "rope": "o",
            "auto_hur": "t",
            "clear_poison": "g",
            "esc_target": "esc",
            "hp_food": "3",
            "mp_food": "4",
            "tank_ring": "f11",
            "main_ring": "f12",
            "tank_amulet": "u",
            "main_amulet": "i",
            "hp_potion": "1",
            "mp_potion": "2",
            "critical_healing_spell": "5",
            "light_healing_spell": "7",
            "utura_spell": "8",
            "utura_gran_spell": "9"
        },
        "game_window": {
            "resolution_height": 1080
        },
        "pathfinding": {
            "radar_x_offset": 53,
            "radar_y_offset_start": 54,
            "radar_y_offset_end": 55,
            "astar_diagonal_cost": 0,
            "move_action_offset": 2
        },
        "ui_defaults": {
            "combo_spell_name": "Default",
            "combo_spell_creature_compare": "lessThan",
            "combo_spell_creature_value": 5,
            "waypoint_direction": "center",
            "combo_spell_current_index_reset_on_load": True
        },
        "chat_tabs": {
            "local_chat": "local chat"
        },
        "slots": {
            "tank_ring": 21,
            "main_ring": 22,
            "tank_amulet": 23,
            "main_amulet": 24,
            "hp_potion": 1,
            "mp_potion": 2
        }
    }

def load_config():
    """
    Loads configuration from user_config.json, then config.default.json,
    or finally uses in-memory defaults.
    """
    global config_data
    loaded_from = None

    if os.path.exists(USER_CONFIG_PATH):
        try:
            with open(USER_CONFIG_PATH, 'r') as f:
                config_data = json.load(f)
            loaded_from = USER_CONFIG_PATH
            logging.info(f"Configuration loaded from {USER_CONFIG_PATH}")
        except Exception as e:
            logging.error(f"Error loading {USER_CONFIG_PATH}: {e}. Falling back.")
            config_data = {} # Reset if user config is corrupt

    if not config_data and os.path.exists(DEFAULT_CONFIG_PATH):
        try:
            with open(DEFAULT_CONFIG_PATH, 'r') as f:
                config_data = json.load(f)
            loaded_from = DEFAULT_CONFIG_PATH
            logging.info(f"Configuration loaded from {DEFAULT_CONFIG_PATH}")
        except Exception as e:
            logging.error(f"Error loading {DEFAULT_CONFIG_PATH}: {e}. Falling back.")
            config_data = {} # Reset if default config is corrupt

    if not config_data:
        config_data = get_initial_defaults()
        loaded_from = "in-memory defaults"
        logging.info(f"No configuration file found. Loaded in-memory default configuration.")

    # Ensure all top-level keys from initial defaults are present if loading from file
    # This helps prevent KeyError if a new config key is added to defaults but missing in user file
    if loaded_from != "in-memory defaults":
        initial_defaults = get_initial_defaults()
        for key, value in initial_defaults.items():
            if key not in config_data:
                logging.warning(f"Key '{key}' not found in loaded config, adding from initial defaults.")
                config_data[key] = value
            # Could also do a deep merge here if necessary for nested dicts
            elif isinstance(value, dict) and isinstance(config_data.get(key), dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in config_data[key]:
                        logging.warning(f"Sub-key '{key}.{sub_key}' not found in loaded config, adding from initial defaults.")
                        config_data[key][sub_key] = sub_value


def get_config(key_path: str, default_value=None):
    """
    Retrieves a configuration value using a dot-separated key path.
    Example: get_config('keyboard_delays.write_interval_min')
    """
    keys = key_path.split('.')
    value = config_data
    try:
        for key in keys:
            value = value[key]
        return value
    except KeyError:
        logging.warning(f"Configuration key '{key_path}' not found. Returning default value: {default_value}")
        return default_value
    except TypeError: # Handles cases where an intermediate key is not a dict
        logging.warning(f"Configuration path '{key_path}' is invalid (intermediate key not a dictionary). Returning default value: {default_value}")
        return default_value

# Load configuration when the module is imported
load_config()

def save_config(data_to_save: dict) -> bool:
    """
    Saves the provided configuration data to USER_CONFIG_PATH (config.json).
    Updates the in-memory config_data upon successful save.
    Returns True on success, False on failure.
    """
    global config_data
    try:
        with open(USER_CONFIG_PATH, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        logging.info(f"Configuration successfully saved to {USER_CONFIG_PATH}")
        config_data = data_to_save  # Update in-memory config
        return True
    except Exception as e:
        logging.error(f"Error saving configuration to {USER_CONFIG_PATH}: {e}")
        return False

if __name__ == '__main__':
    # Example usage:
    print(f"Profile file path: {get_config('profile_file_path')}")
    print(f"Backpacks: {get_config('backpacks')}")
    print(f"NPC 'hi' keyword: {get_config('npc_keywords.hi')}")
    print(f"Stop attack threshold: {get_config('combat_thresholds.no_monster_stop_attack_threshold')}")
    print(f"Min write interval: {get_config('keyboard_delays.write_interval_min')}")
    print(f"A non-existent key: {get_config('a.b.c', 'default_for_non_existent')}")

    # Test saving a user config (optional, for testing the load order)
    # test_user_config = {"profile_file_path": "my_custom_file.json", "new_setting": "my_value"}
    # with open(USER_CONFIG_PATH, 'w') as f:
    #     json.dump(test_user_config, f, indent=4)
    # print(f"\nSaved a test {USER_CONFIG_PATH}. Please re-run to see it load.")

    # Test default config load (optional, for testing the load order)
    # if os.path.exists(USER_CONFIG_PATH):
    #     os.remove(USER_CONFIG_PATH) # Remove user to test default
    # test_default_config = {"profile_file_path": "default_profile.json", "only_in_default": True}
    # with open(DEFAULT_CONFIG_PATH, 'w') as f:
    #     json.dump(test_default_config, f, indent=4)
    # print(f"\nSaved a test {DEFAULT_CONFIG_PATH} (and removed user config if it existed). Please re-run.")

    # Test in-memory load (optional)
    # if os.path.exists(USER_CONFIG_PATH):
    #     os.remove(USER_CONFIG_PATH)
    # if os.path.exists(DEFAULT_CONFIG_PATH):
    #     os.remove(DEFAULT_CONFIG_PATH)
    # print(f"\nRemoved config files if they existed. Please re-run to test in-memory defaults.")
