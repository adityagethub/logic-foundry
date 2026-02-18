def generate_mermaid(logic_data):
    """
    Generates Mermaid.js flowchart syntax from the extracted logic JSON.
    """
    if "error" in logic_data:
        return "graph TD\n    Error[Error Extraction Failed]:::validation\n    classDef validation fill:#ff4b4b,stroke:#333,stroke-width:2px,color:white;"

    mermaid_lines = ["graph TD"]
    
    # Define Styles
    mermaid_lines.append("    %% Styles")
    mermaid_lines.append("    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;")
    mermaid_lines.append("    classDef startend fill:#262730,stroke:#333,stroke-width:2px,color:white;")
    mermaid_lines.append("    classDef validation fill:#ff4b4b,stroke:#333,stroke-width:2px,color:white;")
    mermaid_lines.append("    classDef pricing fill:#00cc96,stroke:#333,stroke-width:2px,color:black;")
    mermaid_lines.append("    classDef logistics fill:#636efa,stroke:#333,stroke-width:2px,color:white;")
    mermaid_lines.append("    classDef action fill:#e1e1e1,stroke:#333,stroke-width:1px,color:black,shape:rect;")

    # Organize rules by zone for subgraphs
    zones = {
        "validation": [],
        "pricing": [],
        "logistics": [],
        "default": []
    }
    
    rules = logic_data.get('rules', [])
    rule_map = {} # Store basic rule info for iteration

    # 1. Classification Pass
    for i, rule in enumerate(rules):
        rule_id = rule.get('id', f'rule_{i}')
        # Sanitize IDs
        safe_id = "".join(c for c in rule_id if c.isalnum() or c in ['_'])
        if not safe_id: safe_id = f"rule_{i}"
        
        trigger_text = rule.get('trigger', 'Condition').replace('"', "'").replace('(', '').replace(')', '')
        action_text = rule.get('action', 'Action').replace('"', "'")
        
        trigger_lower = trigger_text.lower()
        action_lower = action_text.lower()
        
        zone = "default"
        if any(x in action_lower for x in ['shipping', 'fee']) or \
           any(x in trigger_lower for x in ['weight', 'ship', 'location']):
            zone = "logistics"
        elif any(x in action_lower for x in ['discount', 'price', 'rate', 'total']) or \
             any(x in trigger_lower for x in ['vip', 'promo']):
            zone = "pricing"
        elif 'error' in action_lower or 'return -' in action_lower or 'invalid' in action_lower:
            zone = "validation"
            
        rule_map[i] = {
            "id": safe_id,
            "trigger": trigger_text,
            "action": action_text,
            "zone": zone
        }
        zones[zone].append(i)

    # 2. Generate Subgraphs
    # We render subgraphs first to group nodes
    
    # Start Node (Global)
    mermaid_lines.append("    Start((Start)):::startend")
    
    # Validation Cluster
    if zones['validation']:
        mermaid_lines.append("    subgraph Validation [🛡️ Validation]")
        mermaid_lines.append("    direction TB")
        for i in zones['validation']:
            r = rule_map[i]
            mermaid_lines.append(f"    {r['id']}{{\"{r['trigger']}\"}}:::validation")
        mermaid_lines.append("    end")

    # Pricing Cluster
    if zones['pricing']:
        mermaid_lines.append("    subgraph Pricing [💰 Pricing]")
        mermaid_lines.append("    direction TB")
        for i in zones['pricing']:
            r = rule_map[i]
            mermaid_lines.append(f"    {r['id']}{{\"{r['trigger']}\"}}:::pricing")
        mermaid_lines.append("    end")

    # Logistics Cluster
    if zones['logistics']:
        mermaid_lines.append("    subgraph Logistics [🚚 Logistics]")
        mermaid_lines.append("    direction TB")
        for i in zones['logistics']:
            r = rule_map[i]
            mermaid_lines.append(f"    {r['id']}{{\"{r['trigger']}\"}}:::logistics")
        mermaid_lines.append("    end")
        
    # Default Nodes (No Cluster)
    for i in zones['default']:
        r = rule_map[i]
        mermaid_lines.append(f"    {r['id']}{{\"{r['trigger']}\"}}:::default")

    # 3. Generate Edges (The Flow)
    last_node = "Start"
    
    for i in range(len(rules)):
        r = rule_map[i]
        curr_id = r['id']
        action_id = f"{curr_id}_action"
        
        # Main Flow Edge
        mermaid_lines.append(f"    {last_node} -->|Next| {curr_id}")
        
        # Action Node & Edge
        mermaid_lines.append(f"    {action_id}[\"{r['action']}\"]:::action")
        mermaid_lines.append(f"    {curr_id} -- Yes --> {action_id}")
        
        last_node = curr_id

    # End Node
    mermaid_lines.append(f"    {last_node} --> End((End)):::startend")
    
    return "\n".join(mermaid_lines)
