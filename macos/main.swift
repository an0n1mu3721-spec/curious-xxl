// CURIOUS XXL — Mac-app rond de catalogus van Radio Curious
import Cocoa
import WebKit
import AVFoundation
import PDFKit

let supportDir: URL = {
    let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
    let u = base.appendingPathComponent("CURIOUS XXL", isDirectory: true)
    let old = base.appendingPathComponent("Playlist XXL", isDirectory: true)
    // gegevens van de vorige naam meenemen
    if !FileManager.default.fileExists(atPath: u.path) && FileManager.default.fileExists(atPath: old.path) {
        try? FileManager.default.moveItem(at: old, to: u)
    }
    try? FileManager.default.createDirectory(at: u, withIntermediateDirectories: true)
    return u
}()
let storeURL = supportDir.appendingPathComponent("catalogus.json")
let busyURL = supportDir.appendingPathComponent("bezig.txt")
let skipURL = supportDir.appendingPathComponent("overslaan.txt")
// Een bestand dat bij de vorige keer de app liet stoppen, komt op de overslaanlijst
var skipList: Set<String> = {
    var set = Set((try? String(contentsOf: skipURL, encoding: .utf8))?.split(separator: "\n").map(String.init) ?? [])
    if let bad = try? String(contentsOf: busyURL, encoding: .utf8), !bad.isEmpty {
        set.insert(bad)
        try? set.joined(separator: "\n").write(to: skipURL, atomically: true, encoding: .utf8)
        try? FileManager.default.removeItem(at: busyURL)
    }
    return set
}()
let audioExts: Set<String> = ["mp3", "m4a", "aac", "wav", "flac", "aif", "aiff", "ogg"]

func expand(_ p: String) -> String { (p as NSString).expandingTildeInPath }

final class Bridge: NSObject, WKScriptMessageHandler, WKUIDelegate, WKNavigationDelegate {
    weak var web: WKWebView?
    var pageReady = false
    var pendingLinks: [String] = []

