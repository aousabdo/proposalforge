import os
import glob
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# Create images directory if it doesn't exist
os.makedirs('images', exist_ok=True)

# HTML template for rendering Mermaid diagrams
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; }}
        .mermaid {{ background: white; }}
    </style>
</head>
<body>
    <div class="mermaid" style="width: 100%;">
        {mermaid_code}
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</body>
</html>
"""

async def generate_diagram_image(playwright, mermaid_file, output_file):
    """Generate a PNG image from a Mermaid diagram file."""
    # Read the Mermaid code from the file
    with open(mermaid_file, 'r') as f:
        mermaid_code = f.read().strip()
    
    # Create a temporary HTML file with the Mermaid diagram
    html_content = HTML_TEMPLATE.format(mermaid_code=mermaid_code)
    temp_html = Path(f"{mermaid_file}.html")
    temp_html.write_text(html_content)

    # Launch a browser to render the diagram
    browser = await playwright.chromium.launch()
    page = await browser.new_page(viewport={"width": 1200, "height": 800})
    
    try:
        # Navigate to the HTML file and wait for Mermaid to render
        await page.goto(f"file://{temp_html.absolute()}")
        await page.wait_for_selector(".mermaid svg")
        
        # Determine the size of the SVG
        svg_dimensions = await page.evaluate("""() => {
            const svg = document.querySelector('.mermaid svg');
            return { width: svg.getBoundingClientRect().width, height: svg.getBoundingClientRect().height };
        }""")
        
        # Set viewport to match SVG size
        await page.set_viewport_size({
            "width": int(svg_dimensions["width"]) + 40,
            "height": int(svg_dimensions["height"]) + 40
        })
        
        # Take screenshot of the SVG
        mermaid_element = await page.query_selector(".mermaid")
        await mermaid_element.screenshot(path=output_file)
        
        print(f"Generated {output_file}")
    except Exception as e:
        print(f"Error generating {output_file}: {e}")
    finally:
        await browser.close()
        # Clean up temporary HTML file
        temp_html.unlink()

async def main():
    # Get all Mermaid diagram files
    mermaid_files = glob.glob('mermaid_diagrams/diagram_*.mmd')
    
    async with async_playwright() as playwright:
        # Process each diagram file
        for mermaid_file in mermaid_files:
            diagram_num = os.path.basename(mermaid_file).split('_')[1].split('.')[0]
            output_file = f"images/diagram_{diagram_num}.png"
            
            print(f"Processing diagram {diagram_num}...")
            await generate_diagram_image(playwright, mermaid_file, output_file)
    
    print("\nAll diagrams have been generated!")
    print("You can now use the 'system-architecture.md.new' file which references these images.")

# Run the async program
asyncio.run(main()) 