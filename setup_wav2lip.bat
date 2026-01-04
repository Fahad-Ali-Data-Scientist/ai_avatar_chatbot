@echo off
echo ========================================
echo Wav2Lip Setup Script
echo ========================================
echo.

REM Check if git is available
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/3] Cloning Wav2Lip repository...
if exist "Wav2Lip" (
    echo Wav2Lip directory already exists. Skipping clone.
) else (
    git clone https://github.com/Rudrabha/Wav2Lip.git
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to clone Wav2Lip repository
        pause
        exit /b 1
    )
)

echo.
echo [2/3] Creating checkpoints directory...
if not exist "Wav2Lip\checkpoints" mkdir "Wav2Lip\checkpoints"

echo.
echo [3/3] Downloading model checkpoint...
echo This may take a few minutes (file size: ~440 MB)
echo.

REM Check if checkpoint already exists
if exist "Wav2Lip\checkpoints\wav2lip_gan.pth" (
    echo Model checkpoint already exists. Skipping download.
) else (
    REM Try with curl
    where curl >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo Downloading with curl...
        curl -L "https://huggingface.co/Nekochu/Wav2Lip/resolve/main/wav2lip_gan.pth" -o "Wav2Lip\checkpoints\wav2lip_gan.pth"
    ) else (
        REM Try with PowerShell
        echo Downloading with PowerShell...
        powershell -Command "Invoke-WebRequest -Uri 'https://huggingface.co/Nekochu/Wav2Lip/resolve/main/wav2lip_gan.pth' -OutFile 'Wav2Lip\checkpoints\wav2lip_gan.pth'"
    )
    
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to download model checkpoint
        echo Please download manually from:
        echo https://huggingface.co/Nekochu/Wav2Lip/resolve/main/wav2lip_gan.pth
        echo Save it to: Wav2Lip\checkpoints\wav2lip_gan.pth
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Verification:
if exist "Wav2Lip\inference.py" (
    echo [OK] Wav2Lip repository cloned
) else (
    echo [FAIL] Wav2Lip repository not found
)

if exist "Wav2Lip\checkpoints\wav2lip_gan.pth" (
    echo [OK] Model checkpoint downloaded
) else (
    echo [FAIL] Model checkpoint not found
)

echo.
echo You can now run the Jupyter notebook!
echo.
pause

