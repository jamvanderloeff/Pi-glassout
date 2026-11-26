<# :
@echo off
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-Expression ([System.IO.File]::ReadAllText('%~f0'))"
exit /b
#>


Write-Host "Setting up RPi config for Glassout viewer" -ForegroundColor Green

# Append video mode to config.txt
Add-Content -Path "cmdline.txt" -Value " video=DPI-1:640x480@60,reflect_x" -NoNewline

# Append composite to DRM driver line + enable_tvout=1
(Get-Content -Path "config.txt" -Raw) -replace "dtoverlay=vc4-kms-v3d", "dtoverlay=vc4-kms-v3d`ndtoverlay=vc4-kms-dpi-generic`ndtparam=hactive=640,hfp=10,hsync=20,hbp=30`ndtparam=vactive=480,vfp=3,vsync=5,vbp=12`ndtparam=clock-frequency=21000000`ndtparam=hsync-invert=1,vsync-invert=1`nenable_tvout=1`n" | Set-Content -Path "config.txt" -NoNewline

#replace user-config with template, grabbing only user/timezone/keymap
$template = (Get-Content -Path "user-data-template" -Raw)
$original = (Get-Content -Path "user-data" -Raw)

$section = $original -match "time[\s\S]+sudo: null"
#$Matches[0]  | Set-Content -Path "section" -NoNewline

$modified = $template -replace "time[\s\S]+sudo: null", $Matches[0]
$modified | Set-Content -Path "user-data" -NoNewline

# Add packages

# (Get-Content -Path "user-data" -Raw) -replace "- avahi-daemon", "- avahi-daemon`n- fontconfig`n- git`n- kmscube`n- libegl1`n- libgbm1`n- python3-pip`n- python3-jedi`n- python3-opengl`n- python3-pygame`n- python3-websockets"  | Set-Content -Path "user-data" -NoNewline

# Setup autologin

#(Get-Content -Path "user-data" -Raw).Replace("ssh_pwauth: true", "ssh_pwauth: true`nwrite_files:`n  - path: /etc/systemd/system/getty@tty1.service.d/autologin.conf`n    content: |`n      [Service]`n      ExecStart=`n      ExecStart=-/sbin/agetty --autologin cdu --noclear %I `$TERM")  | Set-Content -Path "user-data" -NoNewline

#(Get-Content -Path "user-data" -Raw).Replace("- [ systemctl, enable, --now, ssh ]", "- [ systemctl, enable, --now, ssh ]`n  - systemctl daemon-reload`n  - systemctl restart getty@tty1.service`n")  | Set-Content -Path "user-data" -NoNewline

# Hacky -- set time on first boot to time when config was edited so that initial update doesn't fail on signature verification before NTP is up


Read-Host -Prompt "Press Enter to exit"
