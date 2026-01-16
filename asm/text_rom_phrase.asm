;; place after text_load_loop_old (4 bytes after that fn so 0x19bc)
;; function text_rom_phrase
;; args: A new rom bank
;; args: DE phrase index
; ld c,a
4f
; push prerom
fa a2 c0 (c0a2 is the current rom bank)
; ld c,a
79
; switchrom(33)
cd 7b 03
; call text_load_loop (DE is arg)
cd 
; pop
; switchrom(prerom)
; ret