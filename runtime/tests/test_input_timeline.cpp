// SPDX-License-Identifier: MIT
// Copyright (c) 2026 PSX Ports contributors
#include "input_timeline.hpp"

#include <cstdlib>
#include <sstream>
#include <stdexcept>

namespace {
void require(bool condition) {
    if (!condition) std::abort();
}

psx_port::InputSample sample(std::uint64_t index, std::uint16_t buttons) {
    psx_port::InputSample value;
    value.index = index;
    value.ports[0].buttons = buttons;
    return value;
}
}

int main() {
    using psx_port::InputReplay;
    using psx_port::InputTimeline;
    InputTimeline timeline;
    timeline.setCompatibilityId("test-contract");
    timeline.append(sample(0, 0xFFFFU));
    timeline.append(sample(1, 0xBFFFU));
    auto analog = sample(2, 0xFFFFU);
    analog.ports[0].analog = true;
    analog.ports[0].left_x = 0x90U;
    timeline.append(analog);
    timeline.append(sample(3, 0xFFFFU));
    require(timeline.hasNeutralBookends());

    std::stringstream encoded;
    timeline.write(encoded);
    const auto decoded = InputTimeline::read(encoded);
    require(decoded.samples() == timeline.samples());
    require(decoded.compatibilityId() == timeline.compatibilityId());

    InputReplay replay{decoded};
    require(!replay.sample(0, false).consumed);
    require(replay.sample(0, true).ports[0].neutral());
    require(replay.sample(1, true).ports[0].buttons == 0xBFFFU);
    require(replay.sample(2, true).ports[0].left_x == 0x90U);
    require(replay.sample(3, true).complete);
    require(replay.sample(4, true).ports[0].neutral());

    bool rejected_gap = false;
    try {
        InputTimeline invalid;
        invalid.append(sample(1, 0xFFFFU));
    } catch (const std::invalid_argument&) { rejected_gap = true; }
    require(rejected_gap);

    bool rejected_trailing = false;
    try {
        std::stringstream invalid{
            "PSXPAD2 1 test\n0 ffff 80 80 80 80 1 0 ffff 80 80 80 80 1 0\nextra\n"};
        static_cast<void>(InputTimeline::read(invalid));
    } catch (const std::runtime_error&) { rejected_trailing = true; }
    require(rejected_trailing);
    return 0;
}
