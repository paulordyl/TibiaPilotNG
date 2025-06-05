import json
from typing import List, Dict, Any, Optional # Added Optional
from src.gameplay.spells import KNOWN_SPELLS # For validation against known spell names

# Predefined lists for option validation
VALID_DIRECTIONS = ["north", "south", "east", "west", "center"]
VALID_TARGET_TYPES = ["self", "current_target", "player_name", "creature_name", "none"]
VALID_REFILL_POTIONS_HEALTH = [
    'Health Potion', 'Strong Health Potion', 'Great Health Potion',
    'Ultimate Health Potion', 'Supreme Health Potion'
    # 'Small Health Potion' is not in refill config, but often a starting potion. Decide if to include.
]
VALID_REFILL_POTIONS_MANA = [
    'Mana Potion', 'Strong Mana Potion', 'Great Mana Potion', 'Ultimate Mana Potion'
]
VALID_REFILL_POTIONS_SPIRIT = [ # Added based on refill config
    'Great Spirit Potion', 'Ultimate Spirit Potion'
]
VALID_BUYBACKPACK_NAMES = ['Orange Backpack', 'Red Backpack', 'Parcel']
VALID_DEPOSIT_CITIES = [
    'AbDendriel', 'Ankrahmun', 'Carlin', 'Darashia', 'Edron', 'Farmine',
    'Issavi', 'Kazoordon', 'LibertBay', 'PortHope', 'Rathleton',
    'Svargrond', 'Thais', 'Venore', 'Yalahar', 'Feyrist', 'Dark Mansion'
]
VALID_TRAVEL_CITIES = [
    'AbDendriel', 'Ankrahmun', 'Carlin', 'Darashia', 'Edron', 'Farmine',
    'Issavi', 'Kazoordon', 'LibertBay', 'PortHope', 'Rathleton',
    'Svargrond', 'Thais', 'Venore', 'Yalahar', 'Tibia', 'Peg Leg', 'shortcut'
]


KNOWN_WAYPOINT_TYPES = [
    "walk", "singleMove", "rightClickDirection", "useRope", "useShovel",
    "rightClickUse", "openDoor", "useLadder", "moveUp", "moveDown",
    "depositGold", "depositItems", "depositItemsHouse", "dropFlasks",
    "travel", "refill", "buyBackpack", "refillChecker",
    "defineSpellSequence", "executeSpellSequence" # Added new types
]

# For defineSpellSequence, 'coordinate', 'ignore', 'passinho' might be optional or not used.
# For executeSpellSequence, 'coordinate' might be context (e.g. player location), 'ignore', 'passinho' likely not used.
# Adjusting REQUIRED_WAYPOINT_KEYS or handling their optionality per type might be needed later.
# For now, keeping them required for simplicity of this step.
REQUIRED_WAYPOINT_KEYS = {"label", "type", "coordinate", "options", "ignore", "passinho"}

def validate_script_content(script_content_str: str) -> List[str]:
    """
    Parses and validates a script string.
    Returns a list of error messages. An empty list means the script is valid.
    """
    errors: List[str] = []
    all_script_labels: List[str] = []
    defined_spell_sequence_labels: set[str] = set() # For spell sequence label validation

    try:
        waypoints = json.loads(script_content_str)
        if not isinstance(waypoints, list):
            errors.append("Script must be a JSON array of waypoint objects.")
            return errors

        # First pass to collect all waypoint labels and defined spell sequence labels
        for wp_idx, wp_obj in enumerate(waypoints):
            if isinstance(wp_obj, dict):
                label = wp_obj.get('label')
                if isinstance(label, str) and label:
                    if label in all_script_labels: # Check for duplicate waypoint labels
                        errors.append(f"Waypoint {wp_idx + 1}: Duplicate waypoint label '{label}' found.")
                    all_script_labels.append(label)

                if wp_obj.get('type') == "defineSpellSequence":
                    options = wp_obj.get('options', {})
                    seq_label = options.get('sequenceLabel')
                    if isinstance(seq_label, str) and seq_label:
                        if seq_label in defined_spell_sequence_labels:
                             errors.append(f"Waypoint {wp_idx + 1} (defineSpellSequence): Duplicate spell sequence label '{seq_label}' defined.")
                        defined_spell_sequence_labels.add(seq_label)
                    elif isinstance(options, dict) and 'sequenceLabel' in options : # only error if key exists but is invalid
                        errors.append(f"Waypoint {wp_idx + 1} (defineSpellSequence): 'options.sequenceLabel' must be a non-empty string.")


    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON format: {e}")
        return errors # Can't proceed if JSON is invalid

    if errors: # Return early if duplicate labels were found in the first pass
        return errors

    for i, waypoint in enumerate(waypoints):
        waypoint_errors = _validate_waypoint_object(i, waypoint, all_script_labels, defined_spell_sequence_labels)
        errors.extend(waypoint_errors)

    return errors

