# Workflow Examples

This document provides concrete examples of workflows and how they can be integrated using the initializer skill.

## Example 1: Content Creation Workflow

### Existing Workflow A (OpenClaw Agent)
```json
{
  "agent_name": "Content_Creator_A",
  "framework": "openclaw",
  "capabilities": {
    "web_access": true,
    "web_scraping": true,
    "content_generation": true,
    "blog_posts": true,
    "social_media": false
  },
  "workflows": {
    "research_phase": {
      "tools": ["browser", "search"],
      "output": "research_notes.json"
    },
    "writing_phase": {
      "tools": ["content_generator", "editor"],
      "output": "draft_content.md"
    }
  }
}
```

### Existing Workflow B (LangChain Agent)
```json
{
  "agent_name": "Social_Media_B",
  "framework": "langchain",
  "capabilities": {
    "web_access": true,
    "social_media": true,
    "content_adaptation": true,
    "scheduling": true,
    "analytics": true
  },
  "workflows": {
    "adaptation_phase": {
      "tools": ["content_adapter", "platform_formatter"],
      "output": "social_posts.json"
    },
    "publishing_phase": {
      "tools": ["platform_api", "scheduler"],
      "output": "published_posts.json"
    }
  }
}
```

### Integrated Workflow
```json
{
  "integrated_agent": "Content_Creation_Brain",
  "hemispheres": {
    "secure": {
      "name": "Research_and_Creation",
      "framework": "openclaw",
      "preserved_workflows": [
        "research_phase",
        "writing_phase"
      ],
      "new_capabilities": [
        "content_editing",
        "quality_check"
      ]
    },
    "utility": {
      "name": "Social_Media_Publishing",
      "framework": "langchain",
      "preserved_workflows": [
        "adaptation_phase",
        "publishing_phase"
      ],
      "new_capabilities": [
        "analytics_integration",
        "performance_tracking"
      ]
    }
  },
  "integrated_workflow": {
    "research": {
      "agent": "secure",
      "workflow": "research_phase",
      "output": "research_notes.json"
    },
    "write": {
      "agent": "secure",
      "workflow": "writing_phase",
      "output": "draft_content.md"
    },
    "adapt": {
      "agent": "utility",
      "workflow": "adaptation_phase",
      "input": "draft_content.md",
      "output": "social_posts.json"
    },
    "publish": {
      "agent": "utility",
      "workflow": "publishing_phase",
      "input": "social_posts.json",
      "output": "published_posts.json"
    }
  }
}
```

## Example 2: Data Analysis Pipeline

### Existing Workflow A (CrewAI Crew)
```json
{
  "crew_name": "Data_Analysis_Crew",
  "agents": [
    {
      "name": "Data_Collector",
      "role": "Gather data from sources",
      "tasks": ["extract", "validate", "clean"],
      "tools": ["database", "api", "file_system"]
    },
    {
      "name": "Data_Analyst",
      "role": "Analyze data patterns",
      "tasks": ["analyze", "identify_trends", "generate_insights"],
      "tools": ["pandas", "numpy", "scikit-learn"]
    }
  ],
  "workflow": {
    "collect": "Data_Collector → validate → clean",
    "analyze": "Data_Analyst → analyze → identify_trends",
    "report": "Data_Analyst → generate_insights → export_report"
  }
}
```

### Existing Workflow B (OpenClaw Agent)
```json
{
  "agent_name": "Report_Generator",
  "framework": "openclaw",
  "capabilities": {
    "visualization": true,
    "reporting": true,
    "dashboard_creation": true,
    "email_delivery": true,
    "scheduling": true
  },
  "workflows": {
    "visualization": {
      "tools": ["plotly", "matplotlib"],
      "output": "visualizations.json"
    },
    "reporting": {
      "tools": ["pdf_generator", "doc_formatter"],
      "output": "report.pdf"
    }
  }
}
```

