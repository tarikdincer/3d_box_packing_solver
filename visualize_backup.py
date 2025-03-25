import plotly.graph_objects as go

def visualize_packing(placements, title="3D Box Packing"):
    fig = go.Figure()

    # Generate distinct colors
    def generate_colors(n):
        return [f"hsl({int(i * 360 / n)}, 70%, 60%)" for i in range(n)]

    colors = generate_colors(len(placements))

    for i, placement in enumerate(placements):
        x, y, z = placement.position
        dx, dy, dz = placement.rotation
        box_name = placement.box.name

        # Define 8 corners of the cuboid
        vertices = [
            [x, y, z],               # 0
            [x + dx, y, z],          # 1
            [x + dx, y + dy, z],     # 2
            [x, y + dy, z],          # 3
            [x, y, z + dz],          # 4
            [x + dx, y, z + dz],     # 5
            [x + dx, y + dy, z + dz],# 6
            [x, y + dy, z + dz]      # 7
        ]

        # Triangles to cover all 6 faces (12 total)
        I = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
        J = [1, 3, 2, 5, 3, 6, 0, 7, 5, 7, 6, 4]
        K = [3, 2, 5, 2, 6, 3, 7, 4, 7, 6, 4, 0]


        x_vals = [v[0] for v in vertices]
        y_vals = [v[1] for v in vertices]
        z_vals = [v[2] for v in vertices]

        fig.add_trace(go.Mesh3d(
            x=x_vals,
            y=y_vals,
            z=z_vals,
            i=I, j=J, k=K,
            color=colors[i],
            opacity=1,
            name=box_name,
            hovertext=f"{box_name}<br>Pos: {placement.position}<br>Size: {placement.rotation}",
            hoverinfo='text'
        ))

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title='Length (X)',
            yaxis_title='Width (Y)',
            zaxis_title='Height (Z)',
            aspectmode='data',
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False
    )

    fig.show()
