# Specialized Agent Configuration Template

This is for **specialized configurations** that don't fit the conventional security-utility brain model. The brain architecture is still **integrated**, but can be customized for specific use cases.

## Core Configuration

```json
{
  "name": "{{agent_name}}",
  "type": "brain",
  "version": "1.0.0",
  "description": "Specialized agent brain with custom architecture",
  "specialization": "{{specialization_type}}"
}
```

## Specialized Brain Architecture (INTEGRATED - CUSTOMIZABLE)

### Option A: Multi-Hemisphere Brain (> 2 Hemispheres)

```json
{
  "brain": {
    "type": "hemisphere",
    "architecture": "multi-sided",
    "hemispheres": {
      "analysis": {
        "name": "Analysis Hemisphere",
        "role": "Data analysis and processing",
        "isolation": "high",
        "system_access": false,
        "capabilities": ["analysis", "processing", "computation"],
        "sandbox": true
      },
      "storage": {
        "name": "Storage Hemisphere",
        "role": "Memory and data persistence",
        "isolation": "high",
        "system_access": false,
        "capabilities": ["storage", "retrieval", "persistence"],
        "sandbox": true
      },
      "interface": {
        "name": "Interface Hemisphere",
        "role": "User interaction and communication",
        "isolation": "medium",
        "system_access": false,
        "capabilities": ["chat", "messaging", "presentation"],
        "sandbox": true
      },
      "operations": {
        "name": "Operations Hemisphere",
        "role": "System operations and external communication",
        "isolation": "none",
        "system_access": true,
        "capabilities": ["file_operations", "network", "system_commands"],
        "sandbox": false
      }
    },
    "synchronization": {
      "method": "event_driven",
      "frequency": "on_change",
      "consistency": "eventual",
      "message_format": "json"
    }
  }
}
```

### Option B: Hierarchical Brain

```json
{
  "brain": {
    "type": "hierarchical",
    "architecture": "multi-level",
    "levels": {
      "strategic": {
        "name": "Strategic Level",
        "role": "High-level planning and coordination",
        "subordinates": ["tactical"],
        "capabilities": ["planning", "coordination", "decision_making"],
        "isolation": "medium"
      },
      "tactical": {
        "name": "Tactical Level",
        "role": "Task execution and resource management",
        "subordinates": ["operational"],
        "capabilities": ["task_management", "resource_allocation", "supervision"],
        "isolation": "medium"
      },
      "operational": {
        "name": "Operational Level",
        "role": "Direct operations and execution",
        "subordinates": [],
        "capabilities": ["execution", "processing", "data_handling"],
        "isolation": "low"
      }
    },
    "synchronization": {
      "method": "top_down_with_feedback",
      "frequency": "hierarchical",
      "consistency": "strong"
    }
  }
}
```

### Option C: Domain-Specific Brain (e.g., Healthcare)

```json
{
  "brain": {
    "type": "domain_specific",
    "domain": "healthcare",
    "architecture": "specialized",
    "hemispheres": {
      "clinical": {
        "name": "Clinical Hemisphere",
        "role": "Medical diagnosis and treatment planning",
        "specialization": "clinical_operations",
        "compliance": ["hipaa", "hl7", "fhir"],
        "isolation": "high",
        "system_access": false,
        "capabilities": ["diagnosis", "treatment_planning", "medical_analysis"],
        "sandbox": true
      },
      "administrative": {
        "name": "Administrative Hemisphere",
        "role": "Medical records and scheduling",
        "specialization": "administrative_operations",
        "compliance": ["hipaa", "phi"],
        "isolation": "high",
        "system_access": false,
        "capabilities": ["records_management", "scheduling", "billing"],
        "sandbox": true
      },
      "infrastructure": {
        "name": "Infrastructure Hemisphere",
        "role": "System operations and external integrations",
        "specialization": "infrastructure_operations",
        "compliance": ["hipaa"],
        "isolation": "none",
        "system_access": true,
        "capabilities": ["file_operations", "database_access", "external_apis"],
        "sandbox": false
      }
    },
    "synchronization": {
      "method": "request_response",
      "frequency": "on_demand",
      "consistency": "strong",
      "compliance_enforcement": true
    }
  }
}
```

### Option D: Creative Brain (e.g., Content Creation)

