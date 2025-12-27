#!/usr/bin/env python3
"""
Simple DOCX to PDF Converter
Uses LibreOffice (cross-platform) for best compatibility
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def convert_docx_to_pdf(docx_path, pdf_path=None):
    """
    Convert DOCX to PDF using LibreOffice (recommended) or fallback methods
    
    Args:
        docx_path: Path to input DOCX file
        pdf_path: Optional output PDF path (default: same name as DOCX with .pdf)
    
    Returns:
        Path to created PDF file, or None if failed
    """
    # Validate input file
    docx_path = Path(docx_path)
    if not docx_path.exists():
        print(f"❌ DOCX file not found: {docx_path}")
        return None
    
    # Set default PDF path if not provided
    if pdf_path is None:
        pdf_path = docx_path.with_suffix('.pdf')
    else:
        pdf_path = Path(pdf_path)
    
    print(f"📄 Converting: {docx_path.name}")
    print(f"📄 Output PDF: {pdf_path.name}")
    
    # Try methods in order of reliability
    conversion_methods = [
        _convert_with_libreoffice,
        _convert_with_pypandoc,
        _convert_with_docx2pdf,
    ]
    
    for method in conversion_methods:
        result = method(docx_path, pdf_path)
        if result:
            return result
    
    for method in conversion_methods:
        result = method(docx_path, pdf_path)
        if result:
            return result
        
    for method in conversion_methods:
        result = method(docx_path, pdf_path)
        if result:
            return result
    
    print("❌ All conversion methods failed")
    return None

def _convert_with_libreoffice(docx_path, pdf_path):
    """
    Method 1: Use LibreOffice (most reliable, cross-platform)
    Requires: LibreOffice installed
    """
    print("  Trying LibreOffice conversion...")
    
    # Check if LibreOffice is available
    libreoffice_cmd = None
    if sys.platform == "win32":
        # Windows paths
        possible_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                libreoffice_cmd = path
                break
    else:
        # Linux/Mac - check if soffice is in PATH
        if subprocess.run(["which", "soffice"], capture_output=True).returncode == 0:
            libreoffice_cmd = "soffice"
    
    if not libreoffice_cmd:
        print("  ⚠ LibreOffice not found")
        return None
    
    try:
        # Create output directory if needed
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build conversion command
        cmd = [
            libreoffice_cmd,
            "--headless",  # Run without GUI
            "--convert-to", "pdf",
            "--outdir", str(pdf_path.parent),
            str(docx_path)
        ]
        
        print(f"  Running: {' '.join(cmd)}")
        
        # Run conversion
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        if result.returncode == 0:
            # Check if PDF was created
            if pdf_path.exists():
                file_size = pdf_path.stat().st_size / 1024
                print(f"  ✅ LibreOffice success: {file_size:.1f} KB")
                return str(pdf_path)
            else:
                # LibreOffice might name file differently
                alt_pdf = docx_path.with_suffix('.pdf')
                if alt_pdf.exists():
                    alt_pdf.rename(pdf_path)
                    print(f"  ✅ LibreOffice success (renamed)")
                    return str(pdf_path)
        else:
            print(f"  ❌ LibreOffice failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("  ❌ LibreOffice timeout")
    except Exception as e:
        print(f"  ❌ LibreOffice error: {e}")
    
    return None

def _convert_with_pypandoc(docx_path, pdf_path):
    """
    Method 2: Use PyPandoc (requires pandoc + LaTeX)
    """
    print("  Trying PyPandoc conversion...")
    
    try:
        import pypandoc
        
        # Create output directory
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert using pandoc
        output = pypandoc.convert_file(
            str(docx_path),
            'pdf',
            outputfile=str(pdf_path),
            extra_args=['--pdf-engine=xelatex']
        )
        
        if pdf_path.exists():
            file_size = pdf_path.stat().st_size / 1024
            print(f"  ✅ PyPandoc success: {file_size:.1f} KB")
            return str(pdf_path)
            
    except ImportError:
        print("  ⚠ PyPandoc not installed (pip install pypandoc)")
    except Exception as e:
        print(f"  ❌ PyPandoc error: {e}")
    
    return None

def _convert_with_docx2pdf(docx_path, pdf_path):
    """
    Method 3: Use docx2pdf library (Windows-only, requires Word)
    """
    print("  Trying docx2pdf conversion...")
    
    try:
        from docx2pdf import convert
        
        # Create output directory
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert
        convert(str(docx_path), str(pdf_path))
        
        if pdf_path.exists():
            file_size = pdf_path.stat().st_size / 1024
            print(f"  ✅ docx2pdf success: {file_size:.1f} KB")
            return str(pdf_path)
            
    except ImportError:
        print("  ⚠ docx2pdf not installed (pip install docx2pdf)")
    except Exception as e:
        print(f"  ❌ docx2pdf error: {e}")
    
    return None

def batch_convert_folder(folder_path, output_folder=None):
    """
    Convert all DOCX files in a folder to PDF
    """
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"❌ Folder not found: {folder_path}")
        return []
    
    # Get all DOCX files
    docx_files = list(folder_path.glob("*.docx"))
    
    if not docx_files:
        print(f"ℹ️ No DOCX files found in {folder_path}")
        return []
    
    print(f"🔍 Found {len(docx_files)} DOCX files to convert")
    
    # Set output folder
    if output_folder is None:
        output_folder = folder_path / "pdf_output"
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Convert each file
    successful = []
    for docx_file in docx_files:
        print(f"\n--- Converting {docx_file.name} ---")
        pdf_path = output_folder / docx_file.with_suffix('.pdf').name
        result = convert_docx_to_pdf(docx_file, pdf_path)
        if result:
            successful.append(result)
    
    print(f"\n🎉 Conversion complete: {len(successful)}/{len(docx_files)} successful")
    return successful

def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert DOCX to PDF')
    parser.add_argument('input', help='Input DOCX file or folder')
    parser.add_argument('-o', '--output', help='Output PDF file or folder')
    parser.add_argument('-b', '--batch', action='store_true', 
                       help='Batch convert all DOCX files in folder')
    
    args = parser.parse_args()
    
    if args.batch:
        # Batch convert folder
        results = batch_convert_folder(args.input, args.output)
        if results:
            print("\n✅ Converted files:")
            for pdf in results:
                print(f"  • {Path(pdf).name}")
    else:
        # Single file conversion
        result = convert_docx_to_pdf(args.input, args.output)
        if result:
            print(f"\n✅ Successfully converted to: {result}")
        else:
            print("\n❌ Conversion failed")
            sys.exit(1)

if __name__ == "__main__":
    main()