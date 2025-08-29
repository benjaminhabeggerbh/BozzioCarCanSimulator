# GitHub Actions Documentation Workflow

This directory contains GitHub Actions workflows for automatically building and releasing the Sphinx documentation.

## Workflow: `docs.yml`

### What it does:

1. **Builds Documentation**: 
   - Automatically builds Sphinx HTML and PDF documentation
   - Runs on every push to main branch and on pull requests
   - Can be triggered manually

2. **Deploys to GitHub Pages**:
   - Automatically deploys HTML documentation to GitHub Pages
   - Available at: `https://[username].github.io/[repository-name]/`

3. **Creates Releases**:
   - When you create a git tag (e.g., `v1.0.0`), it automatically:
     - Creates a GitHub release
     - Attaches HTML and PDF documentation as downloadable archives
     - Includes comprehensive release notes

### Setup Instructions:

1. **Enable GitHub Pages**:
   - Go to your repository Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `gh-pages` 
   - Folder: `/ (root)`

2. **Push the workflow**:
   ```bash
   git add .github/
   git commit -m "Add documentation build workflow"
   git push origin main
   ```

3. **Create a release**:
   ```bash
   # Create and push a tag
   git tag v1.0.0
   git push origin v1.0.0
   ```

### What happens after setup:

- **On every push to main**: Documentation builds and deploys to GitHub Pages
- **On tag creation**: Creates a release with downloadable documentation
- **Online documentation**: Available at your GitHub Pages URL
- **Release page**: Available at `https://github.com/[username]/[repository]/releases`

### Expected URLs after setup:

- **Live Documentation**: `https://[username].github.io/[repository-name]/`
- **Releases**: `https://github.com/[username]/[repository-name]/releases`
- **Latest Release**: `https://github.com/[username]/[repository-name]/releases/latest`