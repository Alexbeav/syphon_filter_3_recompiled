// SPDX-License-Identifier: MIT
// Copyright (c) 2026 PSX Ports contributors
#include "input_timeline.hpp"

#include <cassert>
#include <sstream>
#include <stdexcept>

namespace {
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
    timeline.setCompatibilityId("sf3-test-contract");
    timeline.append(sample(0, 0xFFFFU));
    timeline.append(sample(1, 0xBFFFU));
    auto analog = sample(2, 0xFFFFU);
    analog.ports[0].analog = true;
    analog.ports[0].left_x = 0x90U;
    timeline.append(analog);
    timeline.append(sample(3, 0xFFFFU));
    assert(timeline.hasNeutralBookends());

    std::stringstream encoded;
    timeline.write(encoded);
    const auto decoded = InputTimeline::read(encoded);
    assert(decoded.samples() == timeline.samples());
    assert(decoded.compatibilityId() == timeline.compatibilityId());

    InputReplay replay{decoded};
    assert(!replay.sample(0, false).consumed);
    assert(replay.sample(0, true).ports[0].neutral());
    assert(replay.sample(1, true).ports[0].buttons == 0xBFFFU);
    assert(replay.sample(2, true).ports[0].left_x == 0x90U);
    assert(replay.sample(3, true).complete);
    assert(replay.sample(4, true).ports[0].neutral());

    bool rejected_gap = false;
    try {
        InputTimeline invalid;
        invalid.append(sample(1, 0xFFFFU));
    } catch (const std::invalid_argument&) { rejected_gap = true; }
    assert(rejected_gap);

    bool rejected_trailing = false;
    try {
        std::stringstream invalid{
            "PSXPAD2 1 test\n0 ffff 80 80 80 80 1 0 ffff 80 80 80 80 1 0\nextra\n"};
        static_cast<void>(InputTimeline::read(invalid));
    } catch (const std::runtime_error&) { rejected_trailing = true; }
    assert(rejected_trailing);
    return 0;
}
