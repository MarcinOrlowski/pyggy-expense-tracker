import os
import markdown
from django.shortcuts import render
from django.conf import settings


def help_index(request):
    """Display README.md if exists, otherwise list of available documentation files."""
    docs_dir = os.path.join(settings.BASE_DIR, 'docs')
    
    if not os.path.exists(docs_dir):
        return render(request, 'expenses/help_index.html', {
            'docs': [],
            'error': 'Documentation directory not found.'
        })
    
    # Check if user wants to see file listing explicitly
    force_list = request.GET.get('list') == '1'
    
    # Check if README.md exists and render it directly (unless list is forced)
    readme_path = os.path.join(docs_dir, 'README.md')
    if not force_list and os.path.exists(readme_path) and os.path.isfile(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert markdown to HTML
            md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
            html_content = md.convert(content)
            
            # Extract title from first h1 or use default
            title = 'Documentation'
            if content.startswith('# '):
                first_line = content.split('\n')[0]
                title = first_line[2:].strip()
            
            return render(request, 'expenses/help_page.html', {
                'title': title,
                'content': html_content,
                'page_name': 'README',
                'is_readme': True
            })
            
        except (OSError, UnicodeDecodeError) as e:
            # Fall through to show file listing with error
            pass
    
    # No README.md found or error reading it, show file listing
    docs = []
    try:
        for filename in os.listdir(docs_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(docs_dir, filename)
                if os.path.isfile(filepath):
                    # Extract title from filename or first line of file
                    title = filename[:-3].replace('_', ' ').replace('-', ' ').title()
                    docs.append({
                        'filename': filename,
                        'title': title,
                        'url_name': filename[:-3].lower()
                    })
        
        # Sort docs alphabetically by title, but put README first if exists
        docs.sort(key=lambda x: (x['filename'].lower() != 'readme.md', x['title']))
        
    except OSError as e:
        return render(request, 'expenses/help_index.html', {
            'docs': [],
            'error': f'Error reading documentation directory: {e}'
        })
    
    return render(request, 'expenses/help_index.html', {'docs': docs})


def help_page(request, page_name):
    """Display a specific documentation page."""
    docs_dir = os.path.join(settings.BASE_DIR, 'docs')
    file_path = os.path.join(docs_dir, f'{page_name}.md')
    
    # Security check: ensure the file is within docs directory
    try:
        real_file_path = os.path.realpath(file_path)
        real_docs_dir = os.path.realpath(docs_dir)
        if not real_file_path.startswith(real_docs_dir):
            return _render_help_error(request, page_name, "Documentation page not found", "The requested documentation page could not be found or is not accessible.")
    except (OSError, ValueError):
        return _render_help_error(request, page_name, "Documentation page not found", "The requested documentation page could not be found or is not accessible.")
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return _render_help_error(request, page_name, "Documentation page not found", f"The documentation page '{page_name}' does not exist.")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
        html_content = md.convert(content)
        
        # Extract title from first h1 or use filename
        title = page_name.replace('_', ' ').replace('-', ' ').title()
        if content.startswith('# '):
            first_line = content.split('\n')[0]
            title = first_line[2:].strip()
        
        return render(request, 'expenses/help_page.html', {
            'title': title,
            'content': html_content,
            'page_name': page_name
        })
        
    except (OSError, UnicodeDecodeError) as e:
        return _render_help_error(request, page_name, "Error reading documentation", f"Unable to read the documentation file: {e}")


def _render_help_error(request, page_name, error_title, error_message):
    """Render a user-friendly error page for help system."""
    error_content = f"""
    <div class="help-error">
        <div class="help-error-icon">
            <i class="fas fa-exclamation-triangle fa-3x"></i>
        </div>
        <h2>{error_title}</h2>
        <p>{error_message}</p>
        <div class="help-error-actions">
            <a href="/help/" class="btn btn-primary">
                <i class="fas fa-home"></i> Go to Help Index
            </a>
            <a href="/help/?list=1" class="btn btn-secondary">
                <i class="fas fa-list"></i> View All Documentation
            </a>
        </div>
    </div>
    """
    
    return render(request, 'expenses/help_page.html', {
        'title': error_title,
        'content': error_content,
        'page_name': page_name,
        'error': True
    })