```json
{
  "brain": {
    "type": "creative",
    "architecture": "collaborative",
    "hemispheres": {
      "ideation": {
        "name": "Ideation Hemisphere",
        "role": "Idea generation and brainstorming",
        "capabilities": ["brainstorming", "ideation", "creative_thinking"],
        "sandbox": true,
        "isolation": "high"
      },
      "creation": {
        "name": "Creation Hemisphere",
        "role": "Content creation and production",
        "capabilities": ["writing", "visual_creation", "media_production"],
        "sandbox": true,
        "isolation": "high"
      },
      "curation": {
        "name": "Curation Hemisphere",
        "role": "Content review and quality control",
        "capabilities": ["editing", "review", "quality_assurance"],
        "sandbox": true,
        "isolation": "medium"
      },
      "distribution": {
        "name": "Distribution Hemisphere",
        "role": "Content publishing and distribution",
        "capabilities": ["social_media", "publishing", "analytics"],
        "sandbox": false,
        "isolation": "none",
        "system_access": true
      }
    },
    "synchronization": {
      "method": "pipeline",
      "frequency": "sequential",
      "consistency": "strong",
      "workflow": "ideation → creation → curation → distribution"
    }
  }
}
```

## Specialized Capabilities

### Healthcare Specialization
```json
{
  "capabilities": {
    "medical_analysis": {
      "enabled": true,
      "compliance": ["hipaa", "phi"],
      "data_types": ["patient_records", "clinical_trials", "research"],
      "agent": "clinical"
    },
    "medical_knowledge": {
      "enabled": true,
      "sources": ["pubmed", "medline", "mayoclinic"],
      "update_frequency": "daily",
      "agent": "clinical"
    },
    "treatment_planning": {
      "enabled": true,
      "guidelines": ["clinical", "evidence_based"],
      "review_required": true,
      "agent": "clinical"
    }
  }
}
```

### Financial Specialization
```json
{
  "capabilities": {
    "financial_analysis": {
      "enabled": true,
      "compliance": ["sox", "glba", "sec"],
      "data_types": ["stocks", "bonds", "commodities", "derivatives"],
      "agent": "analysis"
    },
    "risk_assessment": {
      "enabled": true,
      "models": ["var", "monte_carlo", "stress_test"],
      "reporting": "real_time",
      "agent": "analysis"
    },
    "regulatory_compliance": {
      "enabled": true,
      "frameworks": ["basel", "dodd_frank", "mifid"],
      "audit_trail": true,
      "agent": "administrative"
    }
  }
}
```

### Legal Specialization
```json
{
  "capabilities": {
    "legal_research": {
      "enabled": true,
      "sources": ["case_law", "statutes", "regulations"],
      "jurisdictions": ["federal", "state"],
      "agent": "research"
    },
    "document_analysis": {
      "enabled": true,
      "document_types": ["contracts", "pleadings", "motions"],
      "nlp_models": ["bert_legal", "roberta_legal"],
      "agent": "analysis"
    },
    "compliance_monitoring": {
      "enabled": true,
      "regulations": ["gdpr", "ccpa", "hipaa"],
      "automated_checks": true,
      "agent": "administrative"
    }
  }
}
```

## Specialized Security Configuration

### Healthcare Security
```json
{
  "security": {
    "permission_model": "explicit",
    "encryption": {
      "enabled": true,
      "algorithm": "aes256",
      "key_management": "secure",
      "compliance": ["hipaa_security_rule"]
    },
    "audit_logging": {
      "enabled": true,
      "events": ["all"],
      "retention": "6_years",
      "compliance": ["hipaa_audit_rule"]
    },
    "access_control": {
      "enabled": true,
      "model": "role_based",
      "phi_protection": true,
      "minimum_necessary": true
    },
    "data_protection": {
      "de_identification": true,
      "data_masking": true,
      "phi_handling": "secure"
    }
  }
}
```

### Financial Security
```json
{
  "security": {
    "permission_model": "explicit",
    "encryption": {
      "enabled": true,
      "algorithm": "aes256",
      "key_management": "fips_140_2_compliant"
    },
    "audit_logging": {
      "enabled": true,
      "events": ["all"],
      "retention": "7_years",
      "compliance": ["sox", "glba"]
    },
    "access_control": {
      "enabled": true,
      "model": "role_based",
      "segregation_of_duties": true,
      "dual_control": true
    },
    "fraud_detection": {
      "enabled": true,
      "real_time": true,
      "ml_detection": true
    }
  }
}
```

## Specialized Workflows

