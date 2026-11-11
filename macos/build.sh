#!/bin/zsh
# Bouwt "CURIOUS XXL.app" en zet hem in de map Programma's.
# Gebruik: zsh macos/build.sh   (vereist Xcode Command Line Tools)
set -e
D="${0:A:h}"
ROOT="${D:h}"
B="$D/build"
PAGE="$ROOT/web/curious-xxl.html"
PDF="$ROOT/docs/CURIOUS XXL - Handleiding.pdf"
# eigen logo's van de maker; ontbreken ze, dan gebruikt het script het kant-en-klare icoon uit assets/
LOGO="${CXXL_LOGO:-/Users/Han/Projecten/LOZ/RADIO CURIOUS/Logo Radio Curious.png}"
MARK="${CXXL_MARK:-/Users/Han/Projecten/hankoopman.nl/curious4ever-logo-transparant.png}"
if [[ -w /Applications ]]; then APPDIR=/Applications; else APPDIR="$HOME/Applications"; mkdir -p "$APPDIR"; fi
APP="$APPDIR/CURIOUS XXL.app"
OLD="$APPDIR/Playlist XXL.app"

rm -rf "$B"; mkdir -p "$B"

if [[ -f "$LOGO" && -f "$MARK" ]]; then
  swiftc -O -swift-version 5 "$D/icon.swift" -o "$B/icon" -framework Cocoa -framework CoreImage
  "$B/icon" "$LOGO" "$MARK" "$B/icon1024.png"
else
  cp "$ROOT/assets/icon.png" "$B/icon1024.png"
fi
mkdir -p "$B/AppIcon.iconset"
for s in 16 32 128 256 512; do
  sips -z $s $s "$B/icon1024.png" --out "$B/AppIcon.iconset/icon_${s}x${s}.png" >/dev/null
  sips -z $((s*2)) $((s*2)) "$B/icon1024.png" --out "$B/AppIcon.iconset/icon_${s}x${s}@2x.png" >/dev/null
done
iconutil -c icns "$B/AppIcon.iconset" -o "$B/AppIcon.icns"

swiftc -O -swift-version 5 "$D/main.swift" -o "$B/CURIOUS XXL" -framework Cocoa -framework WebKit -framework AVFoundation -framework PDFKit

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$B/CURIOUS XXL" "$APP/Contents/MacOS/CURIOUS XXL"
[[ -f "$PDF" ]] && cp "$PDF" "$APP/Contents/Resources/"
cp "$B/AppIcon.icns" "$APP/Contents/Resources/AppIcon.icns"
{
  print -r -- '<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;font:14px -apple-system,system-ui,sans-serif}[hidden]{display:none!important}img{max-width:100%}</style></head><body>'
  cat "$PAGE"
  print -r -- '</body></html>'
} > "$APP/Contents/Resources/index.html"
cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>CURIOUS XXL</string>
  <key>CFBundleDisplayName</key><string>CURIOUS XXL</string>
  <key>CFBundleIdentifier</key><string>nl.hankoopman.playlistxxl</string>
  <key>CFBundleExecutable</key><string>CURIOUS XXL</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.2</string>
  <key>CFBundleURLTypes</key><array><dict><key>CFBundleURLName</key><string>nl.hankoopman.curiousxxl.link</string><key>CFBundleURLSchemes</key><array><string>curiousxxl</string></array></dict></array>
  <key>CFBundleVersion</key><string>1</string>
  <key>LSMinimumSystemVersion</key><string>13.0</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>LSApplicationCategoryType</key><string>public.app-category.music</string>
  <key>NSHumanReadableCopyright</key><string>© 2026 Han Koopman · Radio Curious. Alle rechten voorbehouden. Niet verspreiden zonder toestemming.</string>
  <key>NSDesktopFolderUsageDescription</key><string>CURIOUS XXL kopieert de gekozen mp3's naar een map op je bureaublad.</string>
  <key>NSDocumentsFolderUsageDescription</key><string>CURIOUS XXL leest en bewaart back-ups.</string>
  <key>NSDownloadsFolderUsageDescription</key><string>CURIOUS XXL leest speellijsten en back-ups.</string>
</dict></plist>
PLIST
codesign --force --deep -s - "$APP" >/dev/null 2>&1 || true
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP" >/dev/null 2>&1 || true
touch "$APP"
if [[ -d "$OLD" ]]; then osascript -e "tell application \"Finder\" to delete (POSIX file \"$OLD\" as alias)" >/dev/null 2>&1 || true; fi
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -u "$OLD" >/dev/null 2>&1 || true
echo "KLAAR: $APP"