### Integrated Workflow
```json
{
  "integrated_agent": "Data_Analytics_Brain",
  "hemispheres": {
    "secure": {
      "name": "Data_Processing",
      "framework": "crewai",
      "preserved_agents": [
        "Data_Collector",
        "Data_Analyst"
      ],
      "preserved_workflow": "collect → analyze → report",
      "isolation": "high",
      "system_access": false
    },
    "utility": {
      "name": "Visualization_and_Delivery",
      "framework": "openclaw",
      "preserved_workflows": [
        "visualization",
        "reporting"
      ],
      "new_capabilities": [
        "scheduled_reports",
        "dashboard_automation"
      ],
      "system_access": true,
      "email": true
    }
  },
  "integrated_workflow": {
    "data_pipeline": {
      "agent": "secure",
      "workflow": "collect → validate → clean → analyze",
      "output": "analyzed_data.json"
    },
    "insight_generation": {
      "agent": "secure",
      "workflow": "identify_trends → generate_insights",
      "output": "insights.json"
    },
    "visualization": {
      "agent": "utility",
      "workflow": "visualization",
      "input": "insights.json",
      "output": "visualizations.json"
    },
    "report_creation": {
      "agent": "utility",
      "workflow": "reporting",
      "input": ["insights.json", "visualizations.json"],
      "output": "report.pdf"
    },
    "delivery": {
      "agent": "utility",
      "workflow": "email_delivery",
      "input": "report.pdf",
      "recipients": ["stakeholder@example.com"]
    }
  }
}
```

## Example 3: Customer Support System

### Existing Workflow A (LangChain Agent)
```json
{
  "agent_name": "Support_Bot_A",
  "framework": "langchain",
  "capabilities": {
    "chatbot": true,
    "knowledge_base": true,
    "ticket_routing": true,
    "response_generation": true,
    "sentiment_analysis": true
  },
  "workflows": {
    "incoming_query": {
      "tools": ["chatbot", "nlp"],
      "output": "query_context.json"
    },
    "knowledge_retrieval": {
      "tools": ["vector_store", "semantic_search"],
      "output": "relevant_articles.json"
    },
    "response_generation": {
      "tools": ["llm", "response_formatter"],
      "output": "response.json"
    }
  }
}
```

### Existing Workflow B (CrewAI Crew)
```json
{
  "crew_name": "Human_Support_Crew",
  "agents": [
    {
      "name": "Tier_1_Support",
      "role": "Handle simple queries",
      "tasks": ["triage", "basic_resolution"],
      "escalation_threshold": "complex"
    },
    {
      "name": "Tier_2_Support",
      "role": "Handle complex issues",
      "tasks": ["investigate", "resolve"],
      "escalation_threshold": "technical"
    }
  ],
  "workflow": {
    "triage": "Tier_1_Support → assess → route",
    "resolve": "Tier_1_Support → basic_resolution OR Tier_2_Support → investigate → resolve",
    "escalate": "Tier_2_Support → technical → escalate_to_human"
  }
}
```

### Integrated Workflow
```json
{
  "integrated_agent": "Customer_Support_Brain",
  "hemispheres": {
    "secure": {
      "name": "Automated_Support",
      "framework": "langchain",
      "preserved_workflows": [
        "knowledge_retrieval",
        "response_generation"
      ],
      "new_capabilities": [
        "sentiment_aware_responses",
        "learning_from_feedback"
      ],
      "isolation": "high"
    },
    "utility": {
      "name": "Human_Handoff_and_Escalation",
      "framework": "crewai",
      "preserved_agents": [
        "Tier_1_Support",
        "Tier_2_Support"
      ],
      "preserved_workflow": "triage → resolve → escalate",
      "system_access": true,
      "email": true,
      "ticket_system": true
    }
  },
  "integrated_workflow": {
    "automated_handling": {
      "agent": "secure",
      "workflow": "incoming_query → knowledge_retrieval → sentiment_analysis",
      "output": "automated_response.json"
    },
    "triage_decision": {
      "agent": "utility",
      "workflow": "Tier_1_Support → triage",
      "input": "automated_response.json",
      "decision": "auto_resolve OR escalate"
    },
    "auto_resolve": {
      "agent": "secure",
      "workflow": "response_generation → delivery",
      "output": "resolved_ticket.json"
    },
    "escalation": {
      "agent": "utility",
      "workflow": "Tier_1_Support → Tier_2_Support → investigate",
      "output": "escalated_ticket.json"
    },
    "human_handoff": {
      "agent": "utility",
      "workflow": "escalate_to_human → notify_agent",
      "output": "human_notification.json"
    }
  }
}
```

## Example 4: Research Assistant Workflow

### Existing Workflow A (OpenClaw Agent)
```json
{
  "agent_name": "Literature_Reviewer",
  "framework": "openclaw",
  "capabilities": {
    "web_scraping": true,
    "academic_databases": true,
    "citation_management": true,
    "note_taking": true,
    "bibliography": true
  },
  "workflows": {
    "literature_search": {
      "tools": ["browser", "google_scholar", "pubmed"],
      "output": "papers.json"
    },
    "citation_extraction": {
      "tools": ["citation_parser", "bibtex"],
      "output": "citations.bib"
    }
  }
}
```

