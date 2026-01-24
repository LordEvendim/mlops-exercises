import io
import base64
import matplotlib
import matplotlib.pyplot as plt
from typing import List, Optional
from fastmcp import FastMCP

matplotlib.use('Agg')
mcp = FastMCP("Visualization MCP")

@mcp.tool(description="Create a line plot from given data and saves it to a file. Returns the filename.")
def line_plot(
    data: List[List[float]],
    title: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    legend: bool = False
) -> str:
    plt.figure()
    
    for i, series in enumerate(data):
        label = f"Series {i+1}" if legend else None
        plt.plot(series, label=label)
    
    if title:
        plt.title(title)
    if x_label:
        plt.xlabel(x_label)
    if y_label:
        plt.ylabel(y_label)
    if legend:
        plt.legend()
        
    filename = "plot.png"
    plt.savefig(filename)
    plt.close()
    
    return f"Plot saved to {filename}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8004)