def _validate_waypoint_object(index: int, waypoint: Any, all_script_labels: List[str], defined_spell_sequence_labels: set[str]) -> List[str]:
    """Validates a single waypoint object."""
    errors: List[str] = []
    prefix = f"Waypoint {index + 1}:"

    if not isinstance(waypoint, dict):
        errors.append(f"{prefix} Each waypoint must be a JSON object.")
        return errors

    # Check for missing or extra keys
    waypoint_keys = set(waypoint.keys())
    missing_keys = REQUIRED_WAYPOINT_KEYS - waypoint_keys
    if missing_keys:
        errors.append(f"{prefix} Missing required keys: {', '.join(sorted(list(missing_keys)))}.")

    # Allowing extra keys for now, as per current scripts. If strictness is needed, uncomment:
    # extra_keys = waypoint_keys - REQUIRED_WAYPOINT_KEYS
    # if extra_keys:
    #     errors.append(f"{prefix} Contains unknown keys: {', '.join(sorted(list(extra_keys)))}.")

    # Validate types of required keys
    if 'label' in waypoint and not isinstance(waypoint['label'], str):
        errors.append(f"{prefix} 'label' must be a string.")

    waypoint_type = waypoint.get('type')
    if not isinstance(waypoint_type, str):
        errors.append(f"{prefix} 'type' must be a string.")
    elif waypoint_type not in KNOWN_WAYPOINT_TYPES:
        errors.append(f"{prefix} Unknown waypoint type: '{waypoint_type}'.")

    if 'coordinate' in waypoint:
        coord = waypoint['coordinate']
        if not isinstance(coord, list) or len(coord) != 3 or not all(isinstance(c, int) for c in coord):
            errors.append(f"{prefix} 'coordinate' must be an array of 3 integers (e.g., [x, y, z]).")

    if 'options' in waypoint and not isinstance(waypoint['options'], dict):
        errors.append(f"{prefix} 'options' must be an object/dictionary.")

    if 'ignore' in waypoint and not isinstance(waypoint['ignore'], bool):
        errors.append(f"{prefix} 'ignore' must be a boolean (true/false).")

    if 'passinho' in waypoint and not isinstance(waypoint['passinho'], bool):
        errors.append(f"{prefix} 'passinho' must be a boolean (true/false).")

    # Validate options based on type
    if isinstance(waypoint_type, str) and isinstance(waypoint.get('options'), dict):
        options_errors = _validate_waypoint_options(prefix, waypoint_type, waypoint['options'], all_script_labels, defined_spell_sequence_labels)
        errors.extend(options_errors)

    return errors