    func openLink(_ url: String) {
        guard pageReady, let web = web else { pendingLinks.append(url); return }
        let d = (try? JSONSerialization.data(withJSONObject: [url])).flatMap { String(data: $0, encoding: .utf8) } ?? "[\"\"]"
        web.evaluateJavaScript("window.__pxxlLink && window.__pxxlLink(\(d)[0])", completionHandler: nil)
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
            self.pageReady = true
            let todo = self.pendingLinks; self.pendingLinks = []
            todo.forEach { self.openLink($0) }
        }
    }

    func reply(_ id: Int, _ ok: Bool, _ value: Any?) {
        var js = "null"
        if let v = value, !(v is NSNull),
           let d = try? JSONSerialization.data(withJSONObject: [v], options: []),
           let s = String(data: d, encoding: .utf8) {
            js = String(s.dropFirst().dropLast())
        }
        DispatchQueue.main.async {
            self.web?.evaluateJavaScript("window.__pxxlReply(\(id),\(ok ? "true" : "false"),\(js))", completionHandler: nil)
        }
    }

    func userContentController(_ c: WKUserContentController, didReceive m: WKScriptMessage) {
        guard let body = m.body as? [String: Any],
              let id = (body["id"] as? NSNumber)?.intValue,
              let cmd = body["cmd"] as? String else { return }
        let args = body["args"] as? [String: Any] ?? [:]
        switch cmd {
        case "manual":
            DispatchQueue.main.async { (NSApp.delegate as? AppDelegate)?.openManual(); self.reply(id, true, true) }
        case "storeLoad":
            DispatchQueue.global().async { self.reply(id, true, try? String(contentsOf: storeURL, encoding: .utf8)) }
        case "storeSave":
            let s = args["data"] as? String ?? ""
            DispatchQueue.global().async {
                do {
                    try s.write(to: storeURL, atomically: true, encoding: .utf8)
                    let day = ISO8601DateFormatter.string(from: Date(), timeZone: .current, formatOptions: [.withFullDate])
                    let backup = supportDir.appendingPathComponent("reserve-\(day).json")
                    if !FileManager.default.fileExists(atPath: backup.path) { try? s.write(to: backup, atomically: true, encoding: .utf8) }
                    self.reply(id, true, true)
                } catch { self.reply(id, false, error.localizedDescription) }
            }
        case "chooseFolder":
            DispatchQueue.main.async {
                let p = NSOpenPanel()
                p.canChooseDirectories = true; p.canChooseFiles = false; p.allowsMultipleSelection = false
                p.message = "Kies je muziekmap"; p.prompt = "Koppel"
                p.directoryURL = URL(fileURLWithPath: expand(args["start"] as? String ?? "~/Music/MP3"))
                p.beginSheetModal(for: self.web!.window!) { r in
                    self.reply(id, true, r == .OK ? p.url?.path : nil)
                }
            }
        case "scan":
            let root = URL(fileURLWithPath: expand(args["root"] as? String ?? "~/Music/MP3")).standardizedFileURL
            DispatchQueue.global(qos: .userInitiated).async {
                let fm = FileManager.default
                guard fm.isReadableFile(atPath: root.path) else { self.reply(id, false, "geen toegang"); return }
                var out: [[String: String]] = []
                let base = root.path.hasSuffix("/") ? root.path : root.path + "/"
                if let en = fm.enumerator(at: root, includingPropertiesForKeys: [.isRegularFileKey], options: [.skipsHiddenFiles]) {
                    for case let u as URL in en where audioExts.contains(u.pathExtension.lowercased()) {
                        let p = u.standardizedFileURL.path
                        let rel = p.hasPrefix(base) ? String(p.dropFirst(base.count)) : u.lastPathComponent
                        out.append(["rel": rel, "path": p])
                    }
                }
                self.reply(id, true, out)
            }
        case "tags":
            let paths = args["paths"] as? [String] ?? []
            DispatchQueue.global(qos: .utility).async {
                let out: [Any] = paths.map { p in
                    if skipList.contains(p) { return [String: Any]() }
                    try? p.write(to: busyURL, atomically: true, encoding: .utf8)
                    let r: [String: Any] = autoreleasepool { readTags(p) ?? [:] }
                    try? FileManager.default.removeItem(at: busyURL)
                    return r
                }
                self.reply(id, true, out)
            }
        case "copyToDesktop":
            let folder = (args["folder"] as? String ?? "Playlist XXL").replacingOccurrences(of: "/", with: "-")
            let files = args["files"] as? [[String: String]] ?? []
            let extra = args["extra"] as? [[String: String]] ?? []
            DispatchQueue.global(qos: .userInitiated).async {
                let fm = FileManager.default
                let desk = fm.urls(for: .desktopDirectory, in: .userDomainMask)[0]
                var dest = desk.appendingPathComponent(folder); var k = 2
                while fm.fileExists(atPath: dest.path) { dest = desk.appendingPathComponent("\(folder) (\(k))"); k += 1 }
                do {
                    try fm.createDirectory(at: dest, withIntermediateDirectories: true)
                    for f in files {
                        guard let src = f["src"], let name = f["name"] else { continue }
                        try fm.copyItem(at: URL(fileURLWithPath: src), to: dest.appendingPathComponent(name))
                    }
                    for e in extra {
                        guard let name = e["name"], let text = e["text"] else { continue }
                        try text.write(to: dest.appendingPathComponent(name), atomically: true, encoding: .utf8)
                    }
                    DispatchQueue.main.async { NSWorkspace.shared.activateFileViewerSelecting([dest]) }
                    self.reply(id, true, dest.lastPathComponent)
                } catch { self.reply(id, false, error.localizedDescription) }
            }
        case "saveFile":
            let name = args["name"] as? String ?? "playlist-xxl.txt"
            let text = args["text"] as? String ?? ""
            DispatchQueue.main.async {
                let p = NSSavePanel()
                p.nameFieldStringValue = name
                p.directoryURL = FileManager.default.urls(for: .desktopDirectory, in: .userDomainMask)[0]
                p.beginSheetModal(for: self.web!.window!) { r in
                    guard r == .OK, let u = p.url else { self.reply(id, true, false); return }
                    do { try text.write(to: u, atomically: true, encoding: .utf8); self.reply(id, true, true) }
                    catch { self.reply(id, false, error.localizedDescription) }
                }
            }
        case "claude":
            let prompt = args["prompt"] as? String ?? ""
            DispatchQueue.global(qos: .utility).async {
                let p = Process()
                p.executableURL = URL(fileURLWithPath: "/bin/zsh")
                p.arguments = ["-lc", "claude -p \"$PXXL_PROMPT\" --output-format text"]
                var env = ProcessInfo.processInfo.environment
                env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:\(NSHomeDirectory())/.local/bin:/usr/bin:/bin:" + (env["PATH"] ?? "")
                env["PXXL_PROMPT"] = prompt
                p.environment = env
                let out = Pipe(), err = Pipe()
                p.standardOutput = out; p.standardError = err
                p.standardInput = FileHandle.nullDevice
                do {
                    try p.run()
                    let data = out.fileHandleForReading.readDataToEndOfFile()
                    let edata = err.fileHandleForReading.readDataToEndOfFile()
                    p.waitUntilExit()
                    if p.terminationStatus == 0 { self.reply(id, true, String(data: data, encoding: .utf8) ?? "") }
                    else { self.reply(id, false, String(data: edata, encoding: .utf8) ?? "claude gaf een fout") }
                } catch { self.reply(id, false, error.localizedDescription) }
            }
        default:
            reply(id, false, "onbekende opdracht")
        }
    }

    func webView(_ webView: WKWebView, runOpenPanelWith parameters: WKOpenPanelParameters,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping ([URL]?) -> Void) {
        let p = NSOpenPanel()
        p.allowsMultipleSelection = parameters.allowsMultipleSelection
        p.canChooseFiles = true; p.canChooseDirectories = false
        p.beginSheetModal(for: webView.window!) { r in completionHandler(r == .OK ? p.urls : nil) }
    }

    func webView(_ webView: WKWebView, decidePolicyFor a: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        if a.navigationType == .linkActivated, let u = a.request.url, (u.scheme ?? "").hasPrefix("http") {
            NSWorkspace.shared.open(u); decisionHandler(.cancel); return
        }
        decisionHandler(.allow)
    }
}

