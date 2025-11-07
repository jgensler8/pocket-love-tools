ARES=..\ares-windows-x64\ares-v145\ares.exe
MEDNAFEN=..\mednafen-1.32.0-UNSTABLE-win64\mednafen.exe
MGBA=../mGBA-0.10.5-win64/mGBA-0.10.5-win64/mGBA.exe 

replace:
	python ./replace_2.py

run_og:
	$(MEDNAFEN) ./Pocket_Love_If_1999_KID_JP.ngc

run:
# 	$(ARES) ./pocklove_replaced.ngc
# 	$(MEDNAFEN) ./pocklove_replaced.ngc
	$(MGBA) "C:\Users\jgens\Downloads\pocket_love_mod\Pocket Love (J) [S].gb"
# 	$(MGBA) "C:\Users\jgens\Downloads\pocket_love_mod\pocket_love_ghidra_out.gb.bin"

run_rep:
	$(MGBA) ./pkl.gb

# diff: fc.exe /b .\pkl.gb .\pkl.gb.bin