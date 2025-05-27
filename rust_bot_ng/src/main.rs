use std::fmt;
use env_logger::Env;
use log::{error, info, warn, debug}; // Added debug log level

// Module declarations
pub mod input; // Assuming input module is already present or planned
pub mod screen_capture;
pub mod image_processing;
pub mod game_logic;
// pub mod config;     // Example for future module
// pub mod utils;      // Example for future module


// Custom Error type
#[derive(Debug)]
enum AppError {
    InputError(String),
    ScreenCaptureError(String),
    ImageProcessingError(String),
    GameLogicError(String),
    ConfigError(String),
    IOError(std::io::Error),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            AppError::InputError(s) => write!(f, "Input Error: {}", s),
            AppError::ScreenCaptureError(s) => write!(f, "Screen Capture Error: {}", s),
            AppError::ImageProcessingError(s) => write!(f, "Image Processing Error: {}", s),
            AppError::GameLogicError(s) => write!(f, "Game Logic Error: {}", s),
            AppError::ConfigError(s) => write!(f, "Config Error: {}", s),
            AppError::IOError(e) => write!(f, "IO Error: {}", e),
        }
    }
}

impl std::error::Error for AppError {}

// Convert std::io::Error to AppError
impl From<std::io::Error> for AppError {
    fn from(err: std::io::Error) -> AppError {
        AppError::IOError(err)
    }
}