func readTags(_ path: String) -> [String: Any]? {
    let a = AVURLAsset(url: URL(fileURLWithPath: path))
    var d: [String: Any] = [:]
    let dur = CMTimeGetSeconds(a.duration)
    if dur.isFinite && dur > 0 && dur < 86400 { d["dur"] = dur }
    for item in a.commonMetadata {
        guard let key = item.commonKey?.rawValue, let s = item.stringValue, !s.isEmpty else { continue }
        switch key {
        case "title": d["title"] = s
        case "artist": d["artist"] = s
        case "creationDate": if let y = Int(s.prefix(4)), y > 1000, y < 2100 { d["year"] = y }
        case "type": d["genre"] = s
        default: break
        }
    }
    for fmt in a.availableMetadataFormats {
        for item in a.metadata(forFormat: fmt) {
            let ident = item.identifier?.rawValue ?? ""
            let k = String(ident.split(separator: "/").last ?? "").uppercased()
            guard let s = item.stringValue, !s.isEmpty else { continue }
            if d["year"] == nil, ["TYER", "TDRC", "TDOR", "TYE", "%A9DAY"].contains(k), let y = Int(s.prefix(4)), y > 1000, y < 2100 { d["year"] = y }
            if d["genre"] == nil, ["TCON", "TCO", "%A9GEN"].contains(k) { d["genre"] = s }
            if d["bpm"] == nil, ["TBPM", "TBP", "TMPO"].contains(k),
               let b = Double(s.trimmingCharacters(in: .whitespaces)), b.isFinite, b > 20, b < 400 { d["bpm"] = Int(b.rounded()) }
            if d["key"] == nil, ["TKEY", "TKE", "KEY", "INITIALKEY"].contains(k), s.count <= 8 { d["key"] = s.trimmingCharacters(in: .whitespaces) }
            if d["title"] == nil, ["TIT2", "TT2"].contains(k) { d["title"] = s }
            if d["artist"] == nil, ["TPE1", "TP1"].contains(k) { d["artist"] = s }
        }
    }
    return d
}

final class AppDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate {
    var window: NSWindow!
    let bridge = Bridge()

