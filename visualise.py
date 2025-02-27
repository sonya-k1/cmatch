import streamlit as st
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import colorsys
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from statistics import geometric_mean



def visualise_single(json_output_data:str, error_log):

    st.title("Visualisation of single cMatch reconstruct")

    # Parse the JSON data
    data = json.loads(json_output_data)
    # print(f'Data is {data}')
    path = False # Do not plot if we do not have a reconstruction
    if len(error_log) == 0:
        if 'path' in data[0].keys():
            path = data[0]['path']
        else:    
            st.error('Could not match all parts with this threshold')
    else:
        st.error(f"Errors: {str(error_log)}")

    
    # Function to create the visualization
    def plot_bricks(path):
        fig, ax = plt.subplots(figsize=(10, 4))  # Adjust figure size as necessary
        
        # colors for each part (name) - can customize more if needed
        colors = {
            "J23101": "skyblue",
            "B0030": "lightgreen",
            "VioA": "lightcoral",
            "B0015": "plum",
            "GFP": "pink"
        }
        
        y_pos = 0.5  # Fixed height for all bricks

        # Iterate through the path to draw bricks
        for i, part in enumerate(path):
            start = part['start']
            length = part['length']
            name = part['name']
            score = part['score']
            
            # Set color based on part name
            color = colors.get(name, 'grey')

            # Create a rectangle (brick)
            rect = patches.Rectangle((start, y_pos), length, 0.5, edgecolor='black', facecolor=color)

            # Add the rectangle to the plot
            ax.add_patch(rect)
            
                # Stagger label positions vertically
            label_y_pos = y_pos + 1.0 + (i % 2) * 0.75   # Adjusted stagger for readability
            
            # Add annotation for name and score (with line breaks)
            ax.annotate(
                f'{name}\n({score:.2f})',  # Display up to 2 decimal places
                xy=(start + length/2, y_pos + 0.25),
                xytext=(start + length/2, label_y_pos),
                fontsize=10,
                ha='center', 
                va='center',
                color=color,  # Match text color to brick
                arrowprops=dict(arrowstyle='-', color='black', lw=0.5)  # Line properties
            )

        # Add a legend to map colors to part names
        handles = [patches.Patch(color=col, label=name) for name, col in colors.items()]
        ax.legend(handles=handles, loc='upper right', fontsize=10, title="Part Names")

        # Add gridlines for positions
        ax.grid(axis='x', color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

        # Set plot limits and labels
        ax.set_xlim(-20, path[-1]['end'] + 100)
        ax.set_ylim(0, 3 + len(path) * 0.5)  # Increase y-limit for spacing
        ax.set_xlabel("Position", fontsize=12)
        ax.set_ylabel("Part names and match scores", fontsize=12)
        ax.set_yticks([])  # Hide y-axis ticks
        # Hide spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        # plt.tight_layout()

        return fig


    if path:   
        # Generate the plot using the path data
        fig = plot_bricks(path)

        # Display the plot in Streamlit
        st.pyplot(fig)
    else:
        st.error('No reconstruction available.')

def plot_bricks(path):
        fig, ax = plt.subplots(figsize=(10, 4))  # Adjust figure size as necessary
        
        # colors for each part (name) - can customize more if needed
        colors = {
            "J23101": "skyblue",
            "B0030": "lightgreen",
            "VioA": "lightcoral",
            "B0015": "plum",
            "GFP": "blue"
        }
        
        y_pos = 0.5  # Fixed height for all bricks

        # Iterate through the path to draw bricks
        for i, part in enumerate(path):
            start = part['start']
            length_theoretical = part['length']
            name = part['name']
            score = part['score']
            end = part['end']
            length_observed = end-start
            
            # Set color based on part name
            color = colors.get(name, 'grey')

            # Create a rectangle (brick)
            rect = patches.Rectangle((start, y_pos), length_observed, 0.5, edgecolor='black', facecolor=color, alpha=0.5)

            # Add the rectangle to the plot
            ax.add_patch(rect)
            
                # Stagger label positions vertically
            label_y_pos = y_pos + 1.0 + (i % 2) * 0.75   # Adjusted stagger for readability
            
            # Add annotation for name and score (with line breaks)
            ax.annotate(
                f'{name}\n({score:.2f})',  # Display up to 2 decimal places
                xy=(start + length_observed/2, y_pos + 0.25),
                xytext=(start + length_observed/2, label_y_pos),
                fontsize=10,
                ha='center', 
                va='center',
                color=color,  # Match text color to brick
                arrowprops=dict(arrowstyle='-', color='black', lw=0.5)  # Line properties
            )

        # Add a legend to map colors to part names
        handles = [patches.Patch(color=col, label=name) for name, col in colors.items()]
        ax.legend(handles=handles, loc='upper right', fontsize=10, title="Part Names")

        # Add gridlines for positions
        ax.grid(axis='x', color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

        # Set plot limits and labels
        ax.set_xlim(-20, path[-1]['end'] + 100)
        ax.set_ylim(0, 3 + len(path) * 0.5)  # Increase y-limit for spacing
        ax.set_xlabel("Position", fontsize=12)
        ax.set_ylabel("Part names and match scores", fontsize=12)
        ax.set_yticks([])  # Hide y-axis ticks
        # Hide spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        # plt.tight_layout()

        return fig



def visualise_parts(json_output_data:str):

    st.title('cMatch reconstruction map')
    # Parse the JSON data
    data = json.loads(json_output_data)
    # breakpoint()
    len_data = len(data)
    
    # print(f'Data is {data}')
    path = False # Do not plot if we do not have a reconstruction
    i = 1
    for result in data:
        if result['path'] is not None:
            path = result['path']
            fig = plot_bricks(path)
            score = result['score']
            label = result['reconstruct']
            target_name = result['target']

            # Display the plot in Streamlit
            st.text(f"Seq: {i}/{len_data} \n Target name: {target_name} \n cMatch Reconstruction Result: {label} \n Score: {score}")
            st.pyplot(fig)


        else:
            score = result['score']
            error = result['errors']
            target_name = result['target']

            # Display the plot in Streamlit
            st.text(f"Seq: {i}/{len_data} \n Target name: {target_name} \n cMatch Reconstruction Result: {error} \n Score: {score}")  
            # st.error('Could not match all parts with this threshold')
        i+=1



# Function to visualize multiple constructs' score distribution
def visualise_distribution(result_json:str, error_log):
    st.title("Visualisation of multiple cMatch Scores")
    # breakpoint()
    # Parse JSON input
    data = json.loads(result_json)
    # data = result_json # if data already parsed in cmatch
    # print('Data is: ', data)
    
    # if type(data)=='list':
    #     breakpoint()
    # elif type(data)!='dict':
    #     breakpoint()
    # Extract scores
    records = []
    for entry in data:
        # print('entry:', entry)
        target = entry["target"]
        overall_score = entry["score"]
        
        # Store each result
        records.append({
            "target": target,
            "overall_score": overall_score,
            
        })
    
    df = pd.DataFrame(records)
    # breakpoint()
    df.sort_values(by=['overall_score'])
    df_unique = df.drop_duplicates()

    if df.empty:
        st.error("No valid data available for visualization.")
        return

    # Plot KDE (Probability Distribution)
    # st.subheader("cMatch Score Probability Distribution (KDE)")
    # st.subheader('Histogram of cMatch scores')
    fig, ax = plt.subplots(figsize=(8, 4))
    plt.figure(figsize=(8, 6))
    sns.histplot(df_unique['overall_score'], bins=100, kde=False, color='blue', edgecolor='black', ax=ax)


    # sns.kdeplot(df["overall_score"], fill=True, label="Overall Score Distribution", ax=ax)
    ax.set_xlabel("cMatch Score")
    ax.set_ylabel("Frequency")
    ax.set_title("Frequency Distribution of Similarity Scores")
    st.pyplot(fig)
    st.text('Overlap tolerance: 0 bases')
    # if len(error_log) > 0:
    #     st.text(f"Errors: {str(error_log)}")
 
def plot_error_types(errors_json):
    """
    Function to parse errors, count occurrences of each error type, and plot a bar chart using Seaborn and Streamlit.
    
    Args:
        errors_json (str): JSON string of error data.

    """
    errors_list = json.loads(errors_json)

    error_messages = [error['errors'] for sublist in errors_list for error in sublist]

    
    df = pd.DataFrame({'Error Type': error_messages})
    error_counts = df['Error Type'].value_counts().reset_index()
    error_counts.columns = ['Error Type', 'Count']

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    bar_plot = sns.barplot(x="Count", y="Error Type", data=error_counts, palette="viridis")
    bar_plot.set_title("Error Types and Their Frequencies", fontsize=16)
    bar_plot.set_xlabel("Count", fontsize=12)
    bar_plot.set_ylabel("Error Type", fontsize=12)
    st.pyplot(plt)

def plot_3d(results:str):
    # st.title('cMatch vector map')
    st.title("3D Plot of Genetic Part Scores")

    # Parse the JSON data
    data = json.loads(results)
    # breakpoint()
    len_data = len(data)

    i = 1
    for result in data:
        # Extract path scores and names
        if result['path'] is not None:
            path = result['path']
            fig = plot_bricks(path)
            score = result['score']
            label = result['reconstruct']
            target_name = result['target']

            # Display the plot in Streamlit
            st.text(f"Seq: {i}/{len_data} \n Target name: {target_name} \n cMatch Reconstruction Result: {label} \n Score: {score}")
            st.pyplot(fig)
            try:
                part1, part2, part3, part4 = path
                # Calculate averaged score for the first two parts
                avg_score_12 = (part1['score'] + part2['score']) / 2

                # Prepare scores and labels for the 3D plot
                x = avg_score_12  # Average score of first two parts
                y = part3['score']  # Score of third part
                z = part4['score']  # Score of fourth part
                labels = [part1['name'], part2['name'], part3['name'], part4['name']]

                # Define the fixed point (1, 1, 1)
                fixed_point = np.array([1, 1, 1])

                # Calculate distances to (1, 1, 1)
                point = np.array([x, y, z])
                distance = np.linalg.norm(point - fixed_point)

                
                # st.write("### Input Result:")
                # st.json(result)

                
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111, projection='3d')

                # Plot the averaged score and the other scores
                ax.scatter(x, y, z, color='b', label='Construct Point', s=100)
                ax.text(x, y, z, f"({x:.2f}, {y:.2f}, {z:.2f})", color='blue')

                # Plot the fixed point (1, 1, 1)
                ax.scatter(1, 1, 1, color='r', label='Reference Point (1, 1, 1)', s=100)
                ax.text(1, 1, 1, "(1, 1, 1)", color='red')

                # Add connecting line
                ax.plot([x, 1], [y, 1], [z, 1], color='gray', linestyle='--')

                # Label distances for each axis
                ax.text((x + 1) / 2, (y + 1) / 2, (z + 1) / 2,
                        f"Distance: {distance:.2f}", color='black', fontsize=10)

                # Axes labels
                ax.set_xlabel(f"Average Score ({labels[0]} + {labels[1]}) / 2", fontsize=12)
                ax.set_ylabel(f"Score ({labels[2]})", fontsize=12)
                ax.set_zlabel(f"Score ({labels[3]})", fontsize=12)
                ax.set_xlim([0,1])
                ax.set_ylim([0,1])
                ax.set_zlim([0,1])

                # Title and legend
                ax.set_title("3D Visualization of Genetic Part Scores", fontsize=16)
                ax.legend()

                # Display the plot in Streamlit
                st.pyplot(fig)

                # Distance information
                st.text(f"Seq: {i}/{len_data} \n Target name: {target_name} \n cMatch Reconstruction Result: {label} \n Score: {score}")

                st.text(f"### Distance from Reference Point (1, 1, 1): **{distance:.2f}**")
            except ValueError as e:
                
                st.text(f'Overlapping error for target: {target_name} \n Path: {path}\n Errors: {result['errors']}')

            
        else:
            st.text(f'All Parts not found for target: {result['target']}  \n Errors: {result['errors']}')
        i+=1


def generate_colors(n):
    """Generate `n` visually distinct colors using the HSV color space."""
    colors = []
    for i in range(n):
        hue = i / n  # Distribute hues equally
        r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)  # High saturation and value
        colors.append(f'rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, 0.8)')
    return colors



