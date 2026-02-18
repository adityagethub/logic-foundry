import graphviz

def create_graph(logic_data):
    graph = graphviz.Digraph()
    graph.attr(rankdir='TB', newrank='true', bgcolor='transparent')
    graph.attr('node', shape='box', style='filled', fontname='Helvetica', fontsize='10')
    graph.attr('edge', fontname='Helvetica', fontsize='9', color='#666666')

    if "error" in logic_data: 
        return graph

    # --- 1. DEFINE ZONES ---
    with graph.subgraph(name='cluster_validation') as c:
        c.attr(label='🛡️ Validation & Errors', color='#FF4B4B', style='rounded,dashed', fontcolor='#FF4B4B')
        c.attr('node', fillcolor='#FFEEEE', color='#FF4B4B')

    with graph.subgraph(name='cluster_pricing') as c:
        c.attr(label='💰 Pricing & Discounts', color='#00CC96', style='rounded,dashed', fontcolor='#00CC96')
        c.attr('node', fillcolor='#E8FDF5', color='#00CC96')

    with graph.subgraph(name='cluster_logistics') as c:
        c.attr(label='🚚 Logistics & Shipping', color='#636EFA', style='rounded,dashed', fontcolor='#636EFA')
        c.attr('node', fillcolor='#E6EAFE', color='#636EFA')

    graph.node('Start', 'Start Order Process', shape='oval', fillcolor='#262730', fontcolor='white')
    last_node = 'Start'
    
    # --- 2. SMART MAPPING ---
    for i, rule in enumerate(logic_data.get('rules', [])):
        rule_id = rule.get('id', f'rule_{i}')
        trigger = rule.get('trigger', '').lower()
        action = rule.get('action', '').lower()
        
        # Priority Classification Strategy
        # Check specific business logic FIRST, before checking for generic "null" errors
        
        zone = 'default'
        
        # 1. Logistics (Shipping, Weight, Fees)
        if any(x in action for x in ['shipping', 'fee']) or \
           any(x in trigger for x in ['weight', 'destination', 'ak', 'hi', 'ship']):
            zone = 'logistics'

        # 2. Pricing (Discounts, Totals, Promos) - Overrides logistics if ambiguous
        elif any(x in action for x in ['discount', 'total', 'price', 'rate']) or \
             any(x in trigger for x in ['vip', 'promo', 'customer']):
            zone = 'pricing'

        # 3. Validation (Errors, Nulls, Bans) - Only if it returns a negative number or explicit error
        elif 'return -' in action or 'error' in action or 'banned' in trigger:
            zone = 'validation'

        # --- DRAW NODES IN ZONES ---
        if zone == 'logistics':
            with graph.subgraph(name='cluster_logistics') as c:
                c.node(rule_id, f"❓ {rule.get('trigger')}", shape='diamond', style='filled,rounded')
        elif zone == 'pricing':
            with graph.subgraph(name='cluster_pricing') as c:
                c.node(rule_id, f"❓ {rule.get('trigger')}", shape='diamond', style='filled,rounded')
        elif zone == 'validation':
            with graph.subgraph(name='cluster_validation') as c:
                c.node(rule_id, f"❓ {rule.get('trigger')}", shape='diamond', style='filled,rounded')
        else:
            graph.node(rule_id, f"❓ {rule.get('trigger')}", shape='diamond', fillcolor='#F0F2F6', color='#808495')

        # Action Node Styling
        action_id = f"{rule_id}_action"
        action_fill = '#F0F2F6' # Default Gray
        
        if zone == 'validation': action_fill = '#FF4B4B' # Red
        if zone == 'pricing': action_fill = '#00CC96'    # Green
        if zone == 'logistics': action_fill = '#636EFA'  # Blue
        
        graph.node(action_id, f"✅ {rule.get('action')}", shape='box', fillcolor=action_fill, fontcolor='black', style='filled')

        # Connect
        graph.edge(last_node, rule_id, label="Next")
        graph.edge(rule_id, action_id, label="Yes", color='#262730', penwidth='1.5')
        last_node = rule_id

    graph.edge(last_node, 'End', label="Done")
    graph.node('End', 'End Process', shape='doublecircle', fillcolor='#262730', fontcolor='white')
        
    return graph
