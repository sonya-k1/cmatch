import streamlit as st
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import pandas as pd



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
        
        # Colors for each part (name) - can customize more if needed
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

    if df.empty:
        st.error("No valid data available for visualization.")
        return

    # Plot KDE (Probability Distribution)
    # st.subheader("cMatch Score Probability Distribution (KDE)")
    # st.subheader('Histogram of cMatch scores')
    fig, ax = plt.subplots(figsize=(8, 4))
    plt.figure(figsize=(8, 6))
    sns.histplot(df['overall_score'], bins=100, kde=False, color='blue', edgecolor='black', ax=ax)


    # sns.kdeplot(df["overall_score"], fill=True, label="Overall Score Distribution", ax=ax)
    ax.set_xlabel("cMatch Score")
    ax.set_ylabel("Frequency")
    ax.set_title("Frequency Distribution of Similarity Scores")
    st.pyplot(fig)
    st.text('Overlap tolerance: 50 bases')
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

