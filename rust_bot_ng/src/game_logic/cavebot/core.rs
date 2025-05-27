use crate::game_logic::{
    cavebot::waypoints::{Waypoint, WaypointType}, // Corrected path
    context::GameContext, // Corrected path
};
use log::{debug, info, warn}; // Added warn
use std::{sync::Arc, thread, time::Duration};

// Placeholder for all dependencies the Cavebot might need to execute actions.
// This will be fleshed out as other modules (input, screen interaction, etc.) are integrated.
use crate::{
    input::{self, arduino::ArduinoCom},
    image_processing::{cache::DetectionCache, templates::TemplateManager}, // Added TemplateManager and DetectionCache
};
use std::sync::{Arc, Mutex}; // Added Mutex

pub struct AllDependencies {
    pub arduino_com: Arc<Mutex<ArduinoCom>>,
    pub template_manager: Arc<TemplateManager>,
    pub detection_cache: Arc<DetectionCache>,
    // pub screen_handler: Option<Arc<ScreenHandler>>, // Example: Screen interaction (capture, find)
}

impl AllDependencies {
    // Constructor that takes the necessary dependencies
    pub fn new(
        arduino_com: Arc<Mutex<ArduinoCom>>,
        template_manager: Arc<TemplateManager>,
        detection_cache: Arc<DetectionCache>,
    ) -> Self {
        Self {
            arduino_com,
            template_manager,
            detection_cache,
        }
    }
}
// Default cannot be easily derived anymore unless we provide a dummy ArduinoCom,
// which might be complex. For now, new() is the way. Consider a Default impl if
// a default ArduinoCom (e.g., a mock or no-op version) becomes feasible.


pub struct Cavebot {
    waypoints: Vec<Waypoint>,
    pub current_waypoint_index: usize, // Made public for main.rs example, or add getter
    game_context: Arc<GameContext>, // To access shared state like is_running
}

impl Cavebot {
    pub fn new(game_context: Arc<GameContext>) -> Self {
        debug!("Initializing new Cavebot instance.");
        Cavebot {
            waypoints: Vec::new(),
            current_waypoint_index: 0,
            game_context,
        }
    }
    
    // Method to get current waypoints count, useful for main.rs example
    pub fn waypoints_count(&self) -> usize {
        self.waypoints.len()
    }


    pub fn add_waypoint(&mut self, waypoint: Waypoint) {
        debug!("Adding waypoint: label='{}', type='{:?}'", waypoint.label, waypoint.waypoint_type);
        self.waypoints.push(waypoint);
    }

    pub fn set_waypoints(&mut self, waypoints: Vec<Waypoint>) {
        debug!("Setting {} waypoints. Old count: {}", waypoints.len(), self.waypoints.len());
        self.waypoints = waypoints;
        self.current_waypoint_index = 0; // Reset index when new waypoints are set
    }

    pub fn run_main_loop(&mut self, deps: &AllDependencies) { // deps is now used
        info!("Cavebot main loop started.");
        while self.game_context.check_is_running() {
            if self.waypoints.is_empty() {
                warn!("Cavebot loop is running but has no waypoints. Add waypoints to proceed.");
                thread::sleep(Duration::from_secs(5)); // Sleep longer if no waypoints
                continue;
            }

            if self.current_waypoint_index >= self.waypoints.len() {
                info!("Reached end of waypoint list. Looping back to start.");
                self.current_waypoint_index = 0; // Loop back
            }

            let waypoint = &self.waypoints[self.current_waypoint_index];

            info!(
                "Processing Waypoint: '{}' - Type: {:?} at ({}, {}, {}). Index: {}",
                waypoint.label,
                waypoint.waypoint_type,
                waypoint.coordinate.0,
                waypoint.coordinate.1,
                waypoint.coordinate.2,
                self.current_waypoint_index
            );

            // TODO: Implement actual task execution based on waypoint.waypoint_type
            // This will involve calling functions from other modules (input, image_processing, etc.)
            // and passing relevant parts of `deps`.
            
            // Create and execute task based on waypoint type
            let task_result = match waypoint.waypoint_type {
                WaypointType::Walk => {
                    let task = tasks::CavebotTask::Walk { coordinate: waypoint.coordinate };
                    task.execute(deps)
                }
                WaypointType::OpenDoor => {
                    // For now, use a hardcoded template name. This could come from waypoint.metadata later.
                    let task = tasks::CavebotTask::OpenDoor {
                        coordinate: waypoint.coordinate,
                        door_template_name: "default_door_template".to_string(),
                    };
                    task.execute(deps)
                }
                // Add other WaypointType cases here
                _ => {
                    warn!("Task execution for waypoint type '{:?}' not implemented yet.", waypoint.waypoint_type);
                    Ok(()) // Or perhaps Err(AppError::NotImplemented) if that's more appropriate
                }
            };

            if let Err(e) = task_result {
                error!("Error executing task for waypoint '{}' (type: {:?}): {}", waypoint.label, waypoint.waypoint_type, e);
                // Decide on error strategy: stop cavebot, skip waypoint, retry, etc.
                // For now, just log and continue to the next waypoint.
            }

            self.current_waypoint_index += 1;

            // Simulate work and prevent tight loop
            thread::sleep(Duration::from_secs(1));
        }
        info!("Cavebot main loop stopped because is_running is false.");
    }
}
