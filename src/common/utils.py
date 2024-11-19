def save_graph_image(graph, output_path: str = "data/graph.png"):
    """
    Save the graph visualization as a PNG file.
    
    Args:
        graph: The graph object
        output_path (str): Path where to save the PNG file
    """
    try:
        # Get the PNG bytes from the graph
        png_data = graph.get_graph(xray=True).draw_mermaid_png()
        
        # Save the bytes directly to a file
        with open(output_path, 'wb') as f:
            f.write(png_data)
            
        print(f"Graph visualization saved to: {output_path}")
        
    except Exception as e:
        print(f"Error saving graph visualization: {e}")
