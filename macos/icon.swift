// Maakt het app-icoon: blauwe gloed uit het Radio Curious-logo, met het Curious4ever-woordmerk erop
import Cocoa
import CoreImage

let args = CommandLine.arguments
guard args.count >= 4,
      let bg = NSImage(contentsOfFile: args[1]),
      let mark = NSImage(contentsOfFile: args[2]) else { print("gebruik: icon achtergrond.png woordmerk.png uit.png"); exit(1) }

let S: CGFloat = 1024
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(S), pixelsHigh: Int(S), bitsPerSample: 8,
                           samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
                           bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)

let body = NSRect(x: 100, y: 100, width: 824, height: 824)
let shape = NSBezierPath(roundedRect: body, xRadius: 186, yRadius: 186)

NSGraphicsContext.saveGraphicsState()
let sh = NSShadow(); sh.shadowColor = NSColor.black.withAlphaComponent(0.35); sh.shadowBlurRadius = 24; sh.shadowOffset = NSSize(width: 0, height: -10)
sh.set(); NSColor(calibratedRed: 0.03, green: 0.07, blue: 0.22, alpha: 1).setFill(); shape.fill()
NSGraphicsContext.restoreGraphicsState()

NSGraphicsContext.saveGraphicsState()
shape.addClip()

if let tiff = bg.tiffRepresentation, let ci = CIImage(data: tiff) {
    let blurred = ci.clampedToExtent().applyingGaussianBlur(sigma: 18).cropped(to: ci.extent)
    let ctx = CIContext()
    if let cg = ctx.createCGImage(blurred, from: ci.extent) {
        let img = NSImage(cgImage: cg, size: NSSize(width: cg.width, height: cg.height))
        let scale = max(body.width / img.size.width, body.height / img.size.height) * 1.15
        let w = img.size.width * scale, h = img.size.height * scale
        img.draw(in: NSRect(x: body.midX - w / 2, y: body.midY - h / 2, width: w, height: h))
    }
}
let grad = NSGradient(colors: [NSColor.black.withAlphaComponent(0.05), NSColor.black.withAlphaComponent(0.45)])!
grad.draw(in: body, angle: -90)
let gloss = NSGradient(colors: [NSColor.white.withAlphaComponent(0.18), NSColor.white.withAlphaComponent(0)])!
gloss.draw(in: NSRect(x: body.minX, y: body.midY, width: body.width, height: body.height / 2), angle: -90)

let mw = body.width * 0.84
let mh = mark.size.height * (mw / mark.size.width)
let markRect = NSRect(x: body.midX - mw / 2, y: body.midY - mh / 2 + 40, width: mw, height: mh)
let ms = NSShadow(); ms.shadowColor = NSColor.black.withAlphaComponent(0.55); ms.shadowBlurRadius = 14; ms.shadowOffset = NSSize(width: 0, height: -4)
NSGraphicsContext.saveGraphicsState(); ms.set()
mark.draw(in: markRect, from: .zero, operation: .sourceOver, fraction: 1)
NSGraphicsContext.restoreGraphicsState()

let para = NSMutableParagraphStyle(); para.alignment = .center
let attrs: [NSAttributedString.Key: Any] = [
    .font: NSFont.systemFont(ofSize: 64, weight: .semibold),
    .foregroundColor: NSColor.white.withAlphaComponent(0.92),
    .kern: 14,
    .paragraphStyle: para
]
let xxl: [NSAttributedString.Key: Any] = [
    .font: NSFont.systemFont(ofSize: 150, weight: .heavy),
    .foregroundColor: NSColor(calibratedRed: 0.95, green: 0.62, blue: 0.30, alpha: 1),
    .kern: 10,
    .paragraphStyle: para
]
let xs = NSShadow(); xs.shadowColor = NSColor.black.withAlphaComponent(0.5); xs.shadowBlurRadius = 16; xs.shadowOffset = NSSize(width: 0, height: -5)
NSGraphicsContext.saveGraphicsState(); xs.set()
("XXL" as NSString).draw(in: NSRect(x: body.minX, y: body.minY + 110, width: body.width, height: 190), withAttributes: xxl)
NSGraphicsContext.restoreGraphicsState()
_ = attrs

NSGraphicsContext.restoreGraphicsState()
NSGraphicsContext.restoreGraphicsState()

let png = rep.representation(using: .png, properties: [:])!
try! png.write(to: URL(fileURLWithPath: args[3]))
print("icoon klaar")
