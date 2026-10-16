ARES=..\ares-windows-x64\ares-v145\ares.exe
MEDNAFEN=..\mednafen-1.32.0-UNSTABLE-win64\mednafen.exe
MGBA=../mGBA-0.10.5-win64/mGBA-0.10.5-win64/mGBA.exe 
# PYTHON=C:\Users\jgens\AppData\Local\Programs\Python\Python313\python.exe
PYTHON=C:/Users/jgens/AppData/Local/Programs/Python/Python313/python.exe

OUT_DIR=out
OG_ROM="Pocket Love (J) [S].gb"
PATCHED_ROM="pocklove_patched.gb"
SAFE_DIALOG_BANK_START=6
SAFE_DIALOG_BANK_END=13
# banks 14..31 might have image data
# bank 16 definitely has image data
# 6..13 still missed the early scenes after choosing audio

replace:
	python ./replace_2.py

translate:
	python ./translate.py

extract_phrases:
	python ./extract_phrases.py

extract_scene_roms:
	$(shell for i in 4 {${SAFE_DIALOG_BANK_START}..${SAFE_DIALOG_BANK_END}} ; do $(PYTHON) extract_scene_rom.py --bank=$${i} --out_dir=${OUT_DIR} ; done;)

extract_scene_meta:
	$(PYTHON) extract_scene_meta.py --bank=5 --out_dir=${OUT_DIR}

translate_test:
	$(PYTHON) translate_test.py

translate_ex:
# 	$(PYTHON) translate_ex.py bank_8_ex.json bank_8_tr_en.json
# 	$(PYTHON) translate_ex.py --start_scene=0 --end_scene=16 bank_8_ex.json bank_8_tr_en.json
# 	$(PYTHON) translate_ex.py --start_scene=0 --end_scene=600 ${OUT_DIR}/bank_8_ex.json ${OUT_DIR}/bank_8_tr_en.json
	$(PYTHON) translate_ex.py --start_scene=0 --end_scene=600 ${OUT_DIR}/bank_4_ex.json ${OUT_DIR}/bank_4_tr_en.json

translate_template:
# 	$(PYTHON) translate_template.py --bank=3 bank_3_ex.json bank_3_tr_temp.json
# 	$(PYTHON) translate_template.py --bank=4 bank_4_ex.json bank_4_tr_temp.json
# 	$(PYTHON) translate_template.py --bank=5 bank_5_ex.json bank_5_tr_temp.json
	$(shell for i in 4 {${SAFE_DIALOG_BANK_START}..${SAFE_DIALOG_BANK_END}} ; do $(PYTHON) translate_template.py --bank=$$i ${OUT_DIR}/bank_$${i}_ex.json ${OUT_DIR}/bank_$${i}_tr_temp.json ; done;)

patch:
	$(shell cp $(OG_ROM) $(PATCHED_ROM))
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) mbc)
# 	$(shell $(PYTHON) patch.py $(PATCHED_ROM) inplace --bank=2 --hex_addr=41e2 --hex_value=05)
# this might be the rombank strip, not entirely sure its still needed
# 	$(shell $(PYTHON) patch.py $(PATCHED_ROM) inplace --bank=2 --hex_addr=41e3 --hex_value=02)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) dialog --bank=4 --overflow_bank 34 ${OUT_DIR}/bank_4_ex.json ${OUT_DIR}/bank_4_tr_en.json)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) dialog --bank=8 --overflow_bank 35 ${OUT_DIR}/bank_8_ex.json ${OUT_DIR}/bank_8_tr_en.json)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) dialog --bank=9 --overflow_bank 36 ${OUT_DIR}/bank_9_ex.json ${OUT_DIR}/bank_9_tr_en.json)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) dialog --bank=10 --overflow_bank 37 ${OUT_DIR}/bank_10_ex.json ${OUT_DIR}/bank_10_tr_en.json)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) dialog --bank=11 --overflow_bank 38 ${OUT_DIR}/bank_11_ex.json ${OUT_DIR}/bank_11_tr_en.json)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) dialog --bank=12 --overflow_bank 39 ${OUT_DIR}/bank_12_ex.json ${OUT_DIR}/bank_12_tr_en.json)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) dialog --bank=13 --overflow_bank 40 --prefix "__81" ${OUT_DIR}/bank_13_ex.json ${OUT_DIR}/bank_13_tr_en.json)
# 	$(shell $(PYTHON) patch.py $(PATCHED_ROM) dialog --bank=33 ${OUT_DIR}/bank_33_ex.json ${OUT_DIR}/bank_33_test_tr.json)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) file --bank=29 --file=patch_start_screen_29.txt)
# patch both phone call wait and day<>day wait (original 0x32)
# 	$(shell $(PYTHON) patch.py $(PATCHED_ROM) inplace --bank=30 --hex_addr=6707 --hex_value=01)
# 	$(shell $(PYTHON) patch.py $(PATCHED_ROM) file --bank=30 --file=patch_stat_requirements.txt)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) file --bank=30 --file=patch_menus_bank_30.txt)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) alphabet --png font_alphabet.png)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) font_ex --png font_ex.png)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) phrases --phrases_file phrases_en.py)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) code_raw --file asm/text_load_loop_old.asm --hex_addr 0x19b8)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) code_raw --file asm/text_rom_phrase.asm --hex_addr 0x19bb)
	$(shell $(PYTHON) patch.py $(PATCHED_ROM) code_raw --file asm/text_load_loop_rel.asm --hex_addr 0x3fbc)
# testing menu options for going to fireworks
# 	$(shell $(PYTHON) patch.py $(PATCHED_ROM) inplace --bank=30 --hex_addr=5838 --hex_value=1d)
# 	$(shell $(PYTHON) patch.py $(PATCHED_ROM) inplace --bank=30 --hex_addr=5839 --hex_value=1d)
# 	$(shell $(PYTHON) patch.py $(PATCHED_ROM) file --bank=29 --file=patch_stat_init_29.txt)

run_og:
	$(MEDNAFEN) ./Pocket_Love_If_1999_KID_JP.ngc

run:
# 	$(ARES) ./pocklove_replaced.ngc
# 	$(MEDNAFEN) ./pocklove_replaced.ngc
	$(MGBA) "C:\Users\jgens\Downloads\pocket_love_mod\Pocket Love (J) [S].gb"
# 	$(MGBA) "C:\Users\jgens\Downloads\pocket_love_mod\pocket_love_ghidra_out.gb.bin"

run_patch:
	$(MGBA) $(PATCHED_ROM)

run_rep:
	$(MGBA) ./pkl.gb

pct:
	cat ./out/*tr_en.json | grep " B" | wc -l
	cat ./out/*tr_en.json | grep eng | grep -v " B" | wc -l

# diff: fc.exe /b .\pkl.gb .\pkl.gb.bin