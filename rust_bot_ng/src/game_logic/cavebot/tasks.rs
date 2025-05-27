use crate::{
    game_logic::cavebot::core::AllDependencies, // For access to ArduinoCom, etc.
    input, // For input::mouse module
    AppError,
};
use log::{debug, info, error}; // Added error

use crate::image_processing; // Added for matching::find_template_on_screen

#[derive(Debug)] // For logging the task
pub enum CavebotTask {
    Walk { coordinate: (i32, i32, i32) },
    OpenDoor { coordinate: (i32, i32, i32), door_template_name: String },
    // TODO: Add other tasks like UseItem, TargetMonster, Say, etc.
}

impl CavebotTask {
    pub fn execute(&self, deps: &AllDependencies) -> Result<(), AppError> {
        match self {
            CavebotTask::Walk { coordinate } => {
                info!("Executing WalkTask to ({}, {}, {})", coordinate.0, coordinate.1, coordinate.2);
                match deps.arduino_com.lock() {
                    Ok(mut arduino_guard) => {
                        input::mouse::move_to(&mut *arduino_guard, (coordinate.0, coordinate.1))?;
                        debug!("WalkTask: mouse::move_to called successfully.");
                        Ok(())
                    }
                    Err(poisoned_error) => {
                        error!("Failed to acquire lock on ArduinoCom for WalkTask: Mutex is poisoned. {}", poisoned_error);
                        Err(AppError::InputError(format!(
                            "Failed to acquire lock on ArduinoCom for WalkTask: Mutex is poisoned. {}",
                            poisoned_error
                        )))
                    }
                }
            }
            CavebotTask::OpenDoor { coordinate, door_template_name } => {
                info!(
                    "Executing OpenDoorTask near ({},{},{}) using template '{}'",
                    coordinate.0, coordinate.1, coordinate.2, door_template_name
                );

                // Define a search region (e.g., 100x100 box centered on coordinate.0, coordinate.1)
                // Game world Z coordinate (coordinate.2) is not used for screen region definition.
                let search_width: u32 = 100;
                let search_height: u32 = 100;
                let region_x = coordinate.0 - (search_width / 2) as i32;
                let region_y = coordinate.1 - (search_height / 2) as i32;
                let screen_capture_region = (region_x, region_y, search_width, search_height);
                let confidence_threshold = 0.8;

                match image_processing::matching::find_template_on_screen(
                    door_template_name,
                    &deps.template_manager,
                    &deps.detection_cache,
                    screen_capture_region,
                    confidence_threshold,
                    false, // use_cache = false for doors
                ) {
                    Ok(Some(location)) => {
                        info!(
                            "Door template '{}' found at screen coordinates: ({}, {}), size: ({}, {})",
                            door_template_name, location.0, location.1, location.2, location.3
                        );
                        match deps.arduino_com.lock() {
                            Ok(mut arduino_guard) => {
                                input::mouse::right_click(
                                    &mut *arduino_guard,
                                    Some((location.0 + location.2 as i32 / 2, location.1 + location.3 as i32 / 2)),
                                )?;
                                info!("Right-clicked center of found door template.");
                            }
                            Err(poisoned_error) => {
                                error!("Failed to acquire lock on ArduinoCom for OpenDoorTask: Mutex is poisoned. {}", poisoned_error);
                                return Err(AppError::InputError(format!(
                                    "Failed to acquire lock on ArduinoCom for OpenDoorTask: Mutex is poisoned. {}",
                                    poisoned_error
                                )));
                            }
                        }
                    }
                    Ok(None) => {
                        info!(
                            "Door template '{}' not found near ({},{},{}) with confidence >= {}.",
                            door_template_name, coordinate.0, coordinate.1, coordinate.2, confidence_threshold
                        );
                        // This might not be an error for the whole task, depends on desired behavior.
                        // For now, just log and return Ok.
                    }
                    Err(e) => {
                        error!(
                            "Error during find_template_on_screen for door '{}': {}",
                            door_template_name, e
                        );
                        return Err(e); // Propagate the error
                    }
                }
                Ok(())
            } // TODO: Implement execute for other task variants here
        }
    }
}
