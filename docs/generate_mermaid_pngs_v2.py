#!/usr/bin/env python3

import os
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def generate_png_from_mermaid(
    input_file, 
    output_file, 
    width=1600,  # Increased from 800
    height=1600, 
    device_scale_factor=2  # New parameter for higher DPI
):
    """Generate a high-resolution PNG from a Mermaid diagram."""
    
    with open(input_file, 'r') as f:
        mermaid_code = f.read()
    
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
    
    temp_html = "temp_diagram.html"
    with open(temp_html, "w") as f:
        f.write(html_content)
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            # Create context with increased resolution
            context = await browser.new_context(
                viewport={"width": width, "height": height},
                device_scale_factor=device_scale_factor  # Key change
            )
            page = await context.new_page()
            
            await page.goto(f"file://{os.path.abspath(temp_html)}")
            await page.wait_for_selector(".mermaid svg", state="visible", timeout=10000)
            await asyncio.sleep(2)  # Extra render time
            
            diagram = await page.query_selector("#diagram")
            await diagram.screenshot(path=output_file)
            
            await browser.close()
    finally:
        if os.path.exists(temp_html):
            os.remove(temp_html)

async def main():
    os.makedirs("images", exist_ok=True)
    mermaid_dir = Path("mermaid")
    
    for mmd_file in mermaid_dir.glob("*.mmd"):
        output_file = f"images/{mmd_file.stem}.png"
        print(f"Processing {mmd_file} -> {output_file}")
        
        try:
            # Generate high-res PNG with 2x scaling
            await generate_png_from_mermaid(
                mmd_file, 
                output_file, 
                width=1600,  # Larger dimensions
                height=1600,
                device_scale_factor=2  # Double the DPI
            )
            print(f"✅ Success: {output_file}")
        except Exception as e:
            print(f"❌ Failed: {output_file} - {e}")
    
    print("All diagrams processed!")

if __name__ == "__main__":
    asyncio.run(main())