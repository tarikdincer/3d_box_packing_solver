from itertools import permutations
from typing import List, Tuple
import pandas as pd
import random
import matplotlib.pyplot as plt
from visualize import visualize_packing, visualize_dual_packing

# Pallet dimensions in mm
PALLET_LENGTH = 1000
PALLET_WIDTH = 1400
PALLET_HEIGHT = 1400

class Box:
    def __init__(self, name: str, l: int, w: int, h: int):
        self.name = name
        self.dimensions = (l, w, h)
        self.rotations = self.generate_rotations()
    
    def generate_rotations(self) -> List[Tuple[int, int, int]]:
        l, w, h = self.dimensions
        return list(set([
            (l, w, h), (w, l, h), (l, h, w),
            (h, l, w), (w, h, l), (h, w, l)
        ]))
    
class Placement:
    def __init__(self, box: Box, position: Tuple[int, int, int], rotation: Tuple[int, int, int]):
        self.box = box
        self.position = position
        self.rotation = rotation
    
    def __str__(self):
        return (f"Box: {self.box.name:<20} | "
                f"Position (mm): {self.position} | "
                f"Rotation (mm): {self.rotation}")

box_types = [
    Box("BELDOOS", 349, 246, 62),
    Box("DOOS VAN DALE 2", 350, 255, 220),
    Box("DOOSGR", 455, 310, 200),
    Box("DOOSGRS", 455, 300, 200),
    Box("DOOSKL", 455, 300, 135),
    Box("DOOSKLS", 455, 300, 80),
    Box("DOOSMIS", 455, 300, 133),
    Box("IM DOOS GROOT", 375, 260, 130),
    Box("IM DOOS KLEIN", 375, 260, 30),
    Box("IM EDU GROOT", 375, 260, 130),
]

def solve_shelf_packing(boxes: List[Box], pallet_dims: Tuple[int, int, int]) -> List[Placement]:
    pallet_length, pallet_width, pallet_height = pallet_dims

    boxes.sort(key=lambda b: max(r[2] for r in b.rotations), reverse=True)

    placements = []
    current_x = 0 # left-right in shelf
    current_y = 0 # shelf position width
    current_z = 0 # layer height
    max_shelf_height = 0
    max_shelf_width = 0

    for box in boxes:
        placed = False
        
        for rotation in box.rotations:
            l, w, h = rotation
            # if it fits in the current shelf
            if current_x + l <= pallet_length and current_y + w <= pallet_width and current_z + h <= pallet_height:
                placements.append(Placement(box, (current_x, current_y, current_z), rotation))
                current_x += l
                max_shelf_height = max(max_shelf_height, h)
                max_shelf_width = max(max_shelf_width, w)
                placed = True
                break
        
        if not placed:
            # trying a new shelf
            current_x = 0
            current_y += max_shelf_width
            max_shelf_width = 0

            for rotation in box.rotations:
                l, w, h = rotation
                if current_x + l <= pallet_length and current_y + w <= pallet_width and current_z + h <= pallet_height:
                    placements.append(Placement(box, (current_x, current_y, current_z), rotation))
                    current_x += l
                    max_shelf_height = max(max_shelf_height, h)
                    max_shelf_width = max(max_shelf_width, w)
                    placed = True
                    break
        
        if not placed:
            # trying a new layer
            current_x = 0
            current_y = 0
            current_z += max_shelf_height
            max_shelf_height = 0
            max_shelf_width = 0

            for rotation in box.rotations:
                l, w, h = rotation
                if current_x + l <= pallet_length and current_y + w <= pallet_width and current_z + h <= pallet_height:
                    placements.append(Placement(box, (current_x, current_y, current_z), rotation))
                    current_x += l
                    max_shelf_height = max(max_shelf_height, h)
                    max_shelf_width = max(max_shelf_width, w)
                    placed = True
                    break

    return placements

def solve_random_packing(boxes: List[Box], pallet_dims: Tuple[int, int, int], max_attempts_per_box=1000) -> List[Placement]:
    pallet_length, pallet_width, pallet_height = pallet_dims
    placements = []

    def check_overlap(new_pos, new_dim, existing_placements):
        nx, ny, nz = new_pos
        nl, nw, nh = new_dim

        for placement in existing_placements:
            px, py, pz = placement.position
            pl, pw, ph = placement.rotation

            if (nx < px + pl and nx + nl > px and
                ny < py + pw and ny + nw > py and
                nz < pz + ph and nz + nh > pz):
                return True

        return False

    for box in boxes:
        placed = False
        valid_rotations = [r for r in box.rotations if r[0] <= pallet_length and r[1] <= pallet_width and r[2] <= pallet_height]
        if not valid_rotations:
            continue  # go to next box
        for _ in range(max_attempts_per_box):
            rotation = random.choice(valid_rotations)
            l, w, h = rotation

            x = random.randint(0, pallet_length - l)
            y = random.randint(0, pallet_width - w)
            z = random.randint(0, pallet_height - h)

            if not check_overlap((x, y, z), (l, w, h), placements):
                placements.append(Placement(box, (x, y, z), rotation))
                placed = True
                break

        if not placed:
            print(f"Warning: Could not place box {box.name} after {max_attempts_per_box} attempts.")

    return placements


