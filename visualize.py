import pyvista as pv
import numpy as np
import random

def visualize_packing(placements, title="3D Packing (PyVista)"):
    plotter = pv.Plotter()
    color_map = {}

    def get_random_color():
        return [random.random() for _ in range(3)]

    for placement in placements:
        x, y, z = placement.position
        dx, dy, dz = placement.rotation
        box_name = placement.box.name

        box = pv.Box(bounds=(x, x+dx, y, y+dy, z, z+dz))

        if box_name not in color_map:
            color_map[box_name] = get_random_color()

        plotter.add_mesh(
            box,
            color=color_map[box_name],
            show_edges=True,
            opacity=1.0,
            label=box_name
        )

        center = np.array([x + dx / 2, y + dy / 2, z + dz / 2])
        plotter.add_point_labels(
            [center],
            [box_name],
            font_size=14,
            text_color='black',
            point_color='white',
            point_size=10,
            shape_opacity=0.5,
            always_visible=True
        )

    plotter.add_axes()
    plotter.show_bounds(grid='front', location='outer', all_edges=True)
    plotter.set_background("white")
    plotter.show(title=title)

def visualize_dual_packing(placements_a, placements_b, title_a="Packing A", title_b="Packing B"):
    plotter = pv.Plotter(shape=(1, 2), title="Packing Comparison")

    def add_boxes_to_subplot(plotter, placements, subplot_idx, title):
        plotter.subplot(0, subplot_idx)
        color_map = {}

        def get_random_color():
            return [random.random() for _ in range(3)]

        for placement in placements:
            x, y, z = placement.position
            dx, dy, dz = placement.rotation
            name = placement.box.name

            box = pv.Box(bounds=(x, x+dx, y, y+dy, z, z+dz))
            if name not in color_map:
                color_map[name] = get_random_color()

            plotter.add_mesh(box, color=color_map[name], show_edges=True, opacity=1.0)
            center = [x + dx/2, y + dy/2, z + dz/2]
            plotter.add_point_labels(
                [center], [name],
                font_size=16, always_visible=True, shape_opacity=0.5,
                text_color='black', point_color='white'
            )

        plotter.add_text(title, position='upper_left', font_size=16)
        plotter.show_bounds(grid='front', location='outer', all_edges=True)
        plotter.reset_camera()
        plotter.camera_position = 'iso'

    add_boxes_to_subplot(plotter, placements_a, 0, title_a)
    add_boxes_to_subplot(plotter, placements_b, 1, title_b)

    plotter.set_background('white')
    plotter.show()
