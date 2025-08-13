# ESP32 CAN Bus Vehicle Controller Documentation

This directory contains the comprehensive Sphinx documentation for the ESP32 CAN Bus Vehicle Controller project.

## Documentation Contents

- **Getting Started**: Quick setup and installation guide
- **Hardware Setup**: Detailed hardware requirements and wiring instructions
- **Software Architecture**: System design and component relationships
- **API Reference**: Complete class and function documentation
- **Vehicle Support**: Supported vehicles and CAN protocols
- **Configuration**: Build-time and runtime configuration options
- **Build & Deployment**: Development environment setup and deployment guide
- **Troubleshooting**: Common issues and solutions

## Building the Documentation

### Prerequisites

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Or install Sphinx manually:

```bash
pip install sphinx sphinx-rtd-theme
```

### Build Commands

**HTML Documentation:**
```bash
# Linux/macOS
make html

# Windows
make.bat html
```

**PDF Documentation (requires LaTeX):**
```bash
# Linux/macOS
make latexpdf

# Windows
make.bat latexpdf
```

**Other Formats:**
```bash
# Available formats
make help

# Common formats
make epub     # EPUB format
make singlehtml  # Single HTML file
make dirhtml  # HTML with directory structure
```

### Viewing the Documentation

After building, open the documentation in your browser:

```bash
# Open HTML documentation
open _build/html/index.html        # macOS
xdg-open _build/html/index.html    # Linux
start _build/html/index.html       # Windows
```

## Development

### Live Rebuild (Development)

For automatic rebuilding during development:

```bash
pip install sphinx-autobuild
sphinx-autobuild . _build/html
```

This will start a local web server and automatically rebuild when files change.

### Documentation Structure

```
docs/
├── conf.py                 # Sphinx configuration
├── index.rst              # Main documentation index
├── getting_started.rst    # Quick start guide
├── hardware_setup.rst     # Hardware documentation
├── software_architecture.rst  # System architecture
├── api_reference.rst      # API documentation
├── vehicle_support.rst    # Vehicle compatibility
├── configuration.rst      # Configuration options
├── build_deployment.rst   # Build and deployment
├── troubleshooting.rst    # Troubleshooting guide
├── requirements.txt       # Python dependencies
├── Makefile               # Build automation (Unix)
├── make.bat              # Build automation (Windows)
├── _static/              # Static assets
└── _build/               # Generated documentation
```

### Adding New Documentation

1. Create new `.rst` files in the `docs/` directory
2. Add them to the `toctree` in `index.rst`
3. Use reStructuredText format for consistency
4. Include code examples and diagrams where helpful

### Documentation Standards

- Use clear, concise language
- Include practical examples
- Provide troubleshooting information
- Keep code examples up to date
- Use consistent formatting and structure

## Publishing

### GitHub Pages

To publish to GitHub Pages:

1. Build HTML documentation: `make html`
2. Copy `_build/html/*` to your gh-pages branch
3. Push to GitHub

### Read the Docs

For automatic building and hosting:

1. Connect your repository to Read the Docs
2. Configure the build settings
3. Documentation will auto-update on commits

## Contributing

When contributing to documentation:

1. Follow the existing structure and style
2. Test your changes by building locally
3. Ensure all links and references work
4. Update the table of contents if adding new sections
5. Include screenshots or diagrams for complex procedures

## Support

For documentation issues:

1. Check the troubleshooting section
2. Verify Sphinx installation and dependencies
3. Ensure all required files are present
4. Check for syntax errors in reStructuredText files

For questions about the ESP32 CAN Bus Vehicle Controller itself, refer to the main project documentation.