#!/usr/bin/env python3

import os
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def generate_png_from_mermaid(input_file, output_file, width=800, height=600):
    """Generate a PNG image from a Mermaid diagram using Playwright."""
    
    # Read the Mermaid content
    with open(input_file, 'r') as f:
        mermaid_code = f.read()
    
    # Create an HTML file with the Mermaid diagram
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mermaid Diagram Renderer</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'default',
                securityLevel: 'loose'
            }});
        </script>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                background-color: white;
            }}
            #diagram {{
                width: {width}px; 
                margin: 0 auto;
            }}
        </style>
    </head>
    <body>
        <div id="diagram" class="mermaid">
{mermaid_code}
        </div>
    </body>
    </html>
    """
    
    # Create a temporary HTML file
    temp_html = "temp_diagram.html"
    with open(temp_html, "w") as f:
        f.write(html_content)
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": width, "height": height})
            
            # Navigate to the HTML file
            await page.goto(f"file://{os.path.abspath(temp_html)}")
            
            # Wait for Mermaid to render
            await page.wait_for_selector(".mermaid svg", state="visible", timeout=10000)
            
            # Wait a bit more to ensure complete rendering
            await asyncio.sleep(2)
            
            # Get the diagram element
            diagram = await page.query_selector("#diagram")
            
            # Take a screenshot of just the diagram
            await diagram.screenshot(path=output_file)
            
            await browser.close()
    finally:
        # Clean up the temporary HTML file
        if os.path.exists(temp_html):
            os.remove(temp_html)

async def main():
    # Create 'images' directory if it doesn't exist
    os.makedirs("images", exist_ok=True)
    
    # Get all .mmd files in the mermaid directory
    mermaid_dir = Path("mermaid")
    mermaid_files = list(mermaid_dir.glob("*.mmd"))
    
    print(f"Found {len(mermaid_files)} Mermaid diagram files")
    
    for mmd_file in mermaid_files:
        output_file = f"images/{mmd_file.stem}.png"
        print(f"Processing {mmd_file} -> {output_file}")
        
        try:
            await generate_png_from_mermaid(mmd_file, output_file)
            print(f"✅ Successfully generated {output_file}")
        except Exception as e:
            print(f"❌ Error generating {output_file}: {e}")
    
    print("All diagrams processed!")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main()) 