def _validate_waypoint_options(prefix: str, waypoint_type: str, options: Dict[str, Any], all_script_labels: List[str], defined_spell_sequence_labels: set[str]) -> List[str]:
    """Validates the 'options' object for a given waypoint type."""
    errors: List[str] = []

    # Type: singleMove, rightClickDirection, moveUp, moveDown
    if waypoint_type in ["singleMove", "rightClickDirection", "moveUp", "moveDown"]:
        if "direction" not in options:
            errors.append(f"{prefix} 'options' for type '{waypoint_type}' must contain 'direction'.")
        elif options["direction"] not in VALID_DIRECTIONS:
            errors.append(f"{prefix} Invalid 'direction' in options: '{options['direction']}'. Must be one of {VALID_DIRECTIONS}.")

    # Type: depositItems, depositItemsHouse (assuming depositItemsHouse can also have city)
    elif waypoint_type == "depositItems" or waypoint_type == "depositItemsHouse":
        if "city" not in options and waypoint_type == "depositItems":
             errors.append(f"{prefix} 'options' for type 'depositItems' must contain 'city'.")
        if "city" in options:
            city_val = options["city"]
            if not isinstance(city_val, str):
                errors.append(f"{prefix} 'options.city' for type '{waypoint_type}' must be a string.")
            elif waypoint_type == "depositItems" and city_val not in VALID_DEPOSIT_CITIES:
                 errors.append(f"{prefix} Invalid 'city' in options: '{city_val}'. Must be one of {VALID_DEPOSIT_CITIES}.")
        # For depositItemsHouse, city is optional. If present, it should be valid.
        elif waypoint_type == "depositItemsHouse" and "city" in options and options["city"] not in VALID_DEPOSIT_CITIES:
             errors.append(f"{prefix} Invalid 'city' in options: '{options['city']}'. Must be one of {VALID_DEPOSIT_CITIES}.")

    # Type: travel
    elif waypoint_type == "travel":
        city_val = options.get("city")
        if city_val is None: # Ensure key exists
            errors.append(f"{prefix} 'options' for type 'travel' must contain 'city'.")
        elif not isinstance(city_val, str):
            errors.append(f"{prefix} 'options.city' for type 'travel' must be a string.")
        elif city_val not in VALID_TRAVEL_CITIES:
            errors.append(f"{prefix} Invalid 'city' in options: '{city_val}'. Must be one of {VALID_TRAVEL_CITIES}.")

    # Type: refill
    elif waypoint_type == "refill":
        expected_potion_keys = {"item", "quantity"}

        if 'healthPotionEnabled' not in options or not isinstance(options['healthPotionEnabled'], bool):
            errors.append(f"{prefix} 'options.healthPotionEnabled' is required and must be a boolean.")
        if 'houseNpcEnabled' not in options or not isinstance(options['houseNpcEnabled'], bool):
            errors.append(f"{prefix} 'options.houseNpcEnabled' is required and must be a boolean.")

        if 'healthPotion' not in options or not isinstance(options['healthPotion'], dict):
            errors.append(f"{prefix} 'options.healthPotion' is required and must be an object.")
        else:
            hp_potion = options['healthPotion']
            missing_hp_keys = expected_potion_keys - set(hp_potion.keys())
            if missing_hp_keys:
                errors.append(f"{prefix} 'options.healthPotion' missing keys: {', '.join(missing_hp_keys)}.")
            if 'item' in hp_potion and (not isinstance(hp_potion['item'], str) or hp_potion['item'] not in VALID_REFILL_POTIONS_HEALTH + VALID_REFILL_POTIONS_SPIRIT): # Allow spirit potions too
                errors.append(f"{prefix} Invalid 'item' in 'options.healthPotion': '{hp_potion['item']}'. Must be one of {VALID_REFILL_POTIONS_HEALTH + VALID_REFILL_POTIONS_SPIRIT}.")
            if 'quantity' in hp_potion and not isinstance(hp_potion['quantity'], int):
                 errors.append(f"{prefix} 'options.healthPotion.quantity' must be an integer.")

        if 'manaPotion' not in options or not isinstance(options['manaPotion'], dict):
            errors.append(f"{prefix} 'options.manaPotion' is required and must be an object.")
        else:
            mp_potion = options['manaPotion']
            missing_mp_keys = expected_potion_keys - set(mp_potion.keys())
            if missing_mp_keys:
                errors.append(f"{prefix} 'options.manaPotion' missing keys: {', '.join(missing_mp_keys)}.")
            if 'item' in mp_potion and (not isinstance(mp_potion['item'], str) or mp_potion['item'] not in VALID_REFILL_POTIONS_MANA + VALID_REFILL_POTIONS_SPIRIT): # Allow spirit potions too
                errors.append(f"{prefix} Invalid 'item' in 'options.manaPotion': '{mp_potion['item']}'. Must be one of {VALID_REFILL_POTIONS_MANA + VALID_REFILL_POTIONS_SPIRIT}.")
            if 'quantity' in mp_potion and not isinstance(mp_potion['quantity'], int):
                errors.append(f"{prefix} 'options.manaPotion.quantity' must be an integer.")

    # Type: buyBackpack
    elif waypoint_type == "buyBackpack":
        bp_name = options.get('name')
        bp_amount = options.get('amount')
        if not isinstance(bp_name, str) or not isinstance(bp_amount, int):
            errors.append(f"{prefix} 'options' for type 'buyBackpack' must have 'name' (string) and 'amount' (integer).")
        elif bp_name not in VALID_BUYBACKPACK_NAMES:
            errors.append(f"{prefix} Invalid 'name' in options for 'buyBackpack': '{bp_name}'. Must be one of {VALID_BUYBACKPACK_NAMES}.")

    # Type: refillChecker
    elif waypoint_type == "refillChecker":
        expected_keys = {"minimumAmountOfHealthPotions", "minimumAmountOfManaPotions", "minimumAmountOfCap", "waypointLabelToRedirect", "healthEnabled"} # Added healthEnabled
        current_keys = set(options.keys())
        missing_keys = expected_keys - current_keys
        if missing_keys:
            errors.append(f"{prefix} 'options' for type 'refillChecker' missing keys: {', '.join(sorted(list(missing_keys)))}.")

        extra_keys = current_keys - expected_keys
        if extra_keys: # Also check for unexpected keys
            errors.append(f"{prefix} 'options' for type 'refillChecker' has unexpected keys: {', '.join(sorted(list(extra_keys)))}.")

        for key in ["minimumAmountOfHealthPotions", "minimumAmountOfManaPotions", "minimumAmountOfCap"]:
            if key in options and not isinstance(options[key], int):
                errors.append(f"{prefix} 'options.{key}' must be an integer. Found: {options[key]}")

        label_to_check = options.get('waypointLabelToRedirect')
        if 'waypointLabelToRedirect' in options: # Only validate if key exists
            if not isinstance(label_to_check, str) or not label_to_check: # Ensure non-empty string
                errors.append(f"{prefix} 'options.waypointLabelToRedirect' must be a non-empty string.")
            elif label_to_check not in all_script_labels:
                 errors.append(f"{prefix} 'options.waypointLabelToRedirect' ('{label_to_check}') does not match any waypoint label in the script.")

        if 'healthEnabled' in options and not isinstance(options['healthEnabled'], bool): # Key name was 'healthEnabled'
            errors.append(f"{prefix} 'options.healthEnabled' must be a boolean.")

    # Types with empty options: "walk", "useRope", "useShovel", "rightClickUse", "openDoor", "useLadder", "depositGold", "dropFlasks"
    # These types should have an empty options dict.
    elif waypoint_type in ["walk", "useRope", "useShovel", "rightClickUse", "openDoor", "useLadder", "depositGold", "dropFlasks"]:
        if options: # If options dictionary is not empty
            errors.append(f"{prefix} 'options' for type '{waypoint_type}' must be empty. Found: {options}")

    elif waypoint_type == "defineSpellSequence":
        if not isinstance(options.get('sequenceLabel'), str) or not options.get('sequenceLabel'):
            errors.append(f"{prefix} 'options.sequenceLabel' is required and must be a non-empty string for defineSpellSequence.")

        spells_list = options.get('spells')
        if not isinstance(spells_list, list):
            errors.append(f"{prefix} 'options.spells' is required and must be a list for defineSpellSequence.")
        else:
            for i, spell_action_dict in enumerate(spells_list):
                action_prefix = f"{prefix} options.spells[{i}]:"
                if not isinstance(spell_action_dict, dict):
                    errors.append(f"{action_prefix} Each spell action must be an object.")
                    continue # Skip further checks for this malformed action

                required_action_keys = {"name", "words", "target_type", "delay_ms"}
                current_action_keys = set(spell_action_dict.keys())
                missing_action_keys = required_action_keys - current_action_keys
                if missing_action_keys:
                    errors.append(f"{action_prefix} Missing required keys: {', '.join(sorted(list(missing_action_keys)))}.")

                spell_name = spell_action_dict.get('name')
                if not isinstance(spell_name, str) or not spell_name:
                    errors.append(f"{action_prefix} 'name' must be a non-empty string.")
                elif spell_name not in KNOWN_SPELLS:
                    errors.append(f"{action_prefix} 'name' ('{spell_name}') is not a recognized spell in KNOWN_SPELLS.")

                # Optionally, verify words match KNOWN_SPELLS - can be strict
                # spell_words = spell_action_dict.get('words')
                # if isinstance(spell_name, str) and spell_name in KNOWN_SPELLS and isinstance(spell_words, str):
                #     if KNOWN_SPELLS[spell_name]['words'] != spell_words:
                #         errors.append(f"{action_prefix} 'words' ('{spell_words}') do not match known words ('{KNOWN_SPELLS[spell_name]['words']}') for spell '{spell_name}'.")
                elif not isinstance(spell_action_dict.get('words'), str):
                     errors.append(f"{action_prefix} 'words' must be a string.")


                target_type = spell_action_dict.get('target_type')
                if not isinstance(target_type, str) or target_type not in VALID_TARGET_TYPES:
                    errors.append(f"{action_prefix} 'target_type' ('{target_type}') is invalid. Must be one of {VALID_TARGET_TYPES}.")

                target_value = spell_action_dict.get('target_value') # Can be None or missing
                if target_type in ["player_name", "creature_name"]:
                    if not isinstance(target_value, str) or not target_value:
                        errors.append(f"{action_prefix} 'target_value' must be a non-empty string when target_type is '{target_type}'.")
                elif target_value is not None and not isinstance(target_value, str): # if present, must be string
                     errors.append(f"{action_prefix} 'target_value' must be a string if provided.")


                delay_ms = spell_action_dict.get('delay_ms')
                if not isinstance(delay_ms, int) or delay_ms < 0:
                    errors.append(f"{action_prefix} 'delay_ms' must be a non-negative integer. Found: {delay_ms}")

                mana_cost = spell_action_dict.get('mana_cost') # Optional
                if mana_cost is not None and not isinstance(mana_cost, int):
                    errors.append(f"{action_prefix} 'mana_cost' must be an integer if provided. Found: {mana_cost}")

    elif waypoint_type == "executeSpellSequence":
        seq_label = options.get('sequenceLabel')
        if not isinstance(seq_label, str) or not seq_label:
            errors.append(f"{prefix} 'options.sequenceLabel' is required and must be a non-empty string for executeSpellSequence.")
        elif seq_label not in defined_spell_sequence_labels:
            errors.append(f"{prefix} 'options.sequenceLabel' ('{seq_label}') does not match any defined spell sequence label.")

    return errors