### Healthcare Workflow
```json
{
  "workflows": {
    "patient_intake": {
      "agent": "administrative",
      "steps": ["registration", "insurance_verification", "triage"],
      "output": "patient_record.json"
    },
    "diagnosis": {
      "agent": "clinical",
      "steps": ["symptom_analysis", "literature_review", "differential_diagnosis"],
      "output": "diagnosis_report.json"
    },
    "treatment_planning": {
      "agent": "clinical",
      "steps": ["evidence_research", "guideline_application", "treatment_design"],
      "output": "treatment_plan.json"
    },
    "implementation": {
      "agent": "infrastructure",
      "steps": ["scheduling", "billing", "record_update"],
      "output": "implementation_log.json"
    }
  }
}
```

### Financial Workflow
```json
{
  "workflows": {
    "market_analysis": {
      "agent": "analysis",
      "steps": ["data_collection", "technical_analysis", "fundamental_analysis"],
      "output": "market_report.json"
    },
    "risk_assessment": {
      "agent": "analysis",
      "steps": ["exposure_calculation", "stress_testing", "var_calculation"],
      "output": "risk_report.json"
    },
    "compliance_check": {
      "agent": "administrative",
      "steps": ["regulatory_review", "documentation", "approval"],
      "output": "compliance_report.json"
    },
    "trade_execution": {
      "agent": "infrastructure",
      "steps": ["order_placement", "confirmation", "settlement"],
      "output": "trade_record.json"
    }
  }
}
```

## Variables

### Required Variables
- `{{agent_name}}` - Name of your specialized agent brain
- `{{specialization_type}}` - Type of specialization (healthcare, financial, legal, etc.)

### Optional Variables
- `{{domain}}` - Specific domain within specialization
- `{{compliance_frameworks}}` - List of applicable compliance frameworks
- `{{integration_points}}` - External systems to integrate with

## Usage

### Applying a Specialized Template
```bash
# Apply healthcare specialization
initializer template apply --type specialized --specialization healthcare \
  --name healthcare_brain

# Apply financial specialization
initializer template apply --type specialized --specialization financial \
  --name trading_brain

# Apply with custom brain architecture
initializer template apply --type specialized \
  --architecture multi_hemisphere \
  --name my_specialized_brain
```

### Customizing Specialized Template
```bash
# Add custom compliance frameworks
initializer template customize --type specialized \
  --specialization healthcare \
  --compliance "hipaa,hl7,fhir,cms"

# Configure specialized security
initializer template customize --type specialized \
  --specialization financial \
  --security "fraud_detection=true,compliance=sox,glba"

# Add specialized workflows
initializer template customize --type specialized \
  --specialization legal \
  --workflows "legal_research,document_analysis,compliance_monitoring"
```

## Specialization Types

### 1. Healthcare
- **Use Case**: Medical diagnosis, treatment planning, patient care
- **Compliance**: HIPAA, HL7, FHIR
- **Brain Architecture**: Clinical, Administrative, Infrastructure hemispheres

### 2. Financial Services
- **Use Case**: Trading, risk management, compliance
- **Compliance**: SOX, GLBA, SEC, Basel
- **Brain Architecture**: Analysis, Risk, Compliance, Operations hemispheres

### 3. Legal
- **Use Case**: Legal research, document analysis, compliance
- **Compliance**: GDPR, CCPA, industry-specific regulations
- **Brain Architecture**: Research, Analysis, Compliance hemispheres

### 4. Education
- **Use Case**: Content delivery, assessment, student support
- **Compliance**: FERPA, educational standards
- **Brain Architecture**: Content, Assessment, Support hemispheres

### 5. Retail
- **Use Case**: Customer service, inventory management, sales
- **Compliance**: PCI DSS, consumer protection
- **Brain Architecture**: Service, Operations, Analytics hemispheres

## Notes

- **Brain architecture remains integrated** but is customizable
- **Specialization-specific capabilities** are included
- **Industry compliance** is built into security configuration
- **Specialized workflows** are optimized for the use case
- **Can be combined** with general configuration for hybrid needs
- **Preserves workflow integrity** during merges

## Customization Guidelines

1. **Maintain Brain Integration**: Always keep the brain architecture as the core
2. **Domain-Specific Capabilities**: Add capabilities relevant to the specialization
3. **Compliance First**: Ensure security configuration meets industry standards
4. **Optimized Workflows**: Design workflows for the specific use case
5. **Integration Ready**: Maintain compatibility with external systems

This template provides flexibility for specialized use cases while maintaining the integrated brain architecture as the foundational design.
