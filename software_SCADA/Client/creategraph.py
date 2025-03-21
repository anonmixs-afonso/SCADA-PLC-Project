import time
import numpy as np
import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io

kivy.require('2.0.0')  # Ensure we're using the correct Kivy version

class TempGraphApp(App):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.temperature_data = {key: value for key, value in self.data.items() if 'temperatura' in key}
        self.graphs = {}  # Dictionary to store each graph's components
        self.time = 0  # Initialize the time attribute

    def build(self):
        # Create a GridLayout with rows and columns based on the number of graphs
        num_graphs = len(self.temperature_data)
        rows = int(np.ceil(np.sqrt(num_graphs)))  # Adjust rows and columns for a balanced layout
        cols = int(np.ceil(num_graphs / 1+rows))

        self.layout = GridLayout(rows=rows, cols=cols)
        self.layout.spacing = 10  # Add spacing between graphs
        self.layout.padding = 10  # Add padding around the grid

        # Define a list of colors for the lines
        colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'orange', 'purple', 'brown']

        # Create a graph for each temperature data
        for i, key in enumerate(self.temperature_data):
            # Create a figure and axis for the graph
            fig, ax = plt.subplots(dpi=100)
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Temperature (°C)')
            ax.set_title(key)  # Use the key as the title of the graph

            # Plot an initial empty line
            line, = ax.plot([], [], label=key, color=colors[i % len(colors)], linewidth=2)

            # Store the figure, axis, and line in the dictionary
            self.graphs[key] = {
                'fig': fig,
                'ax': ax,
                'line': line,
                'image_widget': Image()
            }

            # Add the image widget to the layout
            self.layout.add_widget(self.graphs[key]['image_widget'])

        # Schedule the graph update every second
        Clock.schedule_interval(self.update_graphs, 1)
        return self.layout

    def update_graphs(self, dt):
        for key in self.temperature_data:
            new_value = self.data[key]
            graph = self.graphs[key]

            # Update the line with the new data
            current_xdata, current_ydata = graph['line'].get_data()
            current_xdata = list(current_xdata) + [self.time]
            current_ydata = list(current_ydata) + [new_value]
            graph['line'].set_data(current_xdata, current_ydata)

            # Adjust the x-axis and y-axis limits
            graph['ax'].set_xlim(self.time - 100, self.time)
            graph['ax'].set_ylim(min(current_ydata) - 5, max(current_ydata) + 5)

            # Render the figure to a buffer
            buf = io.BytesIO()
            canvas = FigureCanvasAgg(graph['fig'])
            canvas.draw()
            buf.write(canvas.tostring_argb())
            buf.seek(0)

            # Convert the buffer to a numpy array for flipping
            image_data = np.frombuffer(buf.getvalue(), dtype=np.uint8)
            image_data = image_data.reshape((int(graph['fig'].get_size_inches()[1] * graph['fig'].dpi),
                                            int(graph['fig'].get_size_inches()[0] * graph['fig'].dpi), -1))
            image_data = np.flipud(image_data)

            # Create a Kivy texture from the flipped image data
            texture = Texture.create(size=(image_data.shape[1], image_data.shape[0]), colorfmt='rgba')
            texture.blit_buffer(image_data.tobytes(), colorfmt='rgba', bufferfmt='ubyte')

            # Update the Image widget with the new texture
            graph['image_widget'].texture = texture

        # Increment time for the next data update
        self.time += 1

# Example of how to use the app with your existing data
if __name__ == '__main__':
    # Example data that is updated externally (simulating real data)
    data = {
        'Temperatura SA': 45, 'Temperatura TIT-02': 50, 'Temperatura TIT-01': 55,
        'Temperatura Termostato': 60
    }

    # Create and run the Kivy app with the existing data
    TempGraphApp(data=data).run()
