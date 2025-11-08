"""Template management for note creation."""
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class TemplateManager:
    """Manages note templates."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize the template manager.

        Args:
            templates_dir: Directory containing templates
        """
        self.templates_dir = templates_dir or Path("templates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Built-in templates
        self.builtin_templates = {
            'blank': self._blank_template,
            'daily': self._daily_template,
            'meeting': self._meeting_template,
            'research': self._research_template,
            'idea': self._idea_template
        }

    def _blank_template(self) -> str:
        """Blank template with minimal structure."""
        return ""

    def _daily_template(self) -> str:
        """Daily note template."""
        today = datetime.now().strftime("%Y-%m-%d")
        return f"""# Daily Note - {today}

## 🎯 Today's Focus
-

## ✅ Completed
-

## 📝 Notes
-

## 💭 Reflections
-

## ⏭️ Tomorrow
-
"""

    def _meeting_template(self) -> str:
        """Meeting notes template."""
        return """# Meeting Notes

## 📅 Meeting Details
- **Date:**
- **Time:**
- **Attendees:**
- **Location:**

## 📋 Agenda
1.

## 📝 Discussion Points
-

## ✅ Action Items
- [ ]

## 📎 Follow-up
-
"""

    def _research_template(self) -> str:
        """Research note template."""
        return """# Research Note

## 🎯 Research Question
-

## 📚 Sources
1.

## 🔍 Key Findings
-

## 💡 Insights
-

## 🤔 Open Questions
-

## 🔗 Related Topics
-

## 📌 Next Steps
-
"""

    def _idea_template(self) -> str:
        """Idea/brainstorming template."""
        return """# Idea

## 💡 Core Concept
-

## ❓ Problem It Solves
-

## ✨ Key Features
-

## 🎯 Target Audience
-

## 🚀 Implementation Steps
1.

## 🤔 Challenges
-

## 📈 Success Metrics
-

## 🔗 Related Ideas
-
"""

    def get_template(self, template_name: str) -> str:
        """
        Get a template by name.

        Args:
            template_name: Name of the template

        Returns:
            Template content
        """
        template_name_lower = template_name.lower()

        # Check built-in templates
        if template_name_lower in self.builtin_templates:
            return self.builtin_templates[template_name_lower]()

        # Check custom templates
        template_file = self.templates_dir / f"{template_name}.md"
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()

        # Return blank if not found
        return self._blank_template()

    def list_templates(self) -> List[str]:
        """
        List all available templates.

        Returns:
            List of template names
        """
        templates = list(self.builtin_templates.keys())

        # Add custom templates
        for template_file in self.templates_dir.glob('*.md'):
            templates.append(template_file.stem)

        return sorted(templates)

    def save_template(self, name: str, content: str) -> Path:
        """
        Save a custom template.

        Args:
            name: Template name
            content: Template content

        Returns:
            Path to saved template
        """
        template_file = self.templates_dir / f"{name}.md"

        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return template_file

    def delete_template(self, name: str) -> bool:
        """
        Delete a custom template.

        Args:
            name: Template name

        Returns:
            True if successful
        """
        # Don't allow deletion of built-in templates
        if name.lower() in self.builtin_templates:
            return False

        template_file = self.templates_dir / f"{name}.md"

        if template_file.exists():
            template_file.unlink()
            return True

        return False

    def get_template_metadata(self, template_name: str) -> Dict:
        """
        Get metadata about a template.

        Args:
            template_name: Name of the template

        Returns:
            Dictionary with template info
        """
        is_builtin = template_name.lower() in self.builtin_templates

        return {
            'name': template_name,
            'builtin': is_builtin,
            'content': self.get_template(template_name),
            'editable': not is_builtin
        }