def plot_3d_multiple_scores(data:str):
    st.title("3D Plot of Genetic Part Scores")

    results = json.loads(data)
    unique_acc_values = set()  # To track unique XX values

    for result in results:
        target_name = result['target']
        # Extract accuracy values from target names
        acc_value = target_name.split('_')[2]  
        unique_acc_values.add(acc_value)
            
            

    # Generate distinct colors for unique XX values
    color_palette = cm.get_cmap('tab10')
    acc_color_map = {acc: mcolors.to_hex(color_palette(i / len(unique_acc_values))) 
                     for i, acc in enumerate(unique_acc_values)}

    # Lists to store 3D coordinates and hover info
    x_vals, y_vals, z_vals = [], [], []
    failed_x, failed_y, failed_z = [], [], []
    failed_hover_texts = []
    hover_texts = []
    point_colors = [] 
    failed_colours = []

    for result in results:
        target_name = result['target']
        acc_value = target_name.split('_')[2]  # Extract XX

        if result['path'] is not None and len(result['path']) == 4:
            path = result['path']
            # Successful results (no change here)
            color = acc_color_map[acc_value]
            x = geometric_mean([path[0]['score'], path[1]['score']])
            y = path[2]['score']
            z = path[3]['score']
            
            x_vals.append(x)
            y_vals.append(y)
            z_vals.append(z)
            point_colors.append(color)
            hover_texts.append(
                f"Target: {target_name}<br>"
                f"PBSim Accuracy: {acc_value}<br>"
                f"cMatch Score: {result['score']}<br>"
                f"Mean Score: {geometric_mean([x, y, z])}<br>"
                f"Avg Score (Part 1 & 2): {x:.2f}<br>"
                f"Score (Part 3): {y:.2f}<br>"
                f"Score (Part 4): {z:.2f}"
            )

        else:
            # Failed results, assigned to (0,0,0) with jitter
            color = acc_color_map.get(acc_value, "#808080")
            failed_x.append(0 + np.random.uniform(0, 0.05))
            failed_y.append(0 + np.random.uniform(0, 0.05))
            failed_z.append(0 + np.random.uniform(0, 0.05))
            failed_colours.append(color)
            failed_hover_texts.append(
                f"Target: {target_name}<br>Error: {result['errors']}"
            )


    # Create a 3D scatter plot
    fig = go.Figure()

    # Add points for each result
    fig.add_trace(go.Scatter3d(
        x=x_vals, y=y_vals, z=z_vals,
        mode='markers',
        # text=[f"Point {i+1}" for i in range(len(x_vals))],
        hovertext=hover_texts,
        hoverinfo="text",
        marker=dict(
            size=8,
            color=point_colors,  # Apply gradient colors
            opacity=0.8
        ),
        showlegend=False
    ))

    # Add the fixed reference point (1, 1, 1)
    fig.add_trace(go.Scatter3d(
        x=[1], y=[1], z=[1],
        mode='markers',
        text=["(1, 1, 1)"],
        hovertext="Reference Point: (1, 1, 1)",
        hoverinfo="text",
        marker=dict(
            size=10,
            color='red',  # Fixed color for the reference point
            opacity=0.8
        ),
        name="Reference Point (1,1,1)"
    ))
    fig.add_trace(go.Scatter3d(
    x=failed_x, y=failed_y, z=failed_z,
    mode='markers',
    hovertext=failed_hover_texts,
    hoverinfo="text",
    marker=dict(
        size=6,
        color=failed_colours,  
        opacity=0.8  
    ),
    showlegend=False
))
    for acc_value, color in acc_color_map.items():
        fig.add_trace(go.Scatter3d(
            x=[None], y=[None], z=[None],  
            mode='markers',
            marker=dict(size=10, color=color),
            name=f"PBSim accuracy = {acc_value}"  
        ))

    # Add labels to axes
    fig.update_layout(
        scene=dict( 
            xaxis_title="Average Score (Part 1 & 2)",
            yaxis_title="Score (Part 3)",
            zaxis_title="Score (Part 4)",
            xaxis=dict(
            range=[0, 1],  # Keeping your custom range
            tickmode="array",
            tickvals=[i / 10 for i in range(0, 11)],  # Extends to -0.1
            ticktext=[f"{i/10:.1f}" for i in range(0, 11)]
        ),
        yaxis=dict(
            range=[0, 1],
            tickmode="array",
            tickvals=[i / 10 for i in range(0, 11)],
            ticktext=[f"{i/10:.1f}" for i in range(0, 11)]
        ),
        zaxis=dict(
            range=[0, 1],
            tickmode="array",
            tickvals=[i / 10 for i in range(0, 11)],
            ticktext=[f"{i/10:.1f}" for i in range(0, 11)]
        ),
            aspectmode="cube"
        ),
        title="Interactive 3D Plot of Genetic Part Scores with Gradient coloring",
        showlegend=True
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig)

