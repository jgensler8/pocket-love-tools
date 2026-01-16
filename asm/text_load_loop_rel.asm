;                    **************************************************************
;                    *                          FUNCTION                          *
;                    **************************************************************
;                    undefined __asm text_load_loop_19b8(undefined2 scene_tex
;    undefined         <UNASSIGNED>   <RETURN>
;    undefined2        DE:2           scene_text_start_addr
;    undefined1        A:1            scene_char_code
;    undefined2        HL:2           pbCharPointer                           XREF[2]:     19c0(W), 19ca(W)  
;    undefined2        HL:2           pbCharVal                               XREF[1]:     19ca(W)  
;                    text_load_loop_19b8                             XREF[3]:     text__switch_rom_then_load_198e:
;                                                                                ramfun47_ce52_text_?_rom2__7b20:
;                                                                                ramfun48_ce9c_rom2__7b6a:7baa(c)  
fa 44 c1        ;LD         A,(text_load_loop_done_pointer_low_c144)         = ??
6f              ;LD         L,A
fa 45 c1        ;LD         A,(text_load_loop_done_pointer_high_c145)        = ??
;                    DE = 766A (start of the text block)
67              ;LD         H,A
;                    this sets up HL to be the values in C144 and C145
;                    which are another address: C0EA
;                    C0EA is the starting address to load text into
;                    (this seems to be used across every scene).
;                    however, this address could be changed to draw text
;                    anywhere on screen (like menus!)
;                    LAB_19c0                                        XREF[3]:     19cd(j), 19d2(j), 19d6(j)  
1a              ;LD         scene_char_code,(scene_text_start_addr)
13              ;INC        scene_text_start_addr
fe f0           ;CP         0xf0
38 0e           ;JR         C,LAB_19d4
fe fe           ;CP         0xfe
20 0c           ;JR         NZ,LAB_19cf
cd 23 1a        ;CALL       text_probably_load_dictionary_1a23               undefined text_probably_load_dic

;;;;;;;;;;;;;;;;;;;;; IF
fe fd ; cp 0xfd
20 05 ; jr LAB_19cf
;;;;;;;;;;;;;;;;;;;; code
1a              ;LD         scene_char_code,(scene_text_start_addr)
 ; ld d,a
 ; cp e,$0
 ; cp a,$1f
13              ;INC        scene_text_start_addr
; 
; rom_phrase(scene_bank_A, scene_idx_HL)
; push HL
; maybe push text_load_loop_done_pointer_low_c144 // text_load_loop_done_pointer_high_c145
cd bc 19 ; call text_rom_phrase_19bc
; pop HL
; maybe pop text_load_loop_done_pointer_low_c144 // text_load_loop_done_pointer_high_c145

18 f1           ;JR         LAB_19c0
;                    LAB_19cf                                        XREF[1]:     19c8(j)  
cd e2 19        ;CALL       text_load_phrase_19e2                            undefined text_load_phrase_19e2(
18 ec           ;JR         LAB_19c0
;                    register A holds our next char
;                    HL+ loads this char into the text mem block and increments HL
;                    LAB_19d4                                        XREF[1]:     19c4(j)  
22              ;LD         (pbCharVal+),scene_char_code
b7              ;OR         scene_char_code
20 e8           ;JR         NZ,LAB_19c0
2b              ;DEC        pbCharVal
7d              ;LD         scene_char_code,pbCharVal
ea 44 c1        ;LD         (text_load_loop_done_pointer_low_c144),scene_c   = ??
7c              ;LD         scene_char_code,pbCharVal
ea 45 c1        ;LD         (text_load_loop_done_pointer_high_c145),scene_   = ??
c9              ;RET
