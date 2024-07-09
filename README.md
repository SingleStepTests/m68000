# m68000
Repository for TomHarte-style JSON tests for the Motorola 68000. Generated using the microcoded core in MAME.

STATUS: at least some have been verified as good. There may be bad edge cases but for the most part it's looking good. 

Use decode.py to convert from .json.bin to .json.

They are in ALMOST the same format as the TomHarte tests, just generated with a better emulator, and:

* RAM pieces are now in 16 bits, as it is on the real processor.
* PC is now set using m_au from MAME. To clarify, it has a number of registers, m_pc, m_ipc, m_au, all of which work as a sort of PC, but are updated differently. m_au seems to be consistent though. It's "next prefetch address" so it's +4 from where the test starts executing.
* Data bus now always is as real processor (i.e. only UDS is on, and you read 0xAB, you will get 0xAB00 for data bus. This differs from TomHarte where it would would give 0xAB)
* I think that's mostly all.

These may not be the final form; I may add new features, or adjust so that certain things go better, etc., but they're worth using now.

Thanks to the MAME project for the awesome microcoded emulator!