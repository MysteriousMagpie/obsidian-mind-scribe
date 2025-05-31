
"""Module for generating and managing Obsidian vault templates."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .config import config


def create_templates() -> Dict[str, Path]:
    """
    Create all PARA methodology templates in the vault.
    
    Returns:
        Dictionary mapping template names to their file paths
    """
    templates_path = config.vault_path / "01_Templates"
    templates_path.mkdir(parents=True, exist_ok=True)
    
    templates = {
        "Note_Template.md": _get_note_template(),
        "Project_Template.md": _get_project_template(),
        "Daily_Template.md": _get_daily_template(),
        "Area_Template.md": _get_area_template(),
        "Resource_Template.md": _get_resource_template()
    }
    
    created_files = {}
    
    for filename, content in templates.items():
        file_path = templates_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        created_files[filename] = file_path
        print(f"✓ Created template: {file_path}")
    
    return created_files


def _get_note_template() -> str:
    """Generate the basic note template."""
    return """---
title: "{{title}}"
date_created: {{date:YYYY-MM-DD}}
last_modified: {{date:YYYY-MM-DD}}
para_type: ""
status: "draft"
tags: []
priority: ""
area: ""
links: []
---

# {{title}}

## Overview


## Notes


## Related
- 

## Tasks
- [ ] 

---
*Created: {{date:YYYY-MM-DD HH:mm}}*
"""


def _get_project_template() -> str:
    """Generate the project template."""
    return """---
title: "{{title}}"
date_created: {{date:YYYY-MM-DD}}
last_modified: {{date:YYYY-MM-DD}}
para_type: "project"
status: "active"
priority: "medium"
deadline: ""
area: ""
tags: ["project"]
links: []
---

# {{title}}

## 🎯 Project Overview
**Goal:** 
**Deadline:** 
**Area:** 

## 📋 Tasks
- [ ] 
- [ ] 
- [ ] 

## 🏁 Milestones
- [ ] **Phase 1:** 
- [ ] **Phase 2:** 
- [ ] **Phase 3:** 

## 📚 Resources
- 

## 📝 Notes


## 🔗 Related Projects


---
*Project Status: {{status}} | Priority: {{priority}}*
*Created: {{date:YYYY-MM-DD HH:mm}}*
"""


def _get_daily_template() -> str:
    """Generate the daily note template."""
    return """---
title: "{{date:YYYY-MM-DD}}"
date_created: {{date:YYYY-MM-DD}}
last_modified: {{date:YYYY-MM-DD}}
para_type: "daily"
status: "active"
tags: ["daily"]
weather: ""
mood: ""
---

# {{date:dddd, MMMM Do YYYY}}

## 🌅 Morning
**Intention for today:**

**Priority tasks:**
- [ ] 
- [ ] 
- [ ] 

## 📝 Observations & Notes


## ✅ Accomplishments
- 

## 🔄 Project Updates


## 📚 Learning & Insights


## 🌙 Evening Reflection
**What went well:**

**What could improve:**

**Tomorrow's focus:**

---
*Daily Note | {{date:YYYY-MM-DD}}*
"""


def _get_area_template() -> str:
    """Generate the area template."""
    return """---
title: "{{title}}"
date_created: {{date:YYYY-MM-DD}}
last_modified: {{date:YYYY-MM-DD}}
para_type: "area"
status: "active"
priority: "medium"
last_reviewed: {{date:YYYY-MM-DD}}
review_frequency: "weekly"
tags: ["area"]
links: []
---

# {{title}}

## 🎯 Area Overview
**Purpose:** 
**Standard:** 
**Review Frequency:** 

## 📋 Ongoing Responsibilities
- 
- 
- 

## 🚀 Active Projects
- [[]]
- [[]]

## 📚 Resources & References
- 

## 📊 Key Metrics & KPIs


## 📝 Regular Tasks
### Daily
- [ ] 

### Weekly
- [ ] 

### Monthly
- [ ] 

## 🔄 Review Notes
**Last Review:** {{last_reviewed}}

**Current Status:**

**Next Actions:**

---
*Area: {{title}} | Last Reviewed: {{last_reviewed}}*
"""


def _get_resource_template() -> str:
    """Generate the resource template."""
    return """---
title: "{{title}}"
date_created: {{date:YYYY-MM-DD}}
last_modified: {{date:YYYY-MM-DD}}
para_type: "resource"
status: "active"
category: ""
source: ""
tags: ["resource"]
rating: ""
links: []
---

# {{title}}

## 📖 Overview
**Category:** 
**Source:** 
**Rating:** ⭐⭐⭐⭐⭐

## 🔑 Key Information


## 📝 Summary


## 💡 Key Insights
- 
- 
- 

## 🔗 Related Resources
- [[]]
- [[]]

## 📋 Action Items
- [ ] 

## 🏷️ Tags & Categories


---
*Resource | Category: {{category}} | Source: {{source}}*
"""
