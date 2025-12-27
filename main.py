#!/usr/bin/env python3
"""
Resume Builder - GUI Launcher
Usage: python main.py
"""
import sys
import os

def main():
    """Launch the Resume Builder GUI"""
    try:
        # Check if input directory exists
        if not os.path.exists("input"):
            print("📁 Creating input directory...")
            os.makedirs("input", exist_ok=True)
            print("✅ Created: input/")
            print("💡 Please extract your DOCX template to: input/template1/")
        
        # Launch GUI
        print("🚀 Launching Resume Builder GUI...")
        from gui import ResumeBuilderGUI
        app = ResumeBuilderGUI()
        app.run()
        
        return 0
        
    except ImportError as e:
        print(f"❌ Missing required files: {e}")
        print("\n💡 Make sure these files exist:")
        print("   • gui.py")
        print("   • processor.py")
        print("   • parser.py")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())