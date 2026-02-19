"""
Pixel art generator for the main menu background.
Creates a medieval scene with castle, knight, oak tree, and campfire.
"""

import pygame
from pathlib import Path


def create_castle_background(width=1280, height=720):
    """Create a pixel art castle background."""
    surface = pygame.Surface((width, height))

    # Sky gradient (day time, peaceful)
    for y in range(height):
        progress = y / height
        r = int(135 + (200 - 135) * progress)
        g = int(206 + (220 - 206) * progress)
        b = int(235 + (240 - 235) * progress)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

    # Distant mountains (silhouette)
    mountain_color = (100, 120, 140)
    points = [
        (0, height * 0.5),
        (width * 0.2, height * 0.35),
        (width * 0.35, height * 0.42),
        (width * 0.5, height * 0.28),
        (width * 0.65, height * 0.38),
        (width * 0.8, height * 0.32),
        (width, height * 0.45),
        (width, height),
        (0, height)
    ]
    pygame.draw.polygon(surface, mountain_color, points)

    # Castle in the background (mid-distance)
    castle_x = width * 0.6
    castle_y = height * 0.42
    castle_color = (120, 100, 90)
    castle_dark = (90, 75, 65)
    castle_light = (140, 120, 110)

    # Main castle keep (large central tower)
    keep_width = 140
    keep_height = 180
    keep_x = castle_x - keep_width // 2
    keep_y = castle_y
    pygame.draw.rect(surface, castle_color, (keep_x, keep_y, keep_width, keep_height))
    pygame.draw.rect(surface, castle_dark, (keep_x, keep_y, keep_width, keep_height), 3)

    # Battlements on keep
    for i in range(5):
        battlement_x = keep_x + i * 28
        pygame.draw.rect(surface, castle_light, (battlement_x, keep_y - 10, 20, 15))

    # Left tower
    left_tower_x = keep_x - 60
    left_tower_y = keep_y + 40
    pygame.draw.rect(surface, castle_dark, (left_tower_x, left_tower_y, 50, 140))
    # Cone roof
    pygame.draw.polygon(surface, (150, 70, 70), [
        (left_tower_x + 25, left_tower_y - 30),
        (left_tower_x - 5, left_tower_y),
        (left_tower_x + 55, left_tower_y)
    ])

    # Right tower
    right_tower_x = keep_x + keep_width + 10
    right_tower_y = keep_y + 40
    pygame.draw.rect(surface, castle_dark, (right_tower_x, right_tower_y, 50, 140))
    # Cone roof
    pygame.draw.polygon(surface, (150, 70, 70), [
        (right_tower_x + 25, right_tower_y - 30),
        (right_tower_x - 5, right_tower_y),
        (right_tower_x + 55, right_tower_y)
    ])

    # Windows
    window_color = (60, 80, 100)
    for i in range(3):
        for j in range(2):
            win_x = keep_x + 35 + j * 60
            win_y = keep_y + 40 + i * 50
            pygame.draw.rect(surface, window_color, (win_x, win_y, 15, 25))

    # Castle gate
    gate_color = (70, 50, 40)
    gate_x = keep_x + keep_width // 2 - 25
    gate_y = keep_y + keep_height - 60
    pygame.draw.rect(surface, gate_color, (gate_x, gate_y, 50, 60))
    pygame.draw.arc(surface, castle_dark, (gate_x - 5, gate_y - 25, 60, 50), 0, 3.14159, 3)

    # Castle walls extending
    wall_height = 100
    # Left wall
    pygame.draw.rect(surface, castle_color, (left_tower_x - 100, castle_y + 80, 100, wall_height))
    # Right wall
    pygame.draw.rect(surface, castle_color, (right_tower_x + 50, castle_y + 80, 100, wall_height))

    # Flags on towers
    flag_color = (200, 50, 50)
    # Left flag
    pygame.draw.rect(surface, (100, 80, 70), (left_tower_x + 20, left_tower_y - 60, 4, 35))
    pygame.draw.polygon(surface, flag_color, [
        (left_tower_x + 24, left_tower_y - 58),
        (left_tower_x + 50, left_tower_y - 48),
        (left_tower_x + 24, left_tower_y - 38)
    ])
    # Right flag
    pygame.draw.rect(surface, (100, 80, 70), (right_tower_x + 20, right_tower_y - 60, 4, 35))
    pygame.draw.polygon(surface, flag_color, [
        (right_tower_x + 24, right_tower_y - 58),
        (right_tower_x + 50, right_tower_y - 48),
        (right_tower_x + 24, right_tower_y - 38)
    ])

    # Ground/grass in middle distance
    grass_y = height * 0.55
    pygame.draw.rect(surface, (100, 150, 80), (0, grass_y, width, height - grass_y))

    # Add some grass texture
    grass_dark = (85, 130, 70)
    for i in range(0, width, 8):
        for j in range(int(grass_y), height, 8):
            if (i + j) % 16 == 0:
                pygame.draw.circle(surface, grass_dark, (i, j), 2)

    return surface


