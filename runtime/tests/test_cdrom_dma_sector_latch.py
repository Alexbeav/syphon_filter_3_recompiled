#!/usr/bin/env python3
"""Pin the CD decoder-buffer lifetime across split header/payload DMA."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def function_body(source: str, signature: str, next_signature: str) -> str:
    start = source.index(signature)
    end = source.index(next_signature, start)
    return source[start:end]


def model_contract() -> None:
    sector_a = bytes((index * 17) & 0xFF for index in range(2340))
    sector_b = bytes((index * 29) & 0xFF for index in range(2340))
    latch = sector_a
    position = 0

    header = latch[position : position + 12]
    position += len(header)
    current_decoder_buffer = sector_b
    payload = latch[position : position + 2048]
    position += len(payload)

    assert header + payload == sector_a[:2060]
    assert payload != current_decoder_buffer[12:2060]
    assert position == 2060


def main() -> None:
    source = (ROOT / "runtime/src/cdrom.c").read_text(encoding="utf-8")
    begin = function_body(source, "void cdrom_dma_begin", "void cdrom_dma_end")
    end = function_body(source, "void cdrom_dma_end", "uint32_t cdrom_dma_read")
    read = function_body(source, "uint32_t cdrom_dma_read", "int cdrom_dma_ready")
    sector_delivery = function_body(
        source, "static int read_sector_at", "static void advance_msf"
    )
    init = function_body(source, "void cdrom_init", "int cdrom_has_disc")

    assert "cdrom_dma_latch_if_ready();" in begin
    assert "cdrom_dma_reset_latch();" not in begin
    assert "dma_sector_read_pos >= dma_sector_size" in end
    assert "dma_sector_buffer + dma_sector_read_pos" in read
    assert "memset(dma_sector_buffer" not in sector_delivery
    assert "memset(dma_sector_buffer" in init

    model_contract()
    print("CD-ROM split-DMA sector latch contract: PASS")


if __name__ == "__main__":
    main()
