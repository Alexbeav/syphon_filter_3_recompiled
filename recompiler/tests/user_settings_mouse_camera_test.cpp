#include "config_loader.h"

#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>

int main() {
    namespace fs = std::filesystem;
    const fs::path dir = fs::temp_directory_path() / "psxrecomp-mouse-camera-settings-test";
    const fs::path input = dir / "input.toml";
    const fs::path output = dir / "output.toml";
    std::error_code ec;
    fs::create_directories(dir, ec);
    {
        std::ofstream f(input, std::ios::trunc);
        f << "[controller]\n"
             "mouse_camera = true\n"
             "mouse_chase_yaw_sensitivity = 1.25\n"
             "mouse_chase_pitch_sensitivity = 0.75\n"
             "mouse_aim_yaw_sensitivity = 2.5\n"
             "mouse_aim_pitch_sensitivity = 1.5\n"
             "mouse_invert_y = true\n";
    }

    const auto loaded = PSXRecompV4::load_user_settings(input);
    const auto near = [](double a, double b) { return std::fabs(a - b) < 0.000001; };
    if (loaded.parse_error || !loaded.has_mouse_camera || !loaded.mouse_camera ||
        !loaded.has_mouse_chase_yaw_sensitivity || !near(loaded.mouse_chase_yaw_sensitivity, 1.25) ||
        !loaded.has_mouse_chase_pitch_sensitivity || !near(loaded.mouse_chase_pitch_sensitivity, 0.75) ||
        !loaded.has_mouse_aim_yaw_sensitivity || !near(loaded.mouse_aim_yaw_sensitivity, 2.5) ||
        !loaded.has_mouse_aim_pitch_sensitivity || !near(loaded.mouse_aim_pitch_sensitivity, 1.5) ||
        !loaded.has_mouse_invert_y || !loaded.mouse_invert_y) {
        std::cerr << "mouse camera settings did not parse\n";
        return 1;
    }
    if (!PSXRecompV4::save_user_settings(output, loaded)) {
        std::cerr << "mouse camera settings did not save\n";
        return 1;
    }
    const auto roundtrip = PSXRecompV4::load_user_settings(output);
    if (roundtrip.parse_error || !roundtrip.has_mouse_camera || !roundtrip.mouse_camera ||
        !roundtrip.has_mouse_invert_y || !roundtrip.mouse_invert_y ||
        !near(roundtrip.mouse_aim_yaw_sensitivity, 2.5)) {
        std::cerr << "mouse camera settings did not round-trip\n";
        return 1;
    }

    fs::remove_all(dir, ec);
    return 0;
}
