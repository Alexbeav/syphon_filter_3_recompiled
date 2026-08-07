// SPDX-License-Identifier: MIT
// Copyright (c) 2026 PSX Ports contributors
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <iosfwd>
#include <string>
#include <vector>

namespace psx_port {

struct PadSample {
    std::uint16_t buttons{0xFFFFU};
    std::uint8_t left_x{0x80U};
    std::uint8_t left_y{0x80U};
    std::uint8_t right_x{0x80U};
    std::uint8_t right_y{0x80U};
    bool connected{true};
    bool analog{};

    bool operator==(const PadSample& other) const noexcept;
    [[nodiscard]] bool neutral() const noexcept;
};

struct InputSample {
    std::uint64_t index{};
    std::array<PadSample, 2> ports{};

    bool operator==(const InputSample& other) const noexcept;
};

class InputTimeline {
public:
    static constexpr const char* format_magic = "PSXPAD2";
    static constexpr const char* legacy_format_magic = "PSXPAD1";
    static constexpr std::size_t max_samples = 10'000'000U;

    void setCompatibilityId(std::string compatibility_id);
    [[nodiscard]] const std::string& compatibilityId() const noexcept {
        return compatibility_id_;
    }
    void append(const InputSample& sample);
    [[nodiscard]] const std::vector<InputSample>& samples() const noexcept {
        return samples_;
    }
    [[nodiscard]] bool hasNeutralBookends() const noexcept;

    void write(std::ostream& output) const;
    static InputTimeline read(std::istream& input);

private:
    std::string compatibility_id_;
    std::vector<InputSample> samples_;
};

struct ReplayResult {
    std::array<PadSample, 2> ports{};
    bool consumed{};
    bool complete{};
};

class InputReplay {
public:
    explicit InputReplay(const InputTimeline& timeline) : timeline_{timeline} {}
    [[nodiscard]] ReplayResult sample(std::uint64_t consumer_index,
                                      bool consumer_ready);
    [[nodiscard]] std::size_t consumed() const noexcept { return cursor_; }

private:
    const InputTimeline& timeline_;
    std::size_t cursor_{};
};

} // namespace psx_port
