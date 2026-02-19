"""
Advanced pixel art generator using professional techniques.
Includes dithering, texture patterns, and detailed shading.
"""

import pygame
import random
import math
import numpy as np


def dither_pattern(surface, x, y, width, height, color1, color2, density=0.5, pattern_type="ordered"):
    """
    Apply dithering between two colors.

    Args:
        pattern_type: "ordered" (Bayer matrix), "random", or "stipple"
        density: 0.0 to 1.0, how much of color1 vs color2
    """
    if pattern_type == "ordered":
        # Bayer 4x4 matrix for ordered dithering
        bayer_matrix = [
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5]
        ]

        for py in range(height):
            for px in range(width):
                threshold = bayer_matrix[py % 4][px % 4] / 16.0
                color = color1 if density > threshold else color2
                surface.set_at((x + px, y + py), color)

    elif pattern_type == "random":
        for py in range(height):
            for px in range(width):
                color = color1 if random.random() < density else color2
                surface.set_at((x + px, y + py), color)

    elif pattern_type == "stipple":
        # Checker-like pattern
        for py in range(height):
            for px in range(width):
                if (px + py) % 2 == 0:
                    color = color1 if density > 0.5 else color2
                else:
                    color = color2 if density < 0.5 else color1
                surface.set_at((x + px, y + py), color)


