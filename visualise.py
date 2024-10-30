import streamlit as st
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Your string output


def visualise_single(json_output_data:str, error_log):


    # Parse the JSON data
    data = json.loads(json_output_data)
    print(f'Data is {data}')
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
        fig, ax = plt.subplots(figsize=(10, 2))  # Adjust figure size as necessary
        
        # Colors for each part (name) - can customize more if needed
        colors = {
            "J23101": "skyblue",
            "B0030": "lightgreen",
            "VioA": "lightcoral",
            "B0015": "plum"
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
            
            # Alternate y-position for labels to prevent overlap
            label_y_pos = y_pos + 0.7 if i % 3 == 0 else (y_pos + 1.0 if i % 3 == 1 else y_pos + 1.3)
            
            # Label with name and score (name on the first line, score on the second line)
            plt.text(start + length/2, label_y_pos, f'{name}\n({score})', 
                    horizontalalignment='center', verticalalignment='center', fontsize=8, color='black')
        
        # Set plot limits and labels
        ax.set_xlim(0, path[-1]['end'] + 100)
        ax.set_ylim(0, 2)
        ax.set_xlabel("Position")
        ax.set_yticks([])  # Hide y-axis

        # Hide spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        return fig

    # Streamlit app code
    st.title("Matching Visualization")

    if path:   
        # Generate the plot using the path data
        fig = plot_bricks(path)

        # Display the plot in Streamlit
        st.pyplot(fig)
    else:
        st.error('No reconstruction available.')

