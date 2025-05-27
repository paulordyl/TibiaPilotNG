use log::debug; // For logging initialization

#[derive(Debug, Clone, PartialEq, Eq, Hash)] // Added PartialEq, Eq, Hash for potential use in HashMaps or for comparison
pub enum WaypointType {
    Walk,       // Navigate to a coordinate
    Use,        // Use an item or object at/near a coordinate (e.g., ladder, rope hole)
    Pick,       // Pick up loot (though loot coordinates might be dynamic)
    OpenDoor,   // Interact with a door
    Refill,     // Trigger a refilling sequence (potions, arrows)
    Approach,   // Approach a creature or specific point
    Target,     // Select a target (monster)
    Wait,       // Pause execution for a specified duration
    Say,        // Say something in chat (e.g. for spells or interacting with NPCs)
    Script,     // Execute a sub-script or a sequence of actions
    Logout,     // Log out of the game
    // TODO: Add other types as identified from Python's waypoint.py or taskList, e.g., Attack, SpecialAttack, DropLoot
}

#[derive(Debug, Clone)]
pub struct Waypoint {
    pub label: String,
    pub waypoint_type: WaypointType,
    pub coordinate: (i32, i32, i32), // (x, y, z) representing game coordinates
    // TODO: Add other potential fields like metadata/options for specific types.
    // For example:
    // pub item_id: Option<u32>, // For Use, Pick, DropLoot
    // pub target_name: Option<String>, // For Target, Approach
    // pub duration_ms: Option<u64>, // For Wait
    // pub message: Option<String>, // For Say
    // pub script_name: Option<String>, // For Script
}

impl Waypoint {
    pub fn new(label: String, waypoint_type: WaypointType, coordinate: (i32, i32, i32)) -> Self {
        debug!(
            "Creating new Waypoint: label='{}', type='{:?}', coord=({},{},{})",
            label, waypoint_type, coordinate.0, coordinate.1, coordinate.2
        );
        Waypoint {
            label,
            waypoint_type,
            coordinate,
            // Initialize other fields to None or default values here
        }
    }
}
