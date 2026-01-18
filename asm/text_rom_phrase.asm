;; place after text_load_loop_old (3 bytes after that fn so 0x19bb )
;; function text_rom_phrase
;; args: DE now points to our args (arg 0: new_rom, arg 1: scene_index)

; 1: setup
fa a2 c0 ; ldh a,[a16] c0a2 (prerom)
f5       ; push AF (prerom)

; 2: logic

         ;; save new_rom to b
1a       ; ld a,[DE] (new_rom)
47       ; ld b,a
13       ; inc de

         ;; load new phrase pointer into DE (4000 + idx => value goes into high_c145/low_c144)
         ;;; setup 0x4000 + scene_index
1a       ; ld a,[DE] (scene_index)
cb 20    ; sla (shift left arithmetic aka *2 ) , ignore carry flag
5f       ; ld e,a
16 40    ; ld d,0x40

         ;; switch to new_rom
78       ; ld a, b
cd 7b 03 ; call switch_rom_addr_037b (33)

         ;;; first byte in phrase table (low) -> E
1a       ; ld a, [DE]
4f       ; ld c, a
         ;;; second byte in phrase table (high) -> D
13       ; inc de
1a       ; ld a, [DE]
c6 40    ; adc a,0x40
57       ; ld d, a
59       ; ld e, c

         ;; utilize existing text function
cd bc 3f ; call text_load_loop_old_3fbc (DE is arg)

; 3: cleanup
f1       ; pop af
cd 7b 03 ; call switch_rom_addr_037b
c9       ; ret