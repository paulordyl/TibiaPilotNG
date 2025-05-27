# Testing Digit Recognition

## Objective

This document outlines the process and requirements for testing the image-based digit recognition functionality (`recognize_digits_in_region`) in the `rust_bot_ng` project. Accurate digit recognition is crucial for features like reading HP, MP, quantities, etc., from the game screen.

## Required Test Assets

To effectively test and refine the digit recognition, we need a set of image assets:

### 1. Digit Templates

These are individual image files for each digit (0 through 9).
*   **Naming Convention**: `digit_0.png`, `digit_1.png`, ..., `digit_9.png`.
*   **Location**: `rust_bot_ng/templates/digits/`
*   **Specifications**:
    *   Each image should contain only one digit.
    *   Digits should be tightly cropped (minimal empty space around the digit).
    *   They must accurately represent the font, size, and style of digits as they appear in the game UI elements you want to read.
    *   Ensure consistent background color if possible, or use transparency if the digit rendering in-game supports it and templates are PNGs.
    *   The current placeholder files in this directory must be replaced with these actual game assets.

### 2. Test Images (Fixtures)

These are sample screenshots of game UI elements that display numbers you intend to read (e.g., HP bars, MP bars, item counts).
*   **Location**: `rust_bot_ng/tests/fixtures/digit_recognition/`
    *   Create this directory if it doesn't exist.
*   **Naming Convention**: Use descriptive names, e.g., `hp_100_max_150.png`, `mp_75_full.png`, `item_count_12.png`.
*   **Specifications**:
    *   Capture screenshots of various numbers and scenarios.
    *   Include examples of minimum, maximum, and typical values.
    *   If possible, include images where numbers might be close to other UI elements to test robustness.
    *   Ensure these images are saved in a standard format (e.g., PNG).

## Directory Structure

The expected directory structure for these assets is:

```
rust_bot_ng/
├── src/
│   └── ... (project source code)
├── templates/
│   └── digits/         # <-- Your actual digit templates go here
│       ├── digit_0.png
│       ├── digit_1.png
│       └── ...
│       └── digit_9.png
├── tests/
│   └── fixtures/
│       └── digit_recognition/  # <-- Your test images go here
│           ├── hp_example_01.png
│           ├── mp_example_01.png
│           └── ... (other test images)
└── TESTING_DIGIT_RECOGNITION.md # <-- This file
└── ... (other project files like Cargo.toml, config.toml)
```

## Testing Procedure Outline

The primary way to test is by expanding the unit tests in `src/image_processing/digit_recognition.rs`.

1.  **Navigate to the Test Module**: Open `src/image_processing/digit_recognition.rs` and find the `#[cfg(test)] mod tests { ... }` section.
2.  **Create or Modify Test Functions**:
    *   You can modify the existing `test_recognize_simple_number()` or (preferably) create new, more specific test functions for each test image.
    *   Example test function:
        ```rust
        #[test]
        fn test_hp_reading_from_image_example_01() {
            // 1. Setup: Initialize logger, TemplateManager
            //    (Ensure TemplateManager loads from the correct `templates/` path)
            //    let mut template_manager = TemplateManager::new();
            //    // Adjust path as needed relative to where tests are run or use absolute/manifest-relative paths
            //    template_manager.load_templates_from_directory("../../templates").expect("Failed to load templates");

            // 2. Load Test Image (Fixture):
            //    let test_image_path = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/digit_recognition/hp_example_01.png");
            //    let region_image = image::open(test_image_path).expect("Failed to load test image: hp_example_01.png");

            // 3. Call Recognition Function:
            //    let recognized_value = recognize_digits_in_region(&region_image, &template_manager, "digit_");

            // 4. Assert Expected Outcome:
            //    // Assuming hp_example_01.png shows the number 123
            //    assert_eq!(recognized_value.unwrap(), Some(123), "Failed to recognize HP as 123 from hp_example_01.png");
        }
        ```
3.  **Run Tests**: Execute `cargo test` from the `rust_bot_ng` project root.
4.  **Iterate**: If tests fail, examine the detailed logs produced by `recognize_digits_in_region`. You may need to:
    *   Adjust the digit templates.
    *   Tune parameters within `recognize_digits_in_region` (see below).
    *   Verify the screen regions defined in `config.toml` if testing the full `PlayerMonitor` flow.

## Key Tuning Parameters

Within `src/image_processing/digit_recognition.rs`, the `recognize_digits_in_region` function's accuracy can be influenced by:

*   **`confidence_threshold`**: (Inside `recognize_digits_in_region`, passed to `locate_all_templates_on_image`). If too high, faint or slightly different digits might be missed. If too low, false positives might occur.
*   **`max_overlap`**: (Passed to `locate_all_templates_on_image`). Affects the simple Non-Maximum Suppression. If digits are very close, this might need tuning.
*   **Quality of Digit Templates**: This is paramount. Templates must be clean and representative.
*   **Image Preprocessing**: Currently, no specific preprocessing (like binarization or scaling) is done on the `region_image` before digit matching. If recognition is poor, such steps might need to be added to `recognize_digits_in_region` or applied to the source image before calling.

## Contribution

Please populate the `templates/digits/` and `tests/fixtures/digit_recognition/` directories with the high-quality assets described above. This will enable thorough testing and refinement of the bot's visual perception capabilities.
```
