// Make the context module and its contents public
pub mod context;

// Make the cavebot module and its contents public
pub mod cavebot;

// Make the player_monitor module and its contents public
pub mod player_monitor;

// Make the healer module and its contents public
pub mod healer;

// Re-export structs from context for easier access if desired, e.g.:
// pub use context::{GameContext, PlayerStats, BotSettings};
// Or, users can import them directly via crate::game_logic::context::StructName

// Re-export key structs from cavebot for easier access if desired, e.g.:
// pub use cavebot::core::Cavebot;
// pub use cavebot::waypoints::{Waypoint, WaypointType};

// Re-export key structs from player_monitor for easier access if desired, e.g.:
// pub use player_monitor::PlayerMonitor;

// Re-export key structs from healer for easier access if desired, e.g.:
// pub use healer::Healer;