def create_oak_tree(width=800, height=720):
    """Create a massive, detailed pixel art oak tree that fills half the screen."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # More realistic colors
    trunk_base = (76, 47, 24)
    trunk_mid = (101, 67, 33)
    trunk_light = (120, 85, 50)
    trunk_dark = (55, 35, 18)
    bark_detail = (90, 60, 30)
    bark_shadow = (45, 28, 14)

    # Massive trunk
    trunk_x = width // 2 - 80
    trunk_width = 160
    trunk_height = 500
    trunk_y = height - trunk_height

    # Draw trunk base with gradient effect
    for y in range(trunk_height):
        progress = y / trunk_height
        # Gradient from darker at top to lighter at bottom
        r = int(trunk_dark[0] + (trunk_base[0] - trunk_dark[0]) * progress)
        g = int(trunk_dark[1] + (trunk_base[1] - trunk_dark[1]) * progress)
        b = int(trunk_dark[2] + (trunk_base[2] - trunk_dark[2]) * progress)

        # Make trunk wider at base
        width_mult = 1.0 + (progress * 0.4)
        current_width = int(trunk_width * width_mult)
        offset = (current_width - trunk_width) // 2

        pygame.draw.line(surface, (r, g, b),
                        (trunk_x - offset, trunk_y + y),
                        (trunk_x + trunk_width + offset, trunk_y + y), 2)

    # Detailed bark texture with knots and grooves
    for i in range(15):
        bark_y = trunk_y + i * 35 + 20
        # Vertical grooves
        groove_x = trunk_x + 30 + (i % 3) * 40
        for j in range(8):
            offset_y = bark_y + j * 5
            groove_color = bark_shadow if j % 2 == 0 else bark_detail
            pygame.draw.circle(surface, groove_color, (groove_x, offset_y), 3)

        # Horizontal bark lines
        if i % 2 == 0:
            pygame.draw.line(surface, bark_detail,
                           (trunk_x + 15, bark_y),
                           (trunk_x + trunk_width - 15, bark_y), 4)
            pygame.draw.line(surface, bark_shadow,
                           (trunk_x + 15, bark_y + 2),
                           (trunk_x + trunk_width - 15, bark_y + 2), 2)

    # Knots in trunk
    knot_positions = [
        (trunk_x + 45, trunk_y + 120, 18),
        (trunk_x + 100, trunk_y + 200, 22),
        (trunk_x + 60, trunk_y + 320, 16),
        (trunk_x + 110, trunk_y + 380, 20),
    ]
    for kx, ky, size in knot_positions:
        pygame.draw.ellipse(surface, trunk_dark, (kx - size, ky - size//2, size * 2, size))
        pygame.draw.ellipse(surface, bark_shadow, (kx - size//2, ky - size//3, size, size//1.5))

    # Massive branch system
    branch_data = [
        # Left major branches
        ((trunk_x + 30, trunk_y + 120), (trunk_x - 180, trunk_y + 60), 45, True),
        ((trunk_x + 25, trunk_y + 200), (trunk_x - 200, trunk_y + 150), 38, True),
        ((trunk_x + 20, trunk_y + 280), (trunk_x - 150, trunk_y + 240), 35, True),
        # Right major branches
        ((trunk_x + 130, trunk_y + 100), (trunk_x + 320, trunk_y + 40), 42, False),
        ((trunk_x + 135, trunk_y + 180), (trunk_x + 280, trunk_y + 130), 40, False),
        ((trunk_x + 140, trunk_y + 250), (trunk_x + 260, trunk_y + 210), 36, False),
        # Top branches
        ((trunk_x + 80, trunk_y + 40), (trunk_x + 50, trunk_y - 80), 32, True),
        ((trunk_x + 80, trunk_y + 50), (trunk_x + 150, trunk_y - 60), 30, False),
    ]

    for start, end, thickness, is_left in branch_data:
        # Draw main branch
        pygame.draw.line(surface, trunk_mid, start, end, thickness)
        pygame.draw.line(surface, trunk_dark, start, end, max(3, thickness // 10))

        # Add smaller sub-branches
        mid_x = (start[0] + end[0]) // 2
        mid_y = (start[1] + end[1]) // 2

        # Sub-branch 1
        sub_offset = 60 if is_left else -60
        pygame.draw.line(surface, trunk_mid,
                        (mid_x, mid_y),
                        (mid_x + sub_offset, mid_y - 40),
                        thickness // 2)

        # Sub-branch 2
        sub_offset2 = 80 if is_left else -80
        pygame.draw.line(surface, trunk_mid,
                        (end[0], end[1]),
                        (end[0] + sub_offset2, end[1] - 50),
                        thickness // 3)

    # Massive, detailed canopy with many leaf clusters
    leaf_base = (52, 110, 40)
    leaf_mid = (65, 130, 50)
    leaf_light = (78, 150, 60)
    leaf_highlight = (95, 170, 75)
    leaf_shadow = (40, 90, 30)

    # Create dense canopy coverage
    canopy_clusters = []

    # Left side canopy (dense coverage)
    for i in range(8):
        for j in range(6):
            x = trunk_x - 250 + i * 60 + (j % 2) * 30
            y = 80 + j * 65 + (i % 2) * 20
            radius = 45 + (i * j % 15)
            canopy_clusters.append((x, y, radius, 1))

    # Right side canopy
    for i in range(6):
        for j in range(6):
            x = trunk_x + 180 + i * 55 + (j % 2) * 25
            y = 60 + j * 70 + (i % 2) * 15
            radius = 42 + (i * j % 12)
            canopy_clusters.append((x, y, radius, 1))

    # Top canopy (crown)
    for i in range(5):
        for j in range(4):
            x = trunk_x + 20 + i * 50 + (j % 2) * 20
            y = 20 + j * 55
            radius = 50 + (i * j % 10)
            canopy_clusters.append((x, y, radius, 2))

    # Draw canopy in layers for depth
    # Layer 1: Dark shadows
    for x, y, radius, layer in canopy_clusters:
        pygame.draw.circle(surface, leaf_shadow, (x, y), radius + 4)

    # Layer 2: Base color
    for x, y, radius, layer in canopy_clusters:
        pygame.draw.circle(surface, leaf_base, (x, y), radius)

    # Layer 3: Mid-tone
    for x, y, radius, layer in canopy_clusters:
        pygame.draw.circle(surface, leaf_mid, (x - 2, y - 2), radius - 5)

    # Layer 4: Highlights
    for x, y, radius, layer in canopy_clusters[:30]:
        if layer == 2:  # Extra highlight on top layer
            pygame.draw.circle(surface, leaf_highlight, (x - radius//3, y - radius//3), radius // 2)
        else:
            pygame.draw.circle(surface, leaf_light, (x - radius//4, y - radius//4), radius // 3)

    # Add individual leaf details to some clusters
    import random
    random.seed(42)  # Consistent pattern
    for x, y, radius, layer in canopy_clusters[::3]:
        for _ in range(5):
            leaf_x = x + random.randint(-radius//2, radius//2)
            leaf_y = y + random.randint(-radius//2, radius//2)
            pygame.draw.circle(surface, leaf_highlight, (leaf_x, leaf_y), 3)

    return surface


def create_knight(width=220, height=280):
    """Create a detailed pixel art knight resting and leaning back."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # More realistic metallic colors
    armor_base = (140, 145, 150)
    armor_mid = (165, 170, 175)
    armor_light = (200, 205, 215)
    armor_dark = (90, 95, 100)
    armor_shadow = (60, 65, 70)

    cloth_red = (130, 45, 45)
    cloth_red_dark = (90, 30, 30)
    cloth_red_light = (160, 65, 65)

    leather_brown = (95, 65, 40)
    leather_dark = (65, 45, 25)

    gold_color = (210, 180, 90)
    gold_dark = (170, 140, 60)

    skin_color = (220, 180, 150)
    skin_shadow = (180, 140, 110)

    # Knight is leaning back against tree
    base_y = height - 20

    # Legs in relaxed sitting position
    # Left leg (extended forward)
    leg_segments = [
        # Thigh
        (45, base_y - 90, 28, 50, armor_mid),
        # Knee joint
        (45, base_y - 45, 28, 20, armor_dark),
        # Shin
        (42, base_y - 30, 30, 35, armor_base),
    ]

    for x, y, w, h, color in leg_segments:
        pygame.draw.rect(surface, color, (x, y, w, h), border_radius=4)
        pygame.draw.rect(surface, armor_dark, (x, y, w, h), 2, border_radius=4)
        # Metallic shine
        pygame.draw.line(surface, armor_light, (x + 3, y + 5), (x + 3, y + h - 5), 2)

    # Right leg (bent)
    right_leg_segments = [
        (80, base_y - 85, 28, 48, armor_mid),
        (80, base_y - 42, 28, 18, armor_dark),
        (78, base_y - 28, 30, 33, armor_base),
    ]

    for x, y, w, h, color in right_leg_segments:
        pygame.draw.rect(surface, color, (x, y, w, h), border_radius=4)
        pygame.draw.rect(surface, armor_dark, (x, y, w, h), 2, border_radius=4)
        pygame.draw.line(surface, armor_light, (x + 3, y + 5), (x + 3, y + h - 5), 2)

    # Boots
    pygame.draw.ellipse(surface, leather_brown, (38, base_y - 8, 38, 16))
    pygame.draw.ellipse(surface, leather_dark, (38, base_y - 8, 38, 16), 2)
    pygame.draw.ellipse(surface, leather_brown, (74, base_y - 8, 38, 16))
    pygame.draw.ellipse(surface, leather_dark, (74, base_y - 8, 38, 16), 2)

    # Torso (leaning back at angle)
    body_x = 50
    body_y = base_y - 145

    # Surcoat (red cloth over armor)
    surcoat_points = [
        (body_x - 10, body_y + 20),
        (body_x + 70, body_y + 20),
        (body_x + 75, body_y + 85),
        (body_x - 15, body_y + 85),
    ]
    pygame.draw.polygon(surface, cloth_red, surcoat_points)
    pygame.draw.polygon(surface, cloth_red_dark, surcoat_points, 3)

    # Add cross emblem on surcoat
    cross_x = body_x + 28
    cross_y = body_y + 45
    pygame.draw.rect(surface, gold_color, (cross_x, cross_y - 8, 8, 28))
    pygame.draw.rect(surface, gold_color, (cross_x - 8, cross_y + 2, 24, 8))
    pygame.draw.rect(surface, gold_dark, (cross_x, cross_y - 8, 8, 28), 1)
    pygame.draw.rect(surface, gold_dark, (cross_x - 8, cross_y + 2, 24, 8), 1)

    # Chest plate underneath
    pygame.draw.ellipse(surface, armor_mid, (body_x - 5, body_y + 15, 70, 55))
    pygame.draw.ellipse(surface, armor_dark, (body_x - 5, body_y + 15, 70, 55), 3)
    # Plate segments
    for i in range(3):
        y_offset = body_y + 25 + i * 15
        pygame.draw.line(surface, armor_light, (body_x, y_offset), (body_x + 55, y_offset), 2)

    # Belt
    pygame.draw.rect(surface, leather_brown, (body_x - 10, body_y + 75, 75, 12))
    pygame.draw.rect(surface, gold_color, (body_x + 20, body_y + 76, 18, 10))
    pygame.draw.rect(surface, gold_dark, (body_x + 20, body_y + 76, 18, 10), 2)

    # Arms in relaxed position
    # Left arm (resting on leg)
    # Shoulder pauldron
    pygame.draw.ellipse(surface, armor_mid, (body_x - 8, body_y + 18, 35, 28))
    pygame.draw.ellipse(surface, armor_dark, (body_x - 8, body_y + 18, 35, 28), 2)
    pygame.draw.ellipse(surface, armor_light, (body_x - 3, body_y + 20, 15, 12))

    # Upper arm
    pygame.draw.rect(surface, armor_base, (20, body_y + 38, 22, 45), border_radius=5)
    pygame.draw.rect(surface, armor_dark, (20, body_y + 38, 22, 45), 2, border_radius=5)
    # Elbow
    pygame.draw.circle(surface, armor_dark, (31, body_y + 80), 12)
    pygame.draw.circle(surface, armor_mid, (31, body_y + 80), 10)
    # Forearm
    pygame.draw.rect(surface, armor_base, (26, body_y + 85, 20, 38), border_radius=4)
    pygame.draw.rect(surface, armor_dark, (26, body_y + 85, 20, 38), 2, border_radius=4)
    # Gauntlet
    pygame.draw.rect(surface, armor_dark, (24, body_y + 118, 24, 18), border_radius=3)

    # Right arm (relaxed, hand near sword)
    # Shoulder pauldron
    pygame.draw.ellipse(surface, armor_mid, (body_x + 38, body_y + 18, 35, 28))
    pygame.draw.ellipse(surface, armor_dark, (body_x + 38, body_y + 18, 35, 28), 2)
    pygame.draw.ellipse(surface, armor_light, (body_x + 48, body_y + 20, 15, 12))

    # Upper arm
    pygame.draw.rect(surface, armor_base, (body_x + 58, body_y + 38, 22, 48), border_radius=5)
    pygame.draw.rect(surface, armor_dark, (body_x + 58, body_y + 38, 22, 48), 2, border_radius=5)
    # Elbow
    pygame.draw.circle(surface, armor_dark, (body_x + 69, body_y + 83), 12)
    pygame.draw.circle(surface, armor_mid, (body_x + 69, body_y + 83), 10)
    # Forearm
    pygame.draw.rect(surface, armor_base, (body_x + 64, body_y + 88, 20, 40), border_radius=4)
    pygame.draw.rect(surface, armor_dark, (body_x + 64, body_y + 88, 20, 40), 2, border_radius=4)
    # Gauntlet
    pygame.draw.rect(surface, armor_dark, (body_x + 62, body_y + 123, 24, 18), border_radius=3)

    # Sword leaning against shoulder
    sword_blade = (185, 190, 200)
    sword_shine = (220, 225, 235)
    sword_edge = (140, 145, 155)
    sword_handle = (85, 55, 35)
    sword_pommel = (190, 160, 80)

    sword_x = body_x + 72
    sword_y = body_y - 70

    # Blade (long and detailed)
    pygame.draw.rect(surface, sword_blade, (sword_x, sword_y, 12, 140), border_radius=2)
    pygame.draw.rect(surface, sword_edge, (sword_x, sword_y, 12, 140), 2, border_radius=2)
    # Fuller (groove in blade)
    pygame.draw.rect(surface, sword_edge, (sword_x + 4, sword_y + 5, 4, 110))
    # Shine on blade
    pygame.draw.line(surface, sword_shine, (sword_x + 2, sword_y + 10), (sword_x + 2, sword_y + 130), 2)
    # Crossguard
    pygame.draw.rect(surface, gold_color, (sword_x - 12, sword_y + 138, 36, 8))
    pygame.draw.rect(surface, gold_dark, (sword_x - 12, sword_y + 138, 36, 8), 2)
    # Handle (leather wrapped)
    for i in range(8):
        color = leather_brown if i % 2 == 0 else leather_dark
        pygame.draw.rect(surface, color, (sword_x + 2, sword_y + 146 + i * 4, 8, 4))
    # Pommel
    pygame.draw.circle(surface, sword_pommel, (sword_x + 6, sword_y + 182), 8)
    pygame.draw.circle(surface, gold_dark, (sword_x + 6, sword_y + 182), 8, 2)

    # Shield leaning against tree/knight
    shield_x = 8
    shield_y = base_y - 130
    # Kite shield shape
    shield_width = 48
    shield_height = 95

    # Shield background (red)
    shield_points = [
        (shield_x + shield_width // 2, shield_y),
        (shield_x + shield_width, shield_y + 20),
        (shield_x + shield_width, shield_y + shield_height - 25),
        (shield_x + shield_width // 2, shield_y + shield_height),
        (shield_x, shield_y + shield_height - 25),
        (shield_x, shield_y + 20),
    ]
    pygame.draw.polygon(surface, (140, 50, 50), shield_points)
    pygame.draw.polygon(surface, (100, 35, 35), shield_points, 4)

    # Shield boss (center)
    boss_x = shield_x + shield_width // 2
    boss_y = shield_y + 40
    pygame.draw.circle(surface, gold_color, (boss_x, boss_y), 14)
    pygame.draw.circle(surface, gold_dark, (boss_x, boss_y), 14, 2)
    pygame.draw.circle(surface, armor_mid, (boss_x, boss_y), 8)

    # Shield cross design
    pygame.draw.rect(surface, gold_color, (boss_x - 3, shield_y + 10, 6, 70))
    pygame.draw.rect(surface, gold_color, (shield_x + 10, boss_y - 3, shield_width - 20, 6))

    # Shield rim
    pygame.draw.polygon(surface, armor_mid, shield_points, 3)

    # Head/Helmet (detailed)
    head_x = body_x + 15
    head_y = body_y - 15

    # Helmet base
    pygame.draw.ellipse(surface, armor_mid, (head_x, head_y, 38, 45))
    pygame.draw.ellipse(surface, armor_dark, (head_x, head_y, 38, 45), 3)

    # Face guard
    pygame.draw.rect(surface, armor_dark, (head_x + 8, head_y + 18, 22, 22), border_radius=2)
    # Visor slit
    pygame.draw.rect(surface, (30, 30, 40), (head_x + 10, head_y + 24, 18, 6))
    pygame.draw.line(surface, armor_shadow, (head_x + 11, head_y + 26), (head_x + 27, head_y + 26), 2)

    # Breathing holes
    for i in range(3):
        hole_y = head_y + 32 + i * 3
        pygame.draw.circle(surface, (30, 30, 40), (head_x + 13, hole_y), 1)
        pygame.draw.circle(surface, (30, 30, 40), (head_x + 25, hole_y), 1)

    # Helmet shine
    pygame.draw.ellipse(surface, armor_light, (head_x + 8, head_y + 5, 18, 14))

    # Helmet plume (red)
    plume_base_x = head_x + 19
    plume_base_y = head_y - 5
    for i in range(9):
        plume_height = 25 - abs(i - 4) * 2
        plume_x = plume_base_x - 12 + i * 3
        # Gradient from dark to light red
        red_val = 140 + i * 10
        pygame.draw.line(surface, (red_val, 30, 30),
                        (plume_x, plume_base_y),
                        (plume_x - 2 + (i % 2) * 4, plume_base_y - plume_height), 3)

    return surface


def create_campfire(width=160, height=200):
    """Create a detailed pixel art campfire with realistic flames."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # More realistic wood colors
    log_base = (76, 47, 24)
    log_mid = (95, 63, 35)
    log_dark = (55, 35, 18)
    log_end = (110, 75, 42)
    log_highlight = (120, 85, 50)
    bark_texture = (65, 42, 22)
    charred = (30, 25, 20)

    base_y = height - 30
    center_x = width // 2

    # Stone ring around fire
    stone_color = (110, 105, 100)
    stone_dark = (75, 72, 68)
    stone_light = (140, 135, 128)

    # Draw stones in a circle
    import math
    stone_radius = 65
    for i in range(12):
        angle = (i / 12) * 2 * math.pi
        stone_x = center_x + int(math.cos(angle) * stone_radius)
        stone_y = base_y + int(math.sin(angle) * stone_radius * 0.4)

        # Draw stone
        stone_w = 18 + (i % 3) * 4
        stone_h = 14 + (i % 2) * 3
        pygame.draw.ellipse(surface, stone_dark, (stone_x - stone_w//2, stone_y - stone_h//2, stone_w, stone_h))
        pygame.draw.ellipse(surface, stone_color, (stone_x - stone_w//2 + 2, stone_y - stone_h//2 + 2, stone_w - 4, stone_h - 4))
        # Highlight
        pygame.draw.ellipse(surface, stone_light, (stone_x - stone_w//4, stone_y - stone_h//4, stone_w//3, stone_h//3))

    # Logs arranged in crossing pattern
    # Back log (horizontal)
    log1_y = base_y - 20
    pygame.draw.rect(surface, log_mid, (center_x - 45, log1_y, 90, 18), border_radius=4)
    pygame.draw.rect(surface, log_dark, (center_x - 45, log1_y, 90, 18), 2, border_radius=4)
    # Wood grain texture
    for i in range(8):
        grain_x = center_x - 40 + i * 11
        pygame.draw.line(surface, bark_texture, (grain_x, log1_y + 3), (grain_x, log1_y + 15), 1)
    # Log ends
    pygame.draw.ellipse(surface, log_end, (center_x - 50, log1_y + 2, 16, 14))
    pygame.draw.ellipse(surface, log_dark, (center_x - 50, log1_y + 2, 16, 14), 2)
    pygame.draw.ellipse(surface, log_end, (center_x + 34, log1_y + 2, 16, 14))
    pygame.draw.ellipse(surface, log_dark, (center_x + 34, log1_y + 2, 16, 14), 2)

    # Front left log (angled)
    log2_points = [
        (center_x - 35, base_y - 5),
        (center_x - 5, base_y - 25),
        (center_x, base_y - 22),
        (center_x - 30, base_y - 2),
    ]
    pygame.draw.polygon(surface, log_base, log2_points)
    pygame.draw.polygon(surface, log_dark, log2_points, 2)
    # Charred top
    pygame.draw.line(surface, charred, (center_x - 32, base_y - 4), (center_x - 2, base_y - 24), 6)

    # Front right log (angled other way)
    log3_points = [
        (center_x + 35, base_y - 5),
        (center_x + 5, base_y - 25),
        (center_x, base_y - 22),
        (center_x + 30, base_y - 2),
    ]
    pygame.draw.polygon(surface, log_base, log3_points)
    pygame.draw.polygon(surface, log_dark, log3_points, 2)
    # Charred top
    pygame.draw.line(surface, charred, (center_x + 32, base_y - 4), (center_x + 2, base_y - 24), 6)

    # Top log
    log4_y = base_y - 35
    pygame.draw.rect(surface, log_mid, (center_x - 38, log4_y, 76, 16), border_radius=4)
    pygame.draw.rect(surface, log_dark, (center_x - 38, log4_y, 76, 16), 2, border_radius=4)
    # Charred areas
    for i in range(3):
        char_x = center_x - 30 + i * 28
        pygame.draw.ellipse(surface, charred, (char_x, log4_y + 2, 14, 12))

    # Embers/coals between logs
    ember_glow = (255, 120, 40)
    ember_hot = (255, 80, 20)
    ember_dark = (140, 40, 10)

    coal_positions = [
        (center_x - 15, base_y - 18, 8),
        (center_x + 12, base_y - 20, 10),
        (center_x - 5, base_y - 15, 7),
        (center_x + 5, base_y - 28, 6),
        (center_x - 22, base_y - 24, 9),
        (center_x + 20, base_y - 26, 8),
    ]

    for coal_x, coal_y, size in coal_positions:
        pygame.draw.circle(surface, ember_dark, (coal_x, coal_y), size)
        pygame.draw.circle(surface, ember_hot, (coal_x, coal_y), size - 2)
        pygame.draw.circle(surface, ember_glow, (coal_x - 1, coal_y - 1), size - 4)

    # Detailed multi-layer flames
    flame_base = base_y - 35

    # Flame colors from hot to cool
    flame_deep_red = (200, 30, 10)
    flame_red = (255, 60, 20)
    flame_orange = (255, 130, 30)
    flame_yellow_orange = (255, 180, 50)
    flame_yellow = (255, 220, 80)
    flame_white = (255, 250, 200)

    # Back flame (large)
    back_flame = [
        (center_x, flame_base - 95),
        (center_x - 8, flame_base - 80),
        (center_x - 18, flame_base - 65),
        (center_x - 22, flame_base - 45),
        (center_x - 28, flame_base - 25),
        (center_x - 32, flame_base - 5),
        (center_x - 35, flame_base + 5),
        (center_x + 35, flame_base + 5),
        (center_x + 32, flame_base - 5),
        (center_x + 28, flame_base - 25),
        (center_x + 22, flame_base - 45),
        (center_x + 18, flame_base - 65),
        (center_x + 8, flame_base - 80),
    ]
    pygame.draw.polygon(surface, flame_deep_red, back_flame)

    # Middle-back flame
    mid_back_flame = [
        (center_x - 2, flame_base - 88),
        (center_x - 15, flame_base - 70),
        (center_x - 20, flame_base - 50),
        (center_x - 25, flame_base - 30),
        (center_x - 28, flame_base - 10),
        (center_x + 28, flame_base - 10),
        (center_x + 25, flame_base - 30),
        (center_x + 20, flame_base - 50),
        (center_x + 15, flame_base - 70),
        (center_x + 2, flame_base - 88),
    ]
    pygame.draw.polygon(surface, flame_red, mid_back_flame)

    # Middle flame
    mid_flame = [
        (center_x, flame_base - 80),
        (center_x - 12, flame_base - 65),
        (center_x - 18, flame_base - 48),
        (center_x - 22, flame_base - 28),
        (center_x - 24, flame_base - 8),
        (center_x + 24, flame_base - 8),
        (center_x + 22, flame_base - 28),
        (center_x + 18, flame_base - 48),
        (center_x + 12, flame_base - 65),
    ]
    pygame.draw.polygon(surface, flame_orange, mid_flame)

    # Mid-front flame
    mid_front_flame = [
        (center_x, flame_base - 72),
        (center_x - 10, flame_base - 58),
        (center_x - 15, flame_base - 42),
        (center_x - 18, flame_base - 24),
        (center_x - 20, flame_base - 6),
        (center_x + 20, flame_base - 6),
        (center_x + 18, flame_base - 24),
        (center_x + 15, flame_base - 42),
        (center_x + 10, flame_base - 58),
    ]
    pygame.draw.polygon(surface, flame_yellow_orange, mid_front_flame)

    # Front flame (hottest, yellow)
    front_flame = [
        (center_x, flame_base - 65),
        (center_x - 8, flame_base - 52),
        (center_x - 12, flame_base - 38),
        (center_x - 14, flame_base - 22),
        (center_x - 16, flame_base - 6),
        (center_x + 16, flame_base - 6),
        (center_x + 14, flame_base - 22),
        (center_x + 12, flame_base - 38),
        (center_x + 8, flame_base - 52),
    ]
    pygame.draw.polygon(surface, flame_yellow, front_flame)

    # Hot core (white)
    core_flame = [
        (center_x, flame_base - 50),
        (center_x - 6, flame_base - 40),
        (center_x - 8, flame_base - 25),
        (center_x - 10, flame_base - 10),
        (center_x + 10, flame_base - 10),
        (center_x + 8, flame_base - 25),
        (center_x + 6, flame_base - 40),
    ]
    pygame.draw.polygon(surface, flame_white, core_flame)

    # Sparks rising
    import random
    random.seed(42)
    spark_bright = (255, 220, 120)
    spark_dim = (255, 150, 80)

    spark_positions = [
        (center_x - 20, flame_base - 100, 3, spark_bright),
        (center_x + 15, flame_base - 105, 2, spark_bright),
        (center_x - 8, flame_base - 115, 2, spark_dim),
        (center_x + 25, flame_base - 95, 2, spark_dim),
        (center_x - 30, flame_base - 88, 2, spark_dim),
        (center_x + 5, flame_base - 120, 1, spark_bright),
        (center_x - 15, flame_base - 125, 1, spark_dim),
        (center_x + 22, flame_base - 118, 1, spark_dim),
    ]

    for sx, sy, ssize, scolor in spark_positions:
        pygame.draw.circle(surface, scolor, (sx, sy), ssize)
        # Glow around spark
        glow_surf = pygame.Surface((ssize * 6, ssize * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*scolor[:3], 60), (ssize * 3, ssize * 3), ssize * 3)
        surface.blit(glow_surf, (sx - ssize * 3, sy - ssize * 3))

    # Overall warm glow at base
    glow_color = (255, 140, 60, 80)
    glow_surface = pygame.Surface((100, 60), pygame.SRCALPHA)
    pygame.draw.ellipse(glow_surface, glow_color, (0, 0, 100, 60))
    surface.blit(glow_surface, (center_x - 50, base_y - 40))

    return surface


def generate_all_menu_assets():
    """Generate all menu assets and save them."""
    pygame.init()

    assets_dir = Path(__file__).parent.parent.parent / "assets" / "images" / "menu"
    assets_dir.mkdir(parents=True, exist_ok=True)

    print("Generating menu pixel art assets...")

    # Generate castle background
    print("  - Creating castle background...")
    castle_bg = create_castle_background()
    pygame.image.save(castle_bg, str(assets_dir / "castle_background.png"))

    # Generate oak tree
    print("  - Creating oak tree...")
    oak_tree = create_oak_tree()
    pygame.image.save(oak_tree, str(assets_dir / "oak_tree.png"))

    # Generate knight
    print("  - Creating knight...")
    knight = create_knight()
    pygame.image.save(knight, str(assets_dir / "knight_resting.png"))

    # Generate campfire
    print("  - Creating campfire...")
    campfire = create_campfire()
    pygame.image.save(campfire, str(assets_dir / "campfire.png"))

    print(f"All assets generated successfully in {assets_dir}")
    pygame.quit()


if __name__ == "__main__":
    generate_all_menu_assets()
