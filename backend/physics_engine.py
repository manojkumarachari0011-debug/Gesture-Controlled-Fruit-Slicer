import random
import math

class PhysicsEngine:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.gravity = 0.5
        self.fruits = []
        self.sliced_halves = []
        self.fruit_types = ['apple', 'banana', 'orange']

    def spawn_fruit(self, level=1):
        # Higher level = slightly higher bomb probability (capped at 35%)
        bomb_prob = min(0.15 + (level - 1) * 0.05, 0.35)
        is_bomb = random.random() < bomb_prob
        item_type = 'bomb' if is_bomb else random.choice(self.fruit_types)

        # Higher level = higher launch speed
        speed_mult = 1.0 + (level - 1) * 0.15
        base_vy_min = -19 * speed_mult
        base_vy_max = -15 * speed_mult

        item = {
            'x': random.randint(120, self.screen_width - 120),
            'y': self.screen_height + 20,
            'vx': random.uniform(-3.5 * speed_mult, 3.5 * speed_mult),
            'vy': random.uniform(base_vy_min, base_vy_max),
            'type': item_type,
            'is_bomb': is_bomb
        }
        self.fruits.append(item)

    def update_physics(self):
        missed_fruits = 0
        
        for item in self.fruits[:]:
            item['x'] += item['vx']
            item['y'] += item['vy']
            item['vy'] += self.gravity

            if item['y'] > self.screen_height + 60 and item['vy'] > 0:
                self.fruits.remove(item)
                if not item['is_bomb']:
                    missed_fruits += 1

        for half in self.sliced_halves[:]:
            half['x'] += half['vx']
            half['y'] += half['vy']
            half['vy'] += self.gravity
            half['angle'] += half['rot_speed']

            if half['y'] > self.screen_height + 100:
                self.sliced_halves.remove(half)

        return missed_fruits

    def check_collision(self, hand_pos):
        if not hand_pos:
            return 0, None

        sliced_count = 0
        hx, hy = hand_pos
        hit_types = []

        for item in self.fruits[:]:
            fx = item['x']
            fy = item['y']
            distance = math.hypot(hx - fx, hy - fy)

            if distance < 80:
                self.fruits.remove(item)
                
                if item['is_bomb']:
                    return 0, 'bomb'

                sliced_count += 1
                hit_types.append(item['type'])
                
                self.sliced_halves.append({
                    'x': fx - 15,
                    'y': fy,
                    'vx': item['vx'] - random.uniform(3, 6),
                    'vy': item['vy'] - random.uniform(2, 5),
                    'angle': 0,
                    'rot_speed': random.uniform(5, 10),
                    'type': 'left',
                    'fruit': item['type']
                })
                self.sliced_halves.append({
                    'x': fx + 15,
                    'y': fy,
                    'vx': item['vx'] + random.uniform(3, 6),
                    'vy': item['vy'] - random.uniform(2, 5),
                    'angle': 0,
                    'rot_speed': -random.uniform(5, 10),
                    'type': 'right',
                    'fruit': item['type']
                })

        return sliced_count, hit_types