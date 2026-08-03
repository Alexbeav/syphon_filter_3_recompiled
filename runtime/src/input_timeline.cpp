// SPDX-License-Identifier: MIT
// Copyright (c) 2026 PSX Ports contributors
#include "input_timeline.hpp"

#include <iomanip>
#include <istream>
#include <limits>
#include <ostream>
#include <stdexcept>
#include <utility>

namespace psx_port {
namespace {

PadSample neutral_pad() { return {}; }

unsigned read_hex(std::istream& input, const char* field) {
    std::string token;
    if (!(input >> token))
        throw std::runtime_error{std::string{"missing input-timeline field: "} + field};
    std::size_t consumed = 0;
    unsigned long value = 0;
    try {
        value = std::stoul(token, &consumed, 16);
    } catch (const std::exception&) {
        throw std::runtime_error{std::string{"invalid hexadecimal field: "} + field};
    }
    if (consumed != token.size() || value > std::numeric_limits<unsigned>::max())
        throw std::runtime_error{std::string{"invalid hexadecimal field: "} + field};
    return static_cast<unsigned>(value);
}

PadSample read_pad(std::istream& input) {
    const auto buttons = read_hex(input, "buttons");
    const auto left_x = read_hex(input, "left_x");
    const auto left_y = read_hex(input, "left_y");
    const auto right_x = read_hex(input, "right_x");
    const auto right_y = read_hex(input, "right_y");
    const auto connected = read_hex(input, "connected");
    const auto analog = read_hex(input, "analog");
    if (buttons > 0xFFFFU || left_x > 0xFFU || left_y > 0xFFU ||
        right_x > 0xFFU || right_y > 0xFFU || connected > 1U || analog > 1U)
        throw std::runtime_error{"input-timeline pad value is out of range"};
    return {static_cast<std::uint16_t>(buttons), static_cast<std::uint8_t>(left_x),
            static_cast<std::uint8_t>(left_y), static_cast<std::uint8_t>(right_x),
            static_cast<std::uint8_t>(right_y), connected != 0U, analog != 0U};
}

void write_pad(std::ostream& output, const PadSample& pad) {
    output << ' ' << std::setw(4) << static_cast<unsigned>(pad.buttons)
           << ' ' << std::setw(2) << static_cast<unsigned>(pad.left_x)
           << ' ' << std::setw(2) << static_cast<unsigned>(pad.left_y)
           << ' ' << std::setw(2) << static_cast<unsigned>(pad.right_x)
           << ' ' << std::setw(2) << static_cast<unsigned>(pad.right_y)
           << ' ' << static_cast<unsigned>(pad.connected)
           << ' ' << static_cast<unsigned>(pad.analog);
}

} // namespace

bool PadSample::neutral() const noexcept {
    return buttons == 0xFFFFU && left_x == 0x80U && left_y == 0x80U &&
           right_x == 0x80U && right_y == 0x80U;
}

bool PadSample::operator==(const PadSample& other) const noexcept {
    return buttons == other.buttons && left_x == other.left_x &&
           left_y == other.left_y && right_x == other.right_x &&
           right_y == other.right_y && connected == other.connected &&
           analog == other.analog;
}

bool InputSample::operator==(const InputSample& other) const noexcept {
    return index == other.index && ports == other.ports;
}

void InputTimeline::setCompatibilityId(std::string compatibility_id) {
    if (compatibility_id.size() > 128U ||
        compatibility_id.find_first_of(" \t\r\n") != std::string::npos)
        throw std::invalid_argument{
            "input-timeline compatibility ID must be a whitespace-free token of at most 128 bytes"};
    compatibility_id_ = std::move(compatibility_id);
}

void InputTimeline::append(const InputSample& sample) {
    if (sample.index != samples_.size())
        throw std::invalid_argument{"input-timeline sample indices must be contiguous"};
    samples_.push_back(sample);
}

bool InputTimeline::hasNeutralBookends() const noexcept {
    if (samples_.empty()) return false;
    const auto neutral = [](const InputSample& sample) {
        return sample.ports[0].neutral() && sample.ports[1].neutral();
    };
    return neutral(samples_.front()) && neutral(samples_.back());
}

void InputTimeline::write(std::ostream& output) const {
    output << format_magic << ' ' << samples_.size() << ' '
           << (compatibility_id_.empty() ? "-" : compatibility_id_) << '\n';
    output << std::hex << std::setfill('0');
    for (const auto& sample : samples_) {
        output << std::dec << sample.index << std::hex;
        write_pad(output, sample.ports[0]);
        write_pad(output, sample.ports[1]);
        output << '\n';
    }
    if (!output) throw std::runtime_error{"failed to write input timeline"};
}

InputTimeline InputTimeline::read(std::istream& input) {
    std::string magic;
    std::size_t count = 0;
    if (!(input >> magic >> count) ||
        (magic != format_magic && magic != legacy_format_magic))
        throw std::runtime_error{"invalid input-timeline header"};
    if (count > max_samples)
        throw std::runtime_error{"input-timeline sample count exceeds safety limit"};
    InputTimeline timeline;
    if (magic == format_magic) {
        std::string compatibility_id;
        if (!(input >> compatibility_id))
            throw std::runtime_error{"missing input-timeline compatibility ID"};
        if (compatibility_id != "-") timeline.setCompatibilityId(compatibility_id);
    }
    for (std::size_t expected = 0; expected < count; ++expected) {
        std::uint64_t index = 0;
        if (!(input >> std::dec >> index))
            throw std::runtime_error{"missing input-timeline sample index"};
        InputSample sample;
        sample.index = index;
        sample.ports[0] = read_pad(input);
        sample.ports[1] = read_pad(input);
        timeline.append(sample);
    }
    std::string trailing;
    if (input >> trailing)
        throw std::runtime_error{"unexpected trailing input-timeline data"};
    return timeline;
}

ReplayResult InputReplay::sample(std::uint64_t consumer_index,
                                 bool consumer_ready) {
    ReplayResult result;
    result.ports = {neutral_pad(), neutral_pad()};
    if (!consumer_ready) {
        result.complete = cursor_ >= timeline_.samples().size();
        return result;
    }
    if (cursor_ >= timeline_.samples().size()) {
        result.complete = true;
        return result;
    }
    const auto& next = timeline_.samples()[cursor_];
    if (next.index != consumer_index)
        throw std::runtime_error{"input replay consumer index diverged"};
    result.ports = next.ports;
    result.consumed = true;
    ++cursor_;
    result.complete = cursor_ >= timeline_.samples().size();
    return result;
}

} // namespace psx_port