fn main() -> Result<(), AppError> {
    // Initialize logger
    env_logger::Builder::from_env(Env::default().default_filter_or("info")).init();

    info!("Starting application");

    // Load configuration
    let config = match config::settings::load_config("rust_bot_ng/config.toml") {
        Ok(cfg) => {
            info!("Configuration loaded successfully from rust_bot_ng/config.toml");
            info!("Character Name: {}", cfg.general.character_name);
            cfg
        }
        Err(e) => {
            error!("Failed to load configuration: {}", e);
            // Depending on the severity, you might want to exit or use default values.
            // For this example, we'll exit if config fails to load.
            return Err(e);
        }
    };

    // Initialize input module (Arduino communication, input simulation)
    // Use Arduino port and baud rate from config
    let arduino_com_instance = match input::arduino::ArduinoCom::new(&config.arduino.port, config.arduino.baud_rate) {
        Ok(ac) => {
            info!("ArduinoCom initialized successfully on port {} with baud rate {}.", config.arduino.port, config.arduino.baud_rate);
            Arc::new(Mutex::new(ac))
        }
        Err(e) => {
            error!("Failed to initialize ArduinoCom on port {}: {}. Exiting.", config.arduino.port, e);
            return Err(e); 
        }
    };

    // TODO: Initialize screen capture module
    // Example:
    // use crate::screen_capture::capture;
    // let screen_image = capture::capture_primary_screen()?;

    // TODO: Initialize image processing module
    // Example:
    // use crate::image_processing::{matching, templates::TemplateManager, cache::DetectionCache}; // Updated use statement
    // use image::io::Reader as ImageReader; // For loading a needle image
    
    // Initialize TemplateManager and load templates
    // let mut template_manager = TemplateManager::new();
    // template_manager.load_templates_from_directory("rust_bot_ng/templates")?; // Or relevant path
    // info!("Templates loaded.");

    // Initialize DetectionCache
    // let detection_cache = DetectionCache::new();
    // info!("Detection cache initialized.");

    // Example usage of find_template_on_screen (assuming screen_image is captured elsewhere or not needed for this specific example)
    // let game_window_region = (0, 0, 1920, 1080); // TODO: This should be dynamically determined
    // let confidence = 0.9;

    // Example with use_cache: true
    // if let Some((x,y,w,h)) = matching::find_template_on_screen("some_template_name", &template_manager, &detection_cache, game_window_region, confidence, true)? {
    //     info!("Found 'some_template_name' (cached or fresh) at screen coordinates: ({}, {}), size: ({}, {})", x, y, w, h);
    //     // mouse::move_to(&mut arduino_com, (x + w/2, y + h/2))?;
    //     // mouse::left_click(&mut arduino_com, None)?;
    // } else {
    //     info!("'some_template_name' not found on screen (with cache).");
    // }

    // Example with use_cache: false (forces a fresh search and updates cache)
    // if let Some((x,y,w,h)) = matching::find_template_on_screen("another_template", &template_manager, &detection_cache, game_window_region, confidence, false)? {
    //     info!("Found 'another_template' (fresh search) at screen coordinates: ({}, {}), size: ({}, {})", x, y, w, h);
    // } else {
    //     info!("'another_template' not found on screen (fresh search).");
    // }


    // TODO: Initialize game logic module
    // Example:
    // Declare modules used (adjust as per actual file structure and imports)
    use crate::config; // Already imported for load_config
    use crate::game_logic::{
        context::{GameContext, BotSettings}, // BotSettings for initialization
        cavebot::{core::Cavebot, waypoints::{Waypoint, WaypointType}, core::AllDependencies as CavebotDeps},
        player_monitor::PlayerMonitor,
        healer::Healer,
    };
    use crate::input; // For input::arduino::ArduinoCom
    use crate::image_processing::{templates::TemplateManager, cache::DetectionCache};
    use std::sync::{Arc, Mutex};
    use std::thread;
    use std::time::Duration;
    
    // Initialize TemplateManager and load templates
    // TemplateManager::load_templates_from_directory will recursively load from subdirectories like "templates/digits/"
    let mut template_manager = TemplateManager::new();
    match template_manager.load_templates_from_directory("rust_bot_ng/templates") {
        Ok(_) => info!("Templates loaded successfully from rust_bot_ng/templates/ (including subdirectories like digits/ if present)."),
        Err(e) => {
            error!("Failed to load templates from rust_bot_ng/templates/: {}. Proceeding with empty TemplateManager.", e);
            // This might be acceptable if templates are optional or only for specific features.
        }
    }
    // TODO: PlayerMonitor will eventually call image_processing::digit_recognition::recognize_digits_in_region,
    //       passing a captured screen region (e.g., HP bar area) and the template_manager_arc.
    //       Example call within PlayerMonitor:
    //       let hp_value = recognize_digits_in_region(&hp_bar_image, &template_manager, "digit_")?;
    let template_manager_arc = Arc::new(template_manager);
    
    // Initialize DetectionCache
    let detection_cache_arc = Arc::new(DetectionCache::new());
    info!("Detection cache initialized.");

    // Initialize BotSettings from the loaded configuration
    let bot_settings = BotSettings {
        auto_heal_hp_threshold: 70, // Default or could be from config if added
        auto_heal_mp_threshold: 50, // Default or could be from config if added
        heal_hotkey: config.hotkeys.heal.clone(),
    };
    info!("BotSettings initialized with heal_hotkey: {}", bot_settings.heal_hotkey);

    // Access player status regions from config for potential use by PlayerMonitor
    info!("HP Region from config: x={}, y={}, w={}, h={}",
        config.player_status_regions.hp.x,
        config.player_status_regions.hp.y,
        config.player_status_regions.hp.width,
        config.player_status_regions.hp.height
    );
    // TODO: PlayerMonitor will eventually use config.player_status_regions.hp and .mp
    //       to define areas for screen capture and OCR/image analysis.

    // Initialize GameContext with BotSettings derived from config
    let game_context = Arc::new(GameContext::new(bot_settings));
    info!("GameContext initialized. Character: {}, HP: {}, is_running: {}",
        config.general.character_name, // Example of using general config
        game_context.get_player_hp(),
        game_context.check_is_running()
    );

    // Initialize Cavebot
    let mut cavebot = Cavebot::new(Arc::clone(&game_context));

    // Add some dummy waypoints for testing
    // cavebot.add_waypoint(Waypoint::new("Start".to_string(), WaypointType::Walk, (100, 200, 7)));
    // cavebot.add_waypoint(Waypoint::new("Open a Door".to_string(), WaypointType::OpenDoor, (110, 200, 7))); // Test OpenDoor
    // cavebot.add_waypoint(Waypoint::new("Use Ladder".to_string(), WaypointType::Use, (105, 200, 7)));
    // cavebot.add_waypoint(Waypoint::new("Go to monsters".to_string(), WaypointType::Walk, (150, 250, 6)));
    // info!("Cavebot initialized with {} waypoints.", cavebot.waypoints_count());

    // Initialize Arc for config to share with AllDependencies
    let config_arc = Arc::new(config);

    // Initialize dependencies (AllDependencies)
    // This will be shared among threads that need it (Cavebot, PlayerMonitor)
    let all_deps = AllDependencies::new(
        Arc::clone(&arduino_com_instance),
        Arc::clone(&template_manager_arc),
        Arc::clone(&detection_cache_arc),
        Arc::clone(&config_arc), // Pass Arc-cloned config
    );
    info!("AllDependencies initialized.");

    // Initialize PlayerMonitor
    let player_monitor = PlayerMonitor::new(Arc::clone(&game_context));
    info!("PlayerMonitor initialized.");

    // Spawn PlayerMonitor loop in a separate thread
    let player_monitor_handle = {
        let monitor_game_context = Arc::clone(&game_context);
        let monitor_deps = all_deps.clone(); // Clone AllDependencies for the new thread
        let player_monitor_instance = player_monitor; // Move monitor into thread

        thread::spawn(move || {
            info!("PlayerMonitor thread started.");
            player_monitor_instance.run_monitoring_loop(&monitor_deps);
            info!("PlayerMonitor thread finished.");
        })
    };
    info!("PlayerMonitor loop started in a separate thread.");

    // Initialize Healer
    // let healer = Healer::new(Arc::clone(&game_context), Arc::clone(&arduino_com_instance));
    // info!("Healer initialized.");

    // Spawn Healer loop in a separate thread
    let healer = Healer::new(Arc::clone(&game_context), Arc::clone(&arduino_com_instance));
    info!("Healer initialized.");
    let healer_handle = {
        let healer_instance = healer;
        let healer_game_context = Arc::clone(&game_context);
        // The heal hotkey is now part of BotSettings within GameContext
        thread::spawn(move || {
            info!("Healer thread started.");
            while healer_game_context.check_is_running() {
                let hotkey_to_use = healer_game_context.bot_settings.lock().unwrap().heal_hotkey.clone();
                if let Err(e) = healer_instance.check_and_perform_heal(&hotkey_to_use) {
                    error!("Error in healer using hotkey '{}': {}", hotkey_to_use, e);
                }
                thread::sleep(Duration::from_millis(250)); // Heal check interval
            }
            info!("Healer thread finished.");
        })
    };
    info!("Healer loop started in a separate thread.");


    // Example of starting Cavebot in a separate thread
    // Note: cavebot_deps (now all_deps) is cloned for the cavebot thread implicitly if we pass it directly
    // or we explicitly clone it if we need to use all_deps later in main thread for other purposes.
    // Since AllDependencies is now Clone, we can clone it for each thread.
    let cavebot_thread_handle = {
        let mut cavebot_instance = cavebot; 
        let cavebot_deps_clone = all_deps.clone(); // Explicitly clone for clarity
        std::thread::spawn(move || {
            info!("Cavebot thread started.");
            cavebot_instance.run_main_loop(&cavebot_deps_clone);
            info!("Cavebot thread finished.");
        })
    };
    info!("Cavebot loop started in a separate thread.");

    // To stop the bot after some time (example)
    // For testing, let the bot run for a defined duration, e.g., 20 seconds
    // Reduced for quicker testing if digit recognition is slow or fails often.
    info!("Main thread: Bot is running. Will attempt to stop in 20 seconds (or less if digit recognition fails).");
    thread::sleep(Duration::from_secs(20)); 
    if game_context.check_is_running() {
        info!("Main thread: Time's up, attempting to stop all loops by setting is_running to false.");
        game_context.set_is_running(false);
    }

    // Join all threads
    let mut all_threads_joined_successfully = true;

    // player_monitor_handle is guaranteed to be Some now if initialization up to that point succeeded.
    match player_monitor_handle.join() {
        Ok(_) => info!("PlayerMonitor thread joined successfully."),
        Err(e) => {
            error!("PlayerMonitor thread panicked: {:?}", e);
            all_threads_joined_successfully = false;
        }
    }
    match healer_handle.join() {
       Ok(_) => info!("Healer thread joined successfully."),
       Err(e) => {
           error!("Healer thread panicked: {:?}", e);
           all_threads_joined_successfully = false;
       }
    }
    match cavebot_thread_handle.join() {
        Ok(_) => info!("Cavebot thread joined successfully."),
        Err(e) => {
            error!("Cavebot thread panicked: {:?}", e);
            all_threads_joined_successfully = false;
        }
    }
    
    if all_threads_joined_successfully {
        info!("All processing finished and threads joined successfully.");
    } else {
        warn!("Some threads panicked. Review logs for details.");
    }


    // Main application loop (if not fully handled by cavebot or other threads)
    // This could be a UI loop or a simpler loop for other tasks.
    // If Cavebot runs in its own thread, this loop might just wait or handle UI.
    // For now, let's assume Cavebot might be run directly or in a thread.
    // If run directly and blocking:
    // // cavebot.run_main_loop(&cavebot_deps); 
    // // The rest of the main function after this line would only execute after cavebot stops.

    // If the main loop here is still needed while Cavebot runs in a thread:
    // while game_context.check_is_running() { 
    //     // TODO: This loop would do other things, or just sleep if Cavebot is primary.
    //     info!("Main thread loop running... is_bot_running: {}", game_context.check_is_running());
    //     std::thread::sleep(std::time::Duration::from_secs(2));
    //     // Example: stop after a few main loop iterations if cavebot is threaded
    //     // static mut COUNTER: u32 = 0;
    //     // unsafe {
    //     //     COUNTER += 1;
    //     //     if COUNTER > 5 { game_context.set_is_running(false); }
    //     // }
    // }
    // info!("Main thread loop finished or Cavebot commanded to stop.");


    // Original placeholder for main loop:
    // // while game_context.check_is_running() { // Main loop controlled by GameContext
    // //     // TODO: Determine game window region dynamically
    //     // let game_window_region = (0, 0, 1920, 1080); // Example, replace with actual logic
    //
    //     // TODO: Capture screen (either full or specific region)
    //     // let current_screen_capture = capture::capture_screen_region(game_window_region.0, game_window_region.1, game_window_region.2, game_window_region.3)?;
    //
    //     // TODO: Process image (e.g., find a specific template, deciding whether to use cache)
    //     // let use_cache_for_target = true; // This could be determined by game logic
    //     // if let Some((x,y,w,h)) = matching::find_template_on_screen("target_icon", &template_manager, &detection_cache, game_window_region, 0.8, use_cache_for_target)? {
    //     //     info!("Target icon found at: ({}, {}), size: ({}, {})", x, y, w, h);
    //     //     // TODO: Make game logic decisions based on this, using game_context
    //     //     // e.g., if game_context.player_stats.lock().unwrap().hp < game_context.bot_settings.lock().unwrap().auto_heal_hp_threshold { /* heal */ }
    //     // }
    //     // TODO: Make game logic decisions
    //     // TODO: Send input, e.g.:
    //     // use crate::input::{mouse, keyboard};
    //     // mouse::move_to(&mut arduino_com, (100, 100))?;
    //     // keyboard::press(&mut arduino_com, &["ctrl", "c"])?;
    //     // TODO: Handle errors
    //     // TODO: Add delay or break condition
    //     // std::thread::sleep(std::time::Duration::from_millis(100)); // Example delay
    // }

    warn!("Application finished without a main loop implementation.");
    debug!("This is a debug message."); // Example debug message
    error!("This is an error message."); // Example error message

    Ok(())
}
