; replaces the old text_load_loop because i am too lazy to patch the 3 other call instructions
; 19b8
; call text_load_loop_old (0x3d62)
cd 62 3d
; ret
c9