def calculate_wasted_space(placements: List[Placement], pallet_dims: Tuple[int, int, int]) -> Tuple[int, int, float]:
    pallet_length, pallet_width, pallet_height = pallet_dims
    total_pallet_volume = pallet_length * pallet_width * pallet_height

    used_volume = sum(l * w * h for _, (l, w, h) in [(p.box, p.rotation) for p in placements])
    wasted_volume = total_pallet_volume - used_volume
    wasted_percentage = (wasted_volume / total_pallet_volume) * 100

    return used_volume, wasted_volume, wasted_percentage

def calculate_instance_tightness(boxes: List[Box], pallet_dims: Tuple[int, int, int]) -> Tuple[int, float]:
    total_box_volume = sum(l * w * h for box in boxes for (l, w, h) in [box.dimensions])
    pallet_volume = pallet_dims[0] * pallet_dims[1] * pallet_dims[2]
    tightness = total_box_volume / pallet_volume
    return total_box_volume, tightness

def main():
    df = pd.read_csv("orders.csv")
    results = []

    for i, row in df.iterrows():
        boxes = []
        for j, k in enumerate(row):
            for _ in range(k):
                boxes.append(box_types[j])
        
        placements_shelf = solve_shelf_packing(boxes, (PALLET_LENGTH, PALLET_WIDTH, PALLET_HEIGHT))
        placements_random = solve_random_packing(boxes, (PALLET_LENGTH, PALLET_WIDTH, PALLET_HEIGHT), max_attempts_per_box=10)
        
        total_box_vol, tightness = calculate_instance_tightness(boxes, (PALLET_LENGTH, PALLET_WIDTH, PALLET_HEIGHT))
        print('-' * 20)
        print(f"Instance Tightness:\n")
        print(f"Total Box Volume: {total_box_vol} mm³")
        print(f"Pallet Volume: {PALLET_LENGTH * PALLET_WIDTH * PALLET_HEIGHT} mm³")
        print(f"Tightness: {tightness:.4f} ({tightness * 100:.2f}%)")

        print('-' * 20)
        print(f"Statistics for shelf packing:\n")
        for placement in placements_shelf:
            print(placement)

        
        uv_shelf, wv_shelf, wp_shelf = calculate_wasted_space(placements_shelf, (PALLET_LENGTH, PALLET_WIDTH, PALLET_HEIGHT))
        print(f"Used Volume: {uv_shelf} mm³")
        print(f"Wasted Volume: {wv_shelf} mm³")
        print(f"Wasted Space: {wp_shelf:.2f}%")

        print('-' * 20)
        print(f"Statistics for random packing:\n")
        for placement in placements_random:
            print(placement)
        
        uv_random, wv_random, wp_random = calculate_wasted_space(placements_random, (PALLET_LENGTH, PALLET_WIDTH, PALLET_HEIGHT))
        print(f"Used Volume: {uv_random} mm³")
        print(f"Wasted Volume: {wv_random} mm³")
        print(f"Wasted Space: {wp_random:.2f}%")

        # visualize_packing(placements_shelf, title="Shelf Packing Visualization")
        # visualize_packing(placements_random, title="Random Packing Visualization")
        title_shelf = f"Shelf Packing - Wasted: {wp_shelf:.2f}%"
        title_random = f"Random Packing - Wasted: {wp_random:.2f}%"
        visualize_dual_packing(placements_shelf, placements_random, title_shelf, title_random)
        results.append((tightness, wp_shelf, wp_random))
    tightnesses, shelf_ws, random_ws = zip(*results)

    plt.figure(figsize=(10, 6))
    plt.scatter(tightnesses, shelf_ws, label='Shelf Packing', marker='o')
    plt.scatter(tightnesses, random_ws, label='Random Packing', marker='x')
    plt.xlabel('Instance Tightness', fontsize = 16)
    plt.ylabel('Wasted Space (%)', fontsize = 15)
    plt.title('Tightness vs Wasted Space', fontsize = 16)
    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()



if __name__ == '__main__':
    main()