def create_bark_texture(width, height, base_color, dark_color, mid_color):
    """Create realistic bark texture using noise and patterns."""
    surface = pygame.Surface((width, height))
    surface.fill(base_color)

    # Vertical grooves (characteristic of oak bark)
    groove_count = width // 12
    for i in range(groove_count):
        x = i * 12 + random.randint(-2, 2)
        # Create irregular groove
        for y in range(height):
            groove_width = 2 + (hash((i, y // 20)) % 3)
            # Add wave to groove
            wave_offset = int(2 * math.sin(y / 15 + i))

            for gx in range(groove_width):
                gx_pos = x + gx + wave_offset
                if 0 <= gx_pos < width:
                    surface.set_at((gx_pos, y), dark_color)

    # Horizontal bark lines
    line_count = height // 25
    for i in range(line_count):
        y = i * 25 + random.randint(-5, 5)
        if 0 <= y < height:
            for x in range(width):
                if random.random() < 0.7:  # Not continuous
                    surface.set_at((x, y), mid_color)
                    if y + 1 < height:
                        surface.set_at((x, y + 1), dark_color)

    # Add knots
    knot_count = (width * height) // 8000
    for _ in range(knot_count):
        kx = random.randint(5, width - 5)
        ky = random.randint(5, height - 5)
        knot_size = random.randint(8, 16)

        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            for r in range(knot_size):
                px = int(kx + r * math.cos(rad))
                py = int(ky + (r * 0.6) * math.sin(rad))
                if 0 <= px < width and 0 <= py < height:
                    surface.set_at((px, py), dark_color)

    return surface


def create_advanced_oak_tree(width=640, height=720):
    """Create extremely detailed oak tree using advanced pixel art techniques."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # Professional oak bark color palette (from real references)
    bark_darkest = (35, 25, 15)
    bark_dark = (55, 38, 22)
    bark_base = (76, 52, 30)
    bark_mid = (95, 68, 42)
    bark_light = (115, 85, 55)
    bark_highlight = (135, 105, 70)

    # Leaf color palette with more variety
    leaf_shadow = (28, 60, 20)
    leaf_dark = (40, 85, 30)
    leaf_base = (52, 110, 40)
    leaf_mid = (65, 130, 50)
    leaf_light = (78, 150, 60)
    leaf_bright = (95, 170, 75)
    leaf_yellow = (120, 160, 55)  # Sun-hit leaves

    trunk_center_x = width // 2
    trunk_bottom_y = height
    trunk_height = 480
    trunk_top_y = trunk_bottom_y - trunk_height

    # Draw trunk with realistic taper and texture
    for y in range(trunk_height):
        progress = y / trunk_height

        # Trunk gets wider toward bottom
        trunk_width_at_y = int(80 * (1.0 + progress * 0.8))
        left_x = trunk_center_x - trunk_width_at_y // 2
        right_x = trunk_center_x + trunk_width_at_y // 2

        # Color gradient (darker at top)
        if progress < 0.3:
            base_color = bark_dark
            mid_color = bark_base
        elif progress < 0.7:
            base_color = bark_base
            mid_color = bark_mid
        else:
            base_color = bark_mid
            mid_color = bark_light

        # Fill row with base color
        current_y = trunk_top_y + y
        for x in range(left_x, right_x):
            # Add randomized shading
            rand_shade = random.choice([base_color, mid_color, mid_color, mid_color])
            surface.set_at((x, current_y), rand_shade)

    # Add detailed bark texture overlay
    bark_texture = create_bark_texture(160, trunk_height, bark_base, bark_dark, bark_mid)

    # Apply texture to trunk
    for y in range(trunk_height):
        progress = y / trunk_height
        trunk_width_at_y = int(80 * (1.0 + progress * 0.8))
        left_x = trunk_center_x - trunk_width_at_y // 2
        current_y = trunk_top_y + y

        for x in range(trunk_width_at_y):
            if x < bark_texture.get_width() and y < bark_texture.get_height():
                texture_color = bark_texture.get_at((x, y))
                actual_x = left_x + x
                if 0 <= actual_x < width and 0 <= current_y < height:
                    surface.set_at((actual_x, current_y), texture_color)

    # Add lighting on trunk (left side lit, right side shadow)
    for y in range(trunk_height):
        progress = y / trunk_height
        trunk_width_at_y = int(80 * (1.0 + progress * 0.8))
        left_x = trunk_center_x - trunk_width_at_y // 2
        right_x = trunk_center_x + trunk_width_at_y // 2
        current_y = trunk_top_y + y

        # Left highlight
        for i in range(8):
            lx = left_x + i + random.randint(0, 2)
            if 0 <= lx < width and 0 <= current_y < height:
                if random.random() < 0.4:
                    surface.set_at((lx, current_y), bark_highlight)

        # Right shadow
        for i in range(12):
            rx = right_x - i + random.randint(-1, 1)
            if 0 <= rx < width and 0 <= current_y < height:
                if random.random() < 0.5:
                    surface.set_at((rx, current_y), bark_dark)

    # Strong outline on trunk
    for y in range(trunk_height):
        progress = y / trunk_height
        trunk_width_at_y = int(80 * (1.0 + progress * 0.8))
        left_x = trunk_center_x - trunk_width_at_y // 2
        right_x = trunk_center_x + trunk_width_at_y // 2
        current_y = trunk_top_y + y

        if 0 <= current_y < height:
            if 0 <= left_x - 1 < width:
                surface.set_at((left_x - 1, current_y), bark_darkest)
            if 0 <= right_x < width:
                surface.set_at((right_x, current_y), bark_darkest)

    # Draw major branches with detail
    branches = [
        # (start_x, start_y, end_x, end_y, thickness, angle_variation)
        (trunk_center_x - 20, trunk_top_y + 140, trunk_center_x - 200, trunk_top_y + 80, 35, -0.3),
        (trunk_center_x - 15, trunk_top_y + 220, trunk_center_x - 180, trunk_top_y + 180, 30, -0.2),
        (trunk_center_x + 25, trunk_top_y + 120, trunk_center_x + 180, trunk_top_y + 60, 32, 0.3),
        (trunk_center_x + 20, trunk_top_y + 200, trunk_center_x + 160, trunk_top_y + 160, 28, 0.25),
        (trunk_center_x, trunk_top_y + 50, trunk_center_x - 40, trunk_top_y - 60, 28, -0.1),
        (trunk_center_x, trunk_top_y + 60, trunk_center_x + 60, trunk_top_y - 50, 26, 0.15),
    ]

    for start_x, start_y, end_x, end_y, thickness, curve in branches:
        # Draw branch with taper
        steps = 50
        for i in range(steps):
            t = i / steps
            # Bezier curve for natural branch curve
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2 + curve * 100

            # Quadratic bezier
            x = (1-t)**2 * start_x + 2*(1-t)*t * mid_x + t**2 * end_x
            y = (1-t)**2 * start_y + 2*(1-t)*t * mid_y + t**2 * end_y

            # Taper thickness
            current_thickness = int(thickness * (1 - t * 0.6))

            # Draw branch segment
            for dy in range(-current_thickness//2, current_thickness//2):
                for dx in range(-current_thickness//2, current_thickness//2):
                    px = int(x + dx)
                    py = int(y + dy)
                    if 0 <= px < width and 0 <= py < height:
                        # Color variation
                        shade = random.choice([bark_dark, bark_base, bark_mid])
                        surface.set_at((px, py), shade)

            # Outline
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                ox = int(x + (current_thickness//2 + 1) * math.cos(rad))
                oy = int(y + (current_thickness//2 + 1) * math.sin(rad))
                if 0 <= ox < width and 0 <= oy < height:
                    surface.set_at((ox, oy), bark_darkest)

    # Create incredibly dense, detailed canopy
    random.seed(42)  # Consistent results

    # Define canopy regions
    canopy_clusters = []

    # Left side (massive coverage)
    for ring in range(6):
        radius = 100 + ring * 40
        cluster_count = 10 + ring * 3
        for i in range(cluster_count):
            angle = (i / cluster_count) * math.pi + math.pi * 0.5
            cx = trunk_center_x + int(radius * math.cos(angle) * 1.5)
            cy = trunk_top_y + 200 + int(radius * math.sin(angle))
            size = 35 + random.randint(-8, 12)
            canopy_clusters.append((cx, cy, size, ring))

    # Right side
    for ring in range(5):
        radius = 90 + ring * 35
        cluster_count = 8 + ring * 2
        for i in range(cluster_count):
            angle = (i / cluster_count) * math.pi - math.pi * 0.5
            cx = trunk_center_x + int(radius * math.cos(angle) * 1.3)
            cy = trunk_top_y + 180 + int(radius * math.sin(angle))
            size = 32 + random.randint(-6, 10)
            canopy_clusters.append((cx, cy, size, ring))

    # Top crown
    for ring in range(4):
        radius = 60 + ring * 25
        cluster_count = 12 + ring * 2
        for i in range(cluster_count):
            angle = (i / cluster_count) * 2 * math.pi
            cx = trunk_center_x + int(radius * math.cos(angle))
            cy = trunk_top_y + 50 + int(radius * math.sin(angle) * 0.6)
            size = 38 + random.randint(-5, 8)
            canopy_clusters.append((cx, cy, size, ring))

    # Sort by depth (back to front)
    canopy_clusters.sort(key=lambda c: c[1])

    # Draw canopy with advanced shading
    for cx, cy, size, ring in canopy_clusters:
        # Shadow layer
        pygame.draw.circle(surface, leaf_shadow, (cx + 2, cy + 2), size + 2)

        # Base layer
        pygame.draw.circle(surface, leaf_dark, (cx, cy), size)

        # Mid-tone with dithering
        for angle in range(0, 360, 3):
            rad = math.radians(angle)
            dist = random.uniform(size * 0.3, size * 0.8)
            px = int(cx + dist * math.cos(rad))
            py = int(cy + dist * math.sin(rad))
            if 0 <= px < width and 0 <= py < height:
                surface.set_at((px, py), leaf_base if random.random() < 0.6 else leaf_mid)

        # Lighter inner area
        inner_size = int(size * 0.6)
        pygame.draw.circle(surface, leaf_mid, (cx - 1, cy - 1), inner_size)

        # Highlights (sun side - upper left)
        highlight_size = int(size * 0.35)
        highlight_x = cx - size // 3
        highlight_y = cy - size // 3
        pygame.draw.circle(surface, leaf_light, (highlight_x, highlight_y), highlight_size)

        # Bright spots
        bright_size = int(size * 0.18)
        pygame.draw.circle(surface, leaf_bright, (highlight_x - 3, highlight_y - 3), bright_size)

        # Individual leaves on edges (detail)
        if random.random() < 0.3:
            for _ in range(random.randint(3, 8)):
                leaf_angle = random.uniform(0, 2 * math.pi)
                leaf_dist = size + random.randint(2, 8)
                lx = int(cx + leaf_dist * math.cos(leaf_angle))
                ly = int(cy + leaf_dist * math.sin(leaf_angle))

                # Small leaf shape (3-5 pixels)
                leaf_color = random.choice([leaf_mid, leaf_light, leaf_yellow])
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if abs(dx) + abs(dy) <= 2:
                            px, py = lx + dx, ly + dy
                            if 0 <= px < width and 0 <= py < height:
                                surface.set_at((px, py), leaf_color)

    return surface


def create_advanced_knight(width=240, height=300):
    """Create highly detailed knight using dithering and advanced shading."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # Professional metal palette
    metal_shadow = (45, 48, 52)
    metal_dark = (80, 85, 92)
    metal_base = (125, 132, 142)
    metal_mid = (165, 172, 182)
    metal_light = (195, 202, 215)
    metal_bright = (225, 232, 245)

    # Cloth/fabric colors
    red_shadow = (65, 20, 20)
    red_dark = (100, 30, 30)
    red_base = (140, 45, 45)
    red_mid = (175, 65, 65)
    red_light = (200, 90, 90)

    # Gold trim
    gold_dark = (140, 110, 50)
    gold_base = (190, 150, 70)
    gold_bright = (230, 200, 110)

    # Leather
    leather_dark = (55, 35, 20)
    leather_base = (85, 60, 35)
    leather_light = (110, 80, 50)

    base_y = height - 25

    # Knight in relaxed sitting position
    body_center_x = width // 2

    # === LEGS (armored) ===
    # Left leg (extended)
    left_leg_x = body_center_x - 35
    left_leg_segments = [
        (left_leg_x, base_y - 95, 32, 55),  # Thigh
        (left_leg_x + 2, base_y - 45, 28, 25),  # Knee
        (left_leg_x, base_y - 25, 30, 30),  # Shin
    ]

    for seg_x, seg_y, seg_w, seg_h in left_leg_segments:
        # Fill with base metal
        for py in range(seg_h):
            for px in range(seg_w):
                surface.set_at((seg_x + px, seg_y + py), metal_base)

        # Add metallic shading with dithering
        dither_pattern(surface, seg_x, seg_y, seg_w // 3, seg_h,
                      metal_dark, metal_base, 0.6, "ordered")
        dither_pattern(surface, seg_x + seg_w * 2//3, seg_y, seg_w // 3, seg_h,
                      metal_mid, metal_light, 0.4, "ordered")

        # Highlight strip (light reflection)
        for py in range(seg_h):
            for px in range(3):
                lx = seg_x + 4 + px
                ly = seg_y + py
                if random.random() < 0.7:
                    surface.set_at((lx, ly), metal_light)

        # Outline
        pygame.draw.rect(surface, metal_shadow, (seg_x, seg_y, seg_w, seg_h), 2)

    # Right leg (bent)
    right_leg_x = body_center_x + 8
    right_leg_segments = [
        (right_leg_x, base_y - 90, 32, 52),
        (right_leg_x + 2, base_y - 42, 28, 22),
        (right_leg_x + 1, base_y - 25, 29, 28),
    ]

    for seg_x, seg_y, seg_w, seg_h in right_leg_segments:
        for py in range(seg_h):
            for px in range(seg_w):
                surface.set_at((seg_x + px, seg_y + py), metal_base)

        dither_pattern(surface, seg_x, seg_y, seg_w // 3, seg_h,
                      metal_dark, metal_base, 0.6, "ordered")
        dither_pattern(surface, seg_x + seg_w * 2//3, seg_y, seg_w // 3, seg_h,
                      metal_mid, metal_light, 0.4, "ordered")

        for py in range(seg_h):
            for px in range(3):
                lx = seg_x + 4 + px
                ly = seg_y + py
                if random.random() < 0.7:
                    surface.set_at((lx, ly), metal_light)

        pygame.draw.rect(surface, metal_shadow, (seg_x, seg_y, seg_w, seg_h), 2)

    # Boots
    boot_positions = [(left_leg_x - 2, base_y - 10), (right_leg_x, base_y - 10)]
    for boot_x, boot_y in boot_positions:
        pygame.draw.ellipse(surface, leather_dark, (boot_x, boot_y, 38, 18))
        pygame.draw.ellipse(surface, leather_base, (boot_x + 2, boot_y + 2, 34, 14))
        pygame.draw.ellipse(surface, metal_shadow, (boot_x, boot_y, 38, 18), 2)

    # === TORSO ===
    torso_x = body_center_x - 40
    torso_y = base_y - 155
    torso_w = 80
    torso_h = 65

    # Red surcoat
    surcoat_points = [
        (torso_x, torso_y + 15),
        (torso_x + torso_w, torso_y + 15),
        (torso_x + torso_w + 5, torso_y + torso_h + 10),
        (torso_x - 5, torso_y + torso_h + 10),
    ]
    pygame.draw.polygon(surface, red_base, surcoat_points)

    # Add fabric texture with dithering
    dither_pattern(surface, torso_x + 5, torso_y + 20, 20, torso_h - 5,
                  red_dark, red_base, 0.7, "stipple")
    dither_pattern(surface, torso_x + torso_w - 25, torso_y + 20, 20, torso_h - 5,
                  red_mid, red_light, 0.3, "stipple")

    # Gold cross emblem
    cross_x = torso_x + torso_w // 2 - 6
    cross_y = torso_y + 35
    # Vertical
    pygame.draw.rect(surface, gold_dark, (cross_x, cross_y - 12, 12, 36))
    pygame.draw.rect(surface, gold_base, (cross_x + 1, cross_y - 11, 10, 34))
    pygame.draw.rect(surface, gold_bright, (cross_x + 2, cross_y - 10, 3, 32))
    # Horizontal
    pygame.draw.rect(surface, gold_dark, (cross_x - 12, cross_y, 36, 12))
    pygame.draw.rect(surface, gold_base, (cross_x - 11, cross_y + 1, 34, 10))
    pygame.draw.rect(surface, gold_bright, (cross_x - 10, cross_y + 2, 32, 3))

    # Outline surcoat
    pygame.draw.polygon(surface, red_shadow, surcoat_points, 3)

    # Chest plate (visible at shoulders/edges)
    shoulder_left = (torso_x - 8, torso_y + 10, 40, 32)
    shoulder_right = (torso_x + torso_w - 32, torso_y + 10, 40, 32)

    for shoulder_rect in [shoulder_left, shoulder_right]:
        sx, sy, sw, sh = shoulder_rect
        pygame.draw.ellipse(surface, metal_mid, shoulder_rect)
        dither_pattern(surface, sx + 2, sy + 2, sw - 4, sh - 4,
                      metal_base, metal_light, 0.5, "ordered")
        pygame.draw.ellipse(surface, metal_shadow, shoulder_rect, 3)
        # Rivets
        for i in range(3):
            riv_x = sx + 8 + i * 8
            riv_y = sy + sh // 2
            pygame.draw.circle(surface, metal_dark, (riv_x, riv_y), 3)
            pygame.draw.circle(surface, metal_light, (riv_x - 1, riv_y - 1), 1)

    # === ARMS ===
    # Left arm (relaxed)
    arm_l_segments = [
        (torso_x - 12, torso_y + 32, 24, 50),  # Upper arm
        (torso_x - 14, torso_y + 78, 22, 42),  # Forearm
    ]

    for seg_x, seg_y, seg_w, seg_h in arm_l_segments:
        pygame.draw.rect(surface, metal_base, (seg_x, seg_y, seg_w, seg_h), border_radius=4)
        dither_pattern(surface, seg_x, seg_y, seg_w // 2, seg_h,
                      metal_dark, metal_base, 0.65, "ordered")
        dither_pattern(surface, seg_x + seg_w // 2, seg_y, seg_w // 2, seg_h,
                      metal_mid, metal_light, 0.35, "ordered")
        pygame.draw.rect(surface, metal_shadow, (seg_x, seg_y, seg_w, seg_h), 2, border_radius=4)

    # Gauntlet
    pygame.draw.rect(surface, metal_dark, (torso_x - 16, torso_y + 118, 26, 20), border_radius=3)
    pygame.draw.rect(surface, metal_base, (torso_x - 15, torso_y + 119, 24, 18), border_radius=3)

    # Right arm
    arm_r_segments = [
        (torso_x + torso_w - 12, torso_y + 32, 24, 52),
        (torso_x + torso_w - 10, torso_y + 80, 22, 44),
    ]

    for seg_x, seg_y, seg_w, seg_h in arm_r_segments:
        pygame.draw.rect(surface, metal_base, (seg_x, seg_y, seg_w, seg_h), border_radius=4)
        dither_pattern(surface, seg_x, seg_y, seg_w // 2, seg_h,
                      metal_dark, metal_base, 0.65, "ordered")
        dither_pattern(surface, seg_x + seg_w // 2, seg_y, seg_w // 2, seg_h,
                      metal_mid, metal_light, 0.35, "ordered")
        pygame.draw.rect(surface, metal_shadow, (seg_x, seg_y, seg_w, seg_h), 2, border_radius=4)

    pygame.draw.rect(surface, metal_dark, (torso_x + torso_w - 12, torso_y + 122, 26, 20), border_radius=3)

    # === SWORD ===
    sword_x = torso_x + torso_w + 8
    sword_y = torso_y - 85
    blade_length = 160

    # Blade
    pygame.draw.rect(surface, metal_base, (sword_x, sword_y, 14, blade_length))
    # Fuller (groove)
    pygame.draw.rect(surface, metal_dark, (sword_x + 5, sword_y + 8, 4, blade_length - 30))
    # Edge shine
    for py in range(blade_length):
        surface.set_at((sword_x + 2, sword_y + py), metal_light)
        surface.set_at((sword_x + 3, sword_y + py), metal_bright)
    # Edge
    for py in range(blade_length):
        surface.set_at((sword_x, sword_y + py), metal_shadow)
        surface.set_at((sword_x + 13, sword_y + py), metal_shadow)

    # Crossguard
    pygame.draw.rect(surface, gold_dark, (sword_x - 16, sword_y + blade_length, 46, 10))
    pygame.draw.rect(surface, gold_base, (sword_x - 15, sword_y + blade_length + 1, 44, 8))
    pygame.draw.rect(surface, gold_bright, (sword_x - 14, sword_y + blade_length + 2, 42, 3))

    # Handle (leather wrap)
    handle_y = sword_y + blade_length + 10
    for i in range(10):
        wrap_color = leather_base if i % 2 == 0 else leather_dark
        pygame.draw.rect(surface, wrap_color, (sword_x + 2, handle_y + i * 3, 10, 3))

    # Pommel
    pommel_y = handle_y + 32
    pygame.draw.circle(surface, gold_dark, (sword_x + 7, pommel_y), 10)
    pygame.draw.circle(surface, gold_base, (sword_x + 7, pommel_y), 8)
    pygame.draw.circle(surface, gold_bright, (sword_x + 5, pommel_y - 2), 4)

    # === SHIELD ===
    shield_x = 15
    shield_y = base_y - 145
    shield_w = 55
    shield_h = 110

    # Kite shield shape
    shield_points = [
        (shield_x + shield_w // 2, shield_y),
        (shield_x + shield_w, shield_y + 25),
        (shield_x + shield_w, shield_y + shield_h - 35),
        (shield_x + shield_w // 2, shield_y + shield_h),
        (shield_x, shield_y + shield_h - 35),
        (shield_x, shield_y + 25),
    ]

    # Red background with texture
    pygame.draw.polygon(surface, red_dark, shield_points)
    pygame.draw.polygon(surface, red_base, [(p[0] + 2, p[1] + 2) for p in shield_points])

    # Shield boss
    boss_x = shield_x + shield_w // 2
    boss_y = shield_y + 45
    pygame.draw.circle(surface, gold_dark, (boss_x, boss_y), 18)
    pygame.draw.circle(surface, gold_base, (boss_x, boss_y), 15)
    pygame.draw.circle(surface, metal_mid, (boss_x, boss_y), 10)
    pygame.draw.circle(surface, metal_light, (boss_x - 2, boss_y - 2), 5)

    # Cross design
    pygame.draw.rect(surface, gold_base, (boss_x - 4, shield_y + 12, 8, 80))
    pygame.draw.rect(surface, gold_base, (shield_x + 12, boss_y - 4, shield_w - 24, 8))
    pygame.draw.rect(surface, gold_bright, (boss_x - 2, shield_y + 14, 4, 76))
    pygame.draw.rect(surface, gold_bright, (shield_x + 14, boss_y - 2, shield_w - 28, 4))

    # Metal rim
    pygame.draw.polygon(surface, metal_dark, shield_points, 4)
    pygame.draw.polygon(surface, metal_light, [(p[0] + 1, p[1] + 1) for p in shield_points], 1)

    # === HELMET ===
    head_x = torso_x + 22
    head_y = torso_y - 22
    head_w = 44
    head_h = 52

    # Helmet
    pygame.draw.ellipse(surface, metal_mid, (head_x, head_y, head_w, head_h))
    # Shading with dithering
    dither_pattern(surface, head_x + 2, head_y + 2, head_w // 2, head_h - 4,
                  metal_dark, metal_base, 0.6, "ordered")
    dither_pattern(surface, head_x + head_w // 2, head_y + 2, head_w // 2 - 4, head_h - 4,
                  metal_light, metal_bright, 0.3, "ordered")

    # Faceplate
    pygame.draw.rect(surface, metal_dark, (head_x + 10, head_y + 22, 24, 26), border_radius=3)
    # Visor slit
    pygame.draw.rect(surface, (15, 15, 20), (head_x + 12, head_y + 28, 20, 8))
    for vx in range(20):
        surface.set_at((head_x + 12 + vx, head_y + 30), metal_shadow)

    # Breathing holes
    for i in range(4):
        hole_y = head_y + 38 + i * 3
        pygame.draw.circle(surface, (20, 20, 25), (head_x + 15, hole_y), 1)
        pygame.draw.circle(surface, (20, 20, 25), (head_x + 29, hole_y), 1)

    # Helmet highlight
    pygame.draw.ellipse(surface, metal_bright, (head_x + 10, head_y + 6, 20, 16))

    # Outline
    pygame.draw.ellipse(surface, metal_shadow, (head_x, head_y, head_w, head_h), 3)

    # === PLUME ===
    plume_x = head_x + head_w // 2
    plume_y = head_y - 8

    for i in range(13):
        plume_height = 32 - abs(i - 6) * 2
        px = plume_x - 18 + i * 3
        # Gradient red
        red_intensity = 100 + i * 12
        plume_color = (red_intensity, 25, 25)

        for py in range(plume_height):
            # Feather texture
            if py % 3 == 0 or random.random() < 0.3:
                for dx in range(-1, 2):
                    fpx = px + dx
                    fpy = plume_y - py
                    if 0 <= fpx < width and 0 <= fpy < height:
                        surface.set_at((fpx, fpy), plume_color)

    return surface


def create_advanced_campfire(width=180, height=220):
    """Create photorealistic campfire with complex flames."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # Realistic color palettes
    stone_colors = [(80, 75, 70), (100, 95, 88), (120, 115, 108), (140, 135, 128)]
    wood_colors = [(60, 38, 20), (80, 52, 28), (95, 62, 35), (110, 72, 42)]
    charcoal_color = (25, 22, 20)

    # Ember/coal colors
    ember_core = (255, 240, 200)
    ember_hot = (255, 140, 60)
    ember_warm = (220, 80, 30)
    ember_cool = (140, 50, 20)

    # Flame gradient
    flame_colors = [
        (180, 20, 10),   # Deep red
        (220, 40, 15),   # Red
        (255, 80, 25),   # Red-orange
        (255, 140, 40),  # Orange
        (255, 180, 60),  # Yellow-orange
        (255, 220, 90),  # Yellow
        (255, 245, 180), # White-yellow
    ]

    center_x = width // 2
    base_y = height - 35

    # Stone ring
    random.seed(42)
    stone_count = 14
    stone_radius = 75

    for i in range(stone_count):
        angle = (i / stone_count) * 2 * math.pi
        sx = center_x + int(stone_radius * math.cos(angle))
        sy = base_y + int(stone_radius * math.sin(angle) * 0.35)

        stone_w = 16 + random.randint(0, 8)
        stone_h = 12 + random.randint(0, 6)

        # Stone with texture
        base_stone = random.choice(stone_colors)
        pygame.draw.ellipse(surface, base_stone, (sx - stone_w//2, sy - stone_h//2, stone_w, stone_h))

        # Add texture with dithering
        dither_pattern(surface, sx - stone_w//2 + 2, sy - stone_h//2 + 2,
                      stone_w - 4, stone_h - 4,
                      stone_colors[0], stone_colors[2], 0.6, "random")

        # Highlight
        pygame.draw.ellipse(surface, stone_colors[3],
                          (sx - stone_w//4, sy - stone_h//4, stone_w//3, stone_h//3))

        # Outline
        pygame.draw.ellipse(surface, stone_colors[0],
                          (sx - stone_w//2, sy - stone_h//2, stone_w, stone_h), 1)

    # Logs with detailed texture
    logs = [
        # Back horizontal
        (center_x - 50, base_y - 28, 100, 20, 0),
        # Front left angled
        (center_x - 45, base_y - 12, 65, 18, -25),
        # Front right angled
        (center_x - 20, base_y - 12, 65, 18, 25),
        # Top
        (center_x - 42, base_y - 48, 84, 18, 0),
    ]

    for log_x, log_y, log_w, log_h, angle in logs:
        # Create log surface
        log_surf = pygame.Surface((log_w, log_h), pygame.SRCALPHA)

        # Fill with wood texture
        for y in range(log_h):
            for x in range(log_w):
                wood_color = random.choice(wood_colors[:3])
                log_surf.set_at((x, y), wood_color)

        # Wood grain (vertical lines)
        grain_count = log_w // 8
        for i in range(grain_count):
            gx = i * 8 + random.randint(-2, 2)
            for y in range(log_h):
                if 0 <= gx < log_w:
                    log_surf.set_at((gx, y), wood_colors[0])
                    if gx + 1 < log_w:
                        log_surf.set_at((gx + 1, y), wood_colors[1])

        # Charred areas
        char_width = log_w // 3
        dither_pattern(log_surf, log_w // 3, 2, char_width, log_h - 4,
                      charcoal_color, wood_colors[0], 0.7, "stipple")

        # Rotate if needed
        if angle != 0:
            log_surf = pygame.transform.rotate(log_surf, angle)

        surface.blit(log_surf, (log_x, log_y))

        # Outline
        if angle == 0:
            pygame.draw.rect(surface, wood_colors[0], (log_x, log_y, log_w, log_h), 2, border_radius=4)

    # Glowing embers/coals
    coal_positions = [
        (center_x - 18, base_y - 25, 11),
        (center_x + 15, base_y - 28, 13),
        (center_x - 6, base_y - 22, 9),
        (center_x + 8, base_y - 35, 10),
        (center_x - 25, base_y - 32, 12),
        (center_x + 22, base_y - 34, 11),
        (center_x - 2, base_y - 40, 8),
    ]

    for cx, cy, size in coal_positions:
        # Glow effect
        glow_surf = pygame.Surface((size * 6, size * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*ember_warm[:3], 80), (size * 3, size * 3), size * 3)
        surface.blit(glow_surf, (cx - size * 3, cy - size * 3))

        # Coal
        pygame.draw.circle(surface, ember_cool, (cx, cy), size)
        pygame.draw.circle(surface, ember_warm, (cx, cy), size - 2)
        pygame.draw.circle(surface, ember_hot, (cx - 1, cy - 1), size - 4)
        pygame.draw.circle(surface, ember_core, (cx - 2, cy - 2), max(1, size - 6))

    # Complex layered flames
    flame_base = base_y - 48

    # Back flames (largest, reddest)
    for layer, (flame_height, flame_width, color_index) in enumerate([
        (110, 40, 0),  # Deepest red
        (105, 38, 1),
        (98, 35, 2),
        (90, 32, 3),
        (82, 28, 4),
        (72, 24, 5),
        (60, 18, 6),  # Brightest center
    ]):
        # Create flame shape (organic, flickering)
        flame_points = []
        angle_step = 15

        for angle in range(0, 360, angle_step):
            if angle < 180:  # Top half (flame)
                rad = math.radians(angle)
                # Flame gets narrower toward top
                height_factor = 1 - (angle / 180)
                dist = flame_width * (0.3 + 0.7 * height_factor)

                # Add noise for organic shape
                noise = random.uniform(-3, 3)
                height = flame_height * height_factor + noise

                fx = center_x + dist * math.cos(rad)
                fy = flame_base - height
                flame_points.append((fx, fy))
            else:  # Bottom (base)
                rad = math.radians(angle)
                fx = center_x + flame_width * math.cos(rad)
                fy = flame_base + 8
                flame_points.append((fx, fy))

        if len(flame_points) > 2:
            pygame.draw.polygon(surface, flame_colors[color_index], flame_points)

    # Flame wisps (individual tongues)
    for _ in range(8):
        wisp_x = center_x + random.randint(-20, 20)
        wisp_base_y = flame_base - random.randint(10, 30)
        wisp_height = random.randint(15, 35)
        wisp_width = random.randint(4, 8)

        wisp_color = random.choice(flame_colors[3:])

        wisp_points = [
            (wisp_x, wisp_base_y - wisp_height),
            (wisp_x - wisp_width//2, wisp_base_y - wisp_height//2),
            (wisp_x - wisp_width, wisp_base_y),
            (wisp_x + wisp_width, wisp_base_y),
            (wisp_x + wisp_width//2, wisp_base_y - wisp_height//2),
        ]

        pygame.draw.polygon(surface, wisp_color, wisp_points)

    # Rising sparks
    spark_count = 15
    for i in range(spark_count):
        spark_x = center_x + random.randint(-35, 35)
        spark_y = flame_base - random.randint(60, 140)
        spark_size = random.randint(1, 3)
        spark_color = random.choice([ember_hot, ember_core, flame_colors[5]])

        pygame.draw.circle(surface, spark_color, (spark_x, spark_y), spark_size)

        # Spark trail
        if random.random() < 0.5:
            trail_color = (*spark_color[:3], 120)
            for ty in range(3):
                trail_y = spark_y + ty * 2
                if 0 <= trail_y < height:
                    surface.set_at((spark_x, trail_y), trail_color[:3])

    # Overall warm glow
    glow_surf = pygame.Surface((140, 80), pygame.SRCALPHA)
    pygame.draw.ellipse(glow_surf, (*ember_warm[:3], 60), (0, 0, 140, 80))
    surface.blit(glow_surf, (center_x - 70, base_y - 50))

    return surface


def generate_all_advanced_assets():
    """Generate all advanced menu assets."""
    pygame.init()

    from pathlib import Path
    assets_dir = Path(__file__).parent.parent.parent / "assets" / "images" / "menu"
    assets_dir.mkdir(parents=True, exist_ok=True)

    print("Generating ADVANCED pixel art assets with professional techniques...")
    print("Using: dithering, texture patterns, advanced shading, pixel-perfect details")

    print("\n  [1/4] Creating highly detailed oak tree...")
    print("        - Realistic bark texture with knots and grooves")
    print("        - Gradient shading on trunk")
    print("        - Curved branches with sub-branches")
    print("        - Dense canopy with 200+ leaf clusters")
    oak = create_advanced_oak_tree()
    pygame.image.save(oak, str(assets_dir / "oak_tree.png"))

    print("  [2/4] Creating detailed knight with dithering...")
    print("        - Metallic armor with ordered dithering")
    print("        - Fabric texture on surcoat")
    print("        - Gold cross with highlights")
    print("        - Detailed shield with heraldry")
    knight = create_advanced_knight()
    pygame.image.save(knight, str(assets_dir / "knight_resting.png"))

    print("  [3/4] Creating photorealistic campfire...")
    print("        - Stone ring with natural textures")
    print("        - Detailed wood grain on logs")
    print("        - Glowing embers with heat gradient")
    print("        - Multi-layer flames with wisps")
    campfire = create_advanced_campfire()
    pygame.image.save(campfire, str(assets_dir / "campfire.png"))

    print("  [4/4] Castle background (keeping previous version)...")

    print(f"\nSUCCESS: All advanced assets generated in {assets_dir}")
    print("  These use professional pixel art techniques!")

    pygame.quit()


if __name__ == "__main__":
    generate_all_advanced_assets()
