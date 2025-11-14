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
# 6..13 still missed the early scenes after choosing audio

replace:
	python ./replace_2.py

translate:
	python ./translate.py

scan_phrases:
	python ./scan_phrases.py

extract_scene_roms:
	$(shell for i in {${SAFE_DIALOG_BANK_START}..${SAFE_DIALOG_BANK_END}} ; do $(PYTHON) extract_scene_rom.py --bank=$${i} --out_dir=${OUT_DIR} ; done;)

translate_test:
	$(PYTHON) translate_test.py

translate_ex:
# 	$(PYTHON) translate_ex.py bank_8_ex.json bank_8_tr_en.json
# 	$(PYTHON) translate_ex.py --start_scene=0 --end_scene=16 bank_8_ex.json bank_8_tr_en.json
	$(PYTHON) translate_ex.py --start_scene=0 --end_scene=600 bank_8_ex.json bank_8_tr_en.json

translate_template:
# 	$(PYTHON) translate_template.py --bank=3 bank_3_ex.json bank_3_tr_temp.json
# 	$(PYTHON) translate_template.py --bank=4 bank_4_ex.json bank_4_tr_temp.json
# 	$(PYTHON) translate_template.py --bank=5 bank_5_ex.json bank_5_tr_temp.json
	$(shell for i in {${SAFE_DIALOG_BANK_START}..${SAFE_DIALOG_BANK_END}} ; do $(PYTHON) translate_template.py --bank=$$i ${OUT_DIR}/bank_$${i}_ex.json ${OUT_DIR}/bank_$${i}_tr_temp.json ; done;)

patch:
# 	cp $(OG_ROM) $(PATCHED_ROM)
# 	$(PYTHON) patch.py --bank=8 $(PATCHED_ROM) bank_8_ex.json bank_8_tr_en.json
# 	$(PYTHON) patch.py --bank=3 $(PATCHED_ROM) bank_3_ex.json bank_3_tr_temp.json
# 	$(PYTHON) patch.py --bank=4 $(PATCHED_ROM) bank_4_ex.json bank_4_tr_temp.json
# 	$(PYTHON) patch.py --bank=5 $(PATCHED_ROM) bank_5_ex.json bank_5_tr_temp.json
	$(shell cp $(OG_ROM) $(PATCHED_ROM))
	$(shell for i in {${SAFE_DIALOG_BANK_START}..${SAFE_DIALOG_BANK_END}} ; do $(PYTHON) patch.py --bank=$$i $(PATCHED_ROM) ${OUT_DIR}/bank_$${i}_ex.json ${OUT_DIR}/bank_$${i}_tr_temp.json ; done;)

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

# diff: fc.exe /b .\pkl.gb .\pkl.gb.bin