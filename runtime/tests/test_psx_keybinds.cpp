
#include "psx_keybinds.h"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

int main() {
    namespace fs = std::filesystem;
    const fs::path path = fs::current_path() / "psx-keybinds-contract-test.ini";
    {
        std::ofstream out(path, std::ios::binary | std::ios::trunc);
        out << "[player1]\n"
               "cross = X, Mouse1\n"
               "circle = Z, RMB\n"
               "\n[player2]\n"
               "cross = None\n";
    }

    psx_keybinds_load_file(path.string().c_str());
    bool ok = true;
    ok &= psx_keybinds_get_button(1, PSX_KB_CROSS) == SDL_SCANCODE_X;
    ok &= static_cast<int>(
        psx_keybinds_get_button_alt(1, PSX_KB_CROSS)) > SDL_NUM_SCANCODES;
    ok &= static_cast<int>(
        psx_keybinds_get_button_alt(1, PSX_KB_CIRCLE)) > SDL_NUM_SCANCODES;
    ok &= psx_keybinds_get_button_alt(2, PSX_KB_CROSS) ==
        SDL_SCANCODE_UNKNOWN;

    psx_keybinds_save();
    std::ifstream saved(path, std::ios::binary);
    const std::string text((std::istreambuf_iterator<char>(saved)),
                           std::istreambuf_iterator<char>());
    ok &= text.find("cross     = X, Mouse1") != std::string::npos;
    ok &= text.find("circle    = Z, Mouse3") != std::string::npos;

    std::error_code ignored;
    fs::remove(path, ignored);
    if (!ok) {
        std::cerr << "keybind dual/mouse persistence contract failed\n";
        return 1;
    }
    std::cout << "PASS: dual keyboard/mouse bindings round-trip\n";
    return 0;
}