if __name__ == '__main__':
    # Example Usage and Test Cases
    valid_script_str = """
    [
        {
            "label": "Start",
            "type": "walk",
            "coordinate": [100, 200, 7],
            "options": {},
            "ignore": false,
            "passinho": false
        },
        {
            "label": "Move West",
            "type": "singleMove",
            "coordinate": [99, 200, 7],
            "options": {"direction": "west"},
            "ignore": false,
            "passinho": false
        }
    ]
    """
    errors = validate_script_content(valid_script_str)
    print("Valid script errors:", errors) # Expected: []

    invalid_script_str_json = "this is not json"
    errors = validate_script_content(invalid_script_str_json)
    print("Invalid JSON errors:", errors) # Expected: ["Invalid JSON format: ..."]

    invalid_script_str_structure = """
    {
        "label": "Bad structure"
    }
    """
    errors = validate_script_content(invalid_script_str_structure)
    print("Invalid structure errors:", errors) # Expected: ["Script must be a JSON array..."]

    invalid_script_str_waypoint = """
    [
        {
            "label": "Missing type",
            "coordinate": [1,2,3],
            "options": {},
            "ignore": false,
            "passinho": false
        },
        {
            "label": "Unknown type",
            "type": "fly",
            "coordinate": [1,2,3],
            "options": {},
            "ignore": false,
            "passinho": false
        },
        {
            "label": "Bad coordinate",
            "type": "walk",
            "coordinate": [1,2],
            "options": {},
            "ignore": "false",
            "passinho": false
        },
        {
            "label": "Bad singleMove options",
            "type": "singleMove",
            "coordinate": [1,2,3],
            "options": {"dir": "north"},
            "ignore": false,
            "passinho": false
        }
    ]
    """
    errors = validate_script_content(invalid_script_str_waypoint)
    print("Invalid waypoint errors:", errors)
    # Expected: Multiple errors for missing keys, unknown type, bad coordinate type/length, bad options etc.
