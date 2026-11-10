import Foundation
import PDFKit
import AppKit
let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1])
guard let doc = PDFDocument(url: url) else { fatalError("Invalid PDF") }
if args.count == 2 {
 for i in 0..<doc.pageCount { print("\n=== PAGE \(i+1) ===\n"+(doc.page(at:i)?.string ?? "")) }
} else {
 let page = doc.page(at:Int(args[2])!-1)!
 let bounds=page.bounds(for:.mediaBox)
 let scale=2.0
 let size=NSSize(width:bounds.width*scale,height:bounds.height*scale)
 let im=NSImage(size:size)
 im.lockFocus()
 NSColor.white.setFill(); NSRect(origin:.zero,size:size).fill()
 let ctx=NSGraphicsContext.current!.cgContext
 ctx.scaleBy(x:scale,y:scale)
 page.draw(with:.mediaBox,to:ctx)
 im.unlockFocus()
 let rep=NSBitmapImageRep(data:im.tiffRepresentation!)!
 try! rep.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:args[3]))
}