### Existing Workflow B (LangChain Agent)
```json
{
  "agent_name": "Synthesis_Writer",
  "framework": "langchain",
  "capabilities": {
    "content_synthesis": true,
    "literature_review": true,
    "critical_analysis": true,
    "structure_organization": true,
    "academic_writing": true
  },
  "workflows": {
    "paper_analysis": {
      "tools": ["pdf_parser", "text_analyzer"],
      "output": "paper_summaries.json"
    },
    "synthesis": {
      "tools": ["llm", "outline_generator"],
      "output": "review_draft.md"
    }
  }
}
```

### Integrated Workflow
```json
{
  "integrated_agent": "Research_Assistant_Brain",
  "hemispheres": {
    "secure": {
      "name": "Literature_Collection",
      "framework": "openclaw",
      "preserved_workflows": [
        "literature_search",
        "citation_extraction"
      ],
      "new_capabilities": [
        "duplicate_detection",
        "quality_scoring"
      ],
      "isolation": "high",
      "database_access": true
    },
    "utility": {
      "name": "Analysis_and_Synthesis",
      "framework": "langchain",
      "preserved_workflows": [
        "paper_analysis",
        "synthesis"
      ],
      "new_capabilities": [
        "critical_thinking",
        "argumentation",
        "manuscript_formatting"
      ],
      "system_access": true,
      "file_operations": true
    }
  },
  "integrated_workflow": {
    "literature_discovery": {
      "agent": "secure",
      "workflow": "literature_search → deduplicate → quality_score",
      "output": "curated_papers.json"
    },
    "content_extraction": {
      "agent": "secure",
      "workflow": "citation_extraction → metadata_extraction",
      "input": "curated_papers.json",
      "output": "paper_content.json"
    },
    "deep_analysis": {
      "agent": "utility",
      "workflow": "paper_analysis → critical_analysis",
      "input": "paper_content.json",
      "output": "analysis_results.json"
    },
    "synthesis": {
      "agent": "utility",
      "workflow": "synthesis → argumentation → manuscript_formatting",
      "input": ["analysis_results.json", "citations.bib"],
      "output": "literature_review.md"
    }
  }
}
```

## Workflow Integration Patterns

### Pattern 1: Sequential Pipeline
```
Workflow A → Workflow B → Workflow C

Example:
Research (Secure) → Analysis (Utility) → Reporting (Utility)
```

### Pattern 2: Parallel Processing
```
Workflow A ──┐
             ├→ Integration → Final Output
Workflow B ──┘

Example:
Data Collection (Secure) ──┐
                         ├→ Combined Analysis → Insights
Feature Extraction (Utility)┘
```

### Pattern 3: Adaptive Routing
```
Input → Assessment → Route to Appropriate Workflow
                        ├→ Simple → Workflow A
                        └→ Complex → Workflow B

Example:
Query → Complexity Check → Simple → Auto-Resolve
                         Complex → Human Handoff
```

### Pattern 4: Iterative Refinement
```
Workflow A → Workflow B → Workflow A → Workflow C

Example:
Draft (Secure) → Edit (Utility) → Revise (Secure) → Finalize (Utility)
```

## Workflow Preservation Rules

### Rule 1: Never Overwrite Without Permission
```json
{
  "preservation_policy": {
    "default": "preserve",
    "overwrite_requires_explicit_permission": true,
    "backup_before_changes": true
  }
}
```

### Rule 2: Maintain Workflow Identity
```json
{
  "preserved_workflow": {
    "original_name": "research_phase",
    "original_agent": "Content_Creator_A",
    "original_framework": "openclaw",
    "preserve_logic": true,
    "preserve_tools": true,
    "preserve_outputs": true
  }
}
```

### Rule 3: Seamless Integration
```json
{
  "integration": {
    "method": "streamline",
    "preserve_capabilities": true,
    "add_capabilities": true,
    "merge_outputs": true,
    "create_unified_interface": true
  }
}
```

## Best Practices

### 1. Document Existing Workflows
- Capture all steps and outputs
- Document dependencies and tools
- Identify integration points

### 2. Test Integration
- Verify workflow preservation
- Test data flow between hemispheres
- Validate final outputs

### 3. Monitor Performance
- Track execution times
- Monitor resource usage
- Identify bottlenecks

### 4. Iterate and Improve
- Gather feedback from users
- Optimize integration points
- Refine workflows over time
