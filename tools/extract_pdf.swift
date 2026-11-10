import Foundation
import PDFKit
import AppKit
let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1])
guard let doc = PDFDocument(url: url) else { fatalError("PDF open failed") }
if args.count == 2 {
 for n in 0..<doc.pageCount { print("\n=== PDF PAGE \(n+1) ===\n"); print(doc.page(at:n)?.string ?? "") }
} else {
 let n=Int(args[2])!-1
 guard let page=doc.page(at:n) else {fatalError("bad page")}
 let r=page.bounds(for:.mediaBox)
 let img=page.thumbnail(of: NSSize(width:r.width*2,height:r.height*2),for:.mediaBox)
 let bitmap=NSBitmapImageRep(data:img.tiffRepresentation!)!
 try bitmap.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:args[3]))
}
