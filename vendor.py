#!/usr/bin/env python3
"""
Tantra Vendoring Helper

Helps you copy Tantra's code into your project for full control.
"""
import argparse
import shutil
import sys
from pathlib import Path


def vendor_tantra(target_dir: str, include_examples: bool = False):
    """
    Copy Tantra source code into target directory.
    
    Args:
        target_dir: Destination directory (e.g., 'myproject/agents')
        include_examples: Whether to copy examples/ folder
    """
    # Find Tantra's location
    try:
        import tantra
        tantra_path = Path(tantra.__file__).parent
    except ImportError:
        print("❌ Tantra not found. Install first: pip install tantra")
        sys.exit(1)
    
    target = Path(target_dir)
    
    # Check if target exists
    if target.exists():
        response = input(f"⚠️  {target} already exists. Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
        shutil.rmtree(target)
    
    # Create target directory
    target.mkdir(parents=True, exist_ok=True)
    
    # Copy core files
    print(f"📦 Copying Tantra core to {target}/")
    
    core_files = [
        '__init__.py',
        'agent.py',
        'providers.py',
        'types.py',
        'tools.py',
        'utils.py'
    ]
    
    for file in core_files:
        src = tantra_path / file
        if src.exists():
            shutil.copy2(src, target / file)
            print(f"   ✓ {file}")
    
    # Copy examples if requested
    if include_examples:
        examples_src = tantra_path.parent / 'examples'
        if examples_src.exists():
            examples_dst = target / 'examples'
            shutil.copytree(examples_src, examples_dst)
            print(f"   ✓ examples/")
    
    # Create a vendoring note
    vendor_note = target / 'VENDORED.md'
    with open(vendor_note, 'w') as f:
        f.write(f"""# Vendored from Tantra

This code was vendored from Tantra v{tantra.__version__ if hasattr(tantra, '__version__') else 'unknown'}

- **Vendored on**: {Path.cwd()}
- **Source**: https://github.com/axlnet/tantra
- **Original license**: MIT

## What This Means

This code is now YOURS. Modify it freely for your needs.

- ✅ Customize behavior
- ✅ Add features
- ✅ Optimize performance
- ✅ Change anything

## Staying Updated

Check https://github.com/axlnet/tantra occasionally for:
- Bug fixes
- New features
- Performance improvements

You decide what to adopt!

## Your Customizations

Document your changes below:

---

(Add notes about your modifications here)
""")
    print(f"   ✓ VENDORED.md")
    
    print("\n✅ Vendoring complete!")
    print(f"\n📝 Next steps:")
    print(f"   1. Only dependency: pip install openai")
    print(f"   2. Import from: from {target.name} import Agent")
    print(f"   3. Modify code in {target}/ as needed")
    print(f"   4. Document changes in {target}/VENDORED.md")
    print(f"\n💡 See VENDORING.md for customization ideas!")


def main():
    parser = argparse.ArgumentParser(
        description="Vendor Tantra's source code into your project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Vendor core into myproject/agents/
  python vendor.py myproject/agents/
  
  # Include examples
  python vendor.py myproject/agents/ --examples
  
  # Different location
  python vendor.py lib/ai/tantra/
        """
    )
    
    parser.add_argument(
        'target',
        help='Target directory (e.g., myproject/agents/)'
    )
    
    parser.add_argument(
        '--examples',
        action='store_true',
        help='Also copy examples/ folder'
    )
    
    args = parser.parse_args()
    
    vendor_tantra(args.target, args.examples)


if __name__ == '__main__':
    main()
