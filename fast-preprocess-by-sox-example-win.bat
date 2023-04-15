
@ECHO ON
SET FROM_DIR=input\
SET TO_DIR=output\

SET TO_PATH=%~dp0%TO_DIR%

cd /d %~dp0
cd %FROM_DIR%


FOR %%F IN (*.wav) DO (
	sox %%F -n noiseprof noise.prof
	sox %%F -b 32 -e float -D %TO_PATH%%%F% --show-progress --multi-threaded vad reverse vad reverse norm -3 highpass 80 noisered noise.prof 0.3 norm -3
)


pause