    func applicationDidFinishLaunching(_ n: Notification) {
        buildMenu()
        let cfg = WKWebViewConfiguration()
        cfg.userContentController.add(bridge, name: "pxxl")
        cfg.mediaTypesRequiringUserActionForPlayback = []
        cfg.preferences.setValue(true, forKey: "allowFileAccessFromFileURLs")
        cfg.preferences.setValue(true, forKey: "developerExtrasEnabled")
        let web = WKWebView(frame: .zero, configuration: cfg)
        web.uiDelegate = bridge; web.navigationDelegate = bridge
        bridge.web = web

        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1440, height: 920),
                          styleMask: [.titled, .closable, .miniaturizable, .resizable],
                          backing: .buffered, defer: false)
        window.title = "CURIOUS XXL"
        window.minSize = NSSize(width: 900, height: 600)
        window.contentView = web
        window.delegate = self
        window.setFrameAutosaveName("PlaylistXXLHoofdvenster")
        window.center()
        window.makeKeyAndOrderFront(nil)

        if let page = Bundle.main.url(forResource: "index", withExtension: "html") {
            web.loadFileURL(page, allowingReadAccessTo: URL(fileURLWithPath: "/"))
        }
        NSApp.activate(ignoringOtherApps: true)
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ s: NSApplication) -> Bool { true }

    func buildMenu() {
        let main = NSMenu()
        let appItem = NSMenuItem(); main.addItem(appItem)
        let appMenu = NSMenu()
        appMenu.addItem(withTitle: "Over CURIOUS XXL", action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)), keyEquivalent: "")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Verberg CURIOUS XXL", action: #selector(NSApplication.hide(_:)), keyEquivalent: "h")
        appMenu.addItem(withTitle: "Stop CURIOUS XXL", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        appItem.submenu = appMenu

        let editItem = NSMenuItem(); main.addItem(editItem)
        let edit = NSMenu(title: "Wijzig")
        edit.addItem(withTitle: "Herstel", action: Selector(("undo:")), keyEquivalent: "z")
        edit.addItem(withTitle: "Opnieuw", action: Selector(("redo:")), keyEquivalent: "Z")
        edit.addItem(.separator())
        edit.addItem(withTitle: "Knip", action: #selector(NSText.cut(_:)), keyEquivalent: "x")
        edit.addItem(withTitle: "Kopieer", action: #selector(NSText.copy(_:)), keyEquivalent: "c")
        edit.addItem(withTitle: "Plak", action: #selector(NSText.paste(_:)), keyEquivalent: "v")
        edit.addItem(withTitle: "Selecteer alles", action: #selector(NSText.selectAll(_:)), keyEquivalent: "a")
        editItem.submenu = edit

        let viewItem = NSMenuItem(); main.addItem(viewItem)
        let view = NSMenu(title: "Weergave")
        view.addItem(withTitle: "Ververs", action: #selector(reloadPage), keyEquivalent: "r")
        view.addItem(withTitle: "Toon catalogusmap", action: #selector(showData), keyEquivalent: "")
        viewItem.submenu = view

        let winItem = NSMenuItem(); main.addItem(winItem)
        let win = NSMenu(title: "Venster")
        win.addItem(withTitle: "Minimaliseer", action: #selector(NSWindow.performMiniaturize(_:)), keyEquivalent: "m")
        win.addItem(withTitle: "Zoom", action: #selector(NSWindow.performZoom(_:)), keyEquivalent: "")
        winItem.submenu = win

        let helpItem = NSMenuItem(); main.addItem(helpItem)
        let help = NSMenu(title: "Help")
        help.addItem(withTitle: "Handleiding CURIOUS XXL", action: #selector(openManual), keyEquivalent: "?")
        helpItem.submenu = help
        NSApp.mainMenu = main
    }

    @objc func reloadPage() { bridge.pageReady = false; bridge.web?.reload() }
    var manualWindow: NSWindow?
    let manualLinks = ManualLinks()
    @objc func openManual() {
        if let w = manualWindow { w.makeKeyAndOrderFront(nil); NSApp.activate(ignoringOtherApps: true); return }
        guard let url = Bundle.main.url(forResource: "CURIOUS XXL - Handleiding", withExtension: "pdf"),
              let doc = PDFDocument(url: url) else { return }
        let pv = PDFView()
        pv.document = doc; pv.autoScales = true; pv.displayMode = .singlePageContinuous
        pv.backgroundColor = NSColor(calibratedRed: 0.06, green: 0.08, blue: 0.11, alpha: 1)
        manualLinks.app = self
        pv.delegate = manualLinks
        let f = window.frame
        let w = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 760, height: max(700, f.height)),
                         styleMask: [.titled, .closable, .miniaturizable, .resizable], backing: .buffered, defer: false)
        w.title = "CURIOUS XXL · Handleiding"
        w.contentView = pv
        w.isReleasedWhenClosed = false
        if !w.setFrameUsingName("CuriousXXLHandleiding") { w.setFrameOrigin(NSPoint(x: max(0, f.minX - 380), y: f.minY)) }
        w.setFrameAutosaveName("CuriousXXLHandleiding")
        manualWindow = w
        w.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }
    func followLink(_ url: URL) {
        if url.scheme?.lowercased() == "curiousxxl" {
            window?.orderFront(nil)
            bridge.openLink(url.absoluteString)
        } else {
            NSWorkspace.shared.open(url)
        }
    }

    // links als curiousxxl://ga/uur uit de handleiding
    func applicationWillFinishLaunching(_ n: Notification) {
        NSAppleEventManager.shared().setEventHandler(self, andSelector: #selector(handleURL(_:reply:)),
            forEventClass: AEEventClass(kInternetEventClass), andEventID: AEEventID(kAEGetURL))
    }
    @objc func handleURL(_ event: NSAppleEventDescriptor, reply: NSAppleEventDescriptor) {
        guard let s = event.paramDescriptor(forKeyword: keyDirectObject)?.stringValue else { return }
        window?.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        bridge.openLink(s)
    }
    @objc func showData() { NSWorkspace.shared.activateFileViewerSelecting([storeURL]) }
}

final class ManualLinks: NSObject, PDFViewDelegate {
    weak var app: AppDelegate?
    func pdfViewWillClick(onLink sender: PDFView, with url: URL) { app?.followLink(url) }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.regular)
app.run()
