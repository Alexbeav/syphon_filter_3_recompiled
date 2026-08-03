#include "mouse_camera.h"
#include <assert.h>
#include <string.h>

static unsigned char ram[0x200000];
static uint32_t read_word(uint32_t addr) {
    uint32_t p = addr & 0x1FFFFFu;
    return ram[p] | ((uint32_t)ram[p+1] << 8) | ((uint32_t)ram[p+2] << 16) | ((uint32_t)ram[p+3] << 24);
}
static void write_word(uint32_t addr, uint32_t value) {
    uint32_t p = addr & 0x1FFFFFu;
    ram[p]=value; ram[p+1]=value>>8; ram[p+2]=value>>16; ram[p+3]=value>>24;
}

int main(void) {
    CPUState cpu = {0};
    PsxMouseCameraStats stats;
    PsxMouseCameraConfig config = {
        .enabled=1, .facing_site=0x800549C4u, .facing_expected=0x8EA30034u,
        .application_state_addr=0x80121B88u, .player_state_offset=0x20u,
        .wrapper_offset=0xF8u, .base_offset=0xA4u, .owner_offset=0xDCu,
        .desired_pitch_offset=0x8E8u, .rendered_pitch_offset=0x918u,
        .vector_x_offset=0xCCu, .vector_y_offset=0xD0u, .vector_z_offset=0xD4u,
        .player_reg=19, .controller_reg=18,
        .chase_yaw_sensitivity=.75, .chase_pitch_sensitivity=1.0,
        .aim_yaw_sensitivity=1.0, .aim_pitch_sensitivity=1.0,
    };
    cpu.read_word=read_word; cpu.write_word=write_word;
    cpu.gpr[19]=0x80100608u; cpu.gpr[18]=0x80101CF4u;
    write_word(config.facing_site, config.facing_expected);
    write_word(cpu.gpr[19]+0x20u, 0x80102000u);
    write_word(0x80102000u+0xF8u, 0x80103000u);
    write_word(0x80103000u+0xDCu, cpu.gpr[19]);
    write_word(0x80103000u+0xA4u, 0x80104000u);
    write_word(0x80104000u+0x8E8u, 100u);
    psx_mouse_camera_configure(&config);
    psx_mouse_camera_set_focus(1);
    psx_mouse_camera_add_motion(8, 5);
    psx_mouse_camera_hook(&cpu, config.facing_site);
    assert((int32_t)read_word(cpu.gpr[18]+0xCCu) == 6*4096);
    assert((int32_t)read_word(0x80104000u+0x8E8u) == 105);
    assert((int32_t)read_word(0x80104000u+0x918u) == 105);
    psx_mouse_camera_set_aim(1);
    psx_mouse_camera_add_motion(-3, 10);
    psx_mouse_camera_hook(&cpu, config.facing_site);
    assert((int32_t)read_word(cpu.gpr[18]+0xCCu) == -3*4096);
    assert((int32_t)read_word(cpu.gpr[18]+0xD4u) == 10*4096);
    write_word(0x80103000u+0xDCu, 0x80109999u);
    psx_mouse_camera_add_motion(20, 20);
    psx_mouse_camera_hook(&cpu, config.facing_site);
    psx_mouse_camera_get_stats(&stats);
    assert(stats.applied_chase == 1 && stats.applied_aim == 1);
    assert(stats.rejected_owner == 1);
    return 0;
}
