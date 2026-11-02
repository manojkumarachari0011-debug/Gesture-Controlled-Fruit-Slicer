import os
import pygame
import random
import numpy as np

class Particle:
    def __init__(self, x, y, color, max_speed=6):
        self.x = x
        self.y = y
        self.vx = random.uniform(-max_speed, max_speed)
        self.vy = random.uniform(-max_speed, max_speed)
        self.radius = random.randint(4, 9)
        self.color = color
        self.life = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 12
        self.radius = max(1, self.radius - 0.2)

    def draw(self, surface):
        if self.life > 0:
            surf = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(
                surf,
                (*self.color[:3], max(0, int(self.life))),
                (int(self.radius), int(self.radius)),
                int(self.radius)
            )
            surface.blit(surf, (int(self.x - self.radius), int(self.y - self.radius)))

class DisplayManager:
    def __init__(self, width, height, fps):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.width = width
        self.height = height
        self.fps = fps
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fruit Ninja - Gesture Slicer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 32, bold=True)

        self.trail = []
        self.particles = []
        self.assets = {}
        self.blade_angle = 0 

        self.bgm_volume = 0.5
        self.sfx_volume = 1.0
        self.camera_on = False
        self.bg_music_loaded = False

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.image_dir = os.path.abspath(os.path.join(self.base_dir, '..', 'assets', 'images'))
        self.sound_dir = os.path.abspath(os.path.join(self.base_dir, '..', 'assets', 'sounds'))

        self.background = pygame.Surface((self.width, self.height))
        self.background.fill((25, 20, 35))

        self.slice_sound = None
        self.game_over_sound = None

        self.load_assets()

    def load_assets(self):
        if os.path.exists(self.image_dir):
            available_files = {f.lower(): os.path.join(self.image_dir, f) for f in os.listdir(self.image_dir)}
            for bg_name in ['background.jpg', 'background.png', 'bg.jpg', 'bg.png']:
                if bg_name in available_files:
                    try:
                        loaded_bg = pygame.image.load(available_files[bg_name]).convert()
                        self.background = pygame.transform.scale(loaded_bg, (self.width, self.height))
                        break
                    except Exception: pass

            item_keys = ['apple', 'banana', 'orange', 'bomb']
            for key in item_keys:
                for ext in ['.png', '.jpg']:
                    fname = f"{key}{ext}"
                    if fname in available_files:
                        try:
                            img = pygame.image.load(available_files[fname]).convert_alpha()
                            self.assets[key] = pygame.transform.scale(img, (80, 80))
                            break
                        except Exception: pass
                for h1 in [f"{key}_half_1.png", f"{key}left.png"]:
                    if h1 in available_files:
                        try:
                            img = pygame.image.load(available_files[h1]).convert_alpha()
                            self.assets[f"{key}_half_1"] = pygame.transform.scale(img, (45, 80))
                            break
                        except Exception: pass
                for h2 in [f"{key}_half_2.png", f"{key}right.png"]:
                    if h2 in available_files:
                        try:
                            img = pygame.image.load(available_files[h2]).convert_alpha()
                            self.assets[f"{key}_half_2"] = pygame.transform.scale(img, (45, 80))
                            break
                        except Exception: pass

        star_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        center = 40
        light_metal = (230, 230, 245)
        dark_metal = (110, 110, 125)
        pygame.draw.polygon(star_surf, light_metal, [(center, 0), (center-8, center), (center, center)])
        pygame.draw.polygon(star_surf, dark_metal, [(center, 0), (center+8, center), (center, center)])
        pygame.draw.polygon(star_surf, light_metal, [(80, center), (center, center-8), (center, center)])
        pygame.draw.polygon(star_surf, dark_metal, [(80, center), (center, center+8), (center, center)])
        pygame.draw.polygon(star_surf, light_metal, [(center, 80), (center+8, center), (center, center)])
        pygame.draw.polygon(star_surf, dark_metal, [(center, 80), (center-8, center), (center, center)])
        pygame.draw.polygon(star_surf, light_metal, [(0, center), (center, center+8), (center, center)])
        pygame.draw.polygon(star_surf, dark_metal, [(0, center), (center, center-8), (center, center)])
        pygame.draw.circle(star_surf, (80, 80, 90), (center, center), 12)
        pygame.draw.circle(star_surf, (30, 30, 30), (center, center), 5)
        self.assets['blade'] = star_surf

        if os.path.exists(self.sound_dir):
            for s_name in ['slice.wav', 'slice.mp3']:
                s_path = os.path.join(self.sound_dir, s_name)
                if os.path.exists(s_path):
                    try:
                        self.slice_sound = pygame.mixer.Sound(s_path)
                        self.slice_sound.set_volume(self.sfx_volume)
                        break
                    except Exception: pass

            for go_name in ['game_over.wav', 'game_over.mp3']:
                go_path = os.path.join(self.sound_dir, go_name)
                if os.path.exists(go_path):
                    try:
                        self.game_over_sound = pygame.mixer.Sound(go_path)
                        self.game_over_sound.set_volume(self.sfx_volume)
                        break
                    except Exception: pass

            for bgm_name in ['bgm.mp3', 'bgm.wav']:
                m_path = os.path.join(self.sound_dir, bgm_name)
                if os.path.exists(m_path):
                    try:
                        pygame.mixer.music.load(m_path)
                        pygame.mixer.music.set_volume(self.bgm_volume)
                        pygame.mixer.music.play(-1)
                        self.bg_music_loaded = True
                        break
                    except Exception: pass

    def set_bgm_volume(self, vol):
        self.bgm_volume = round(vol, 1)
        if self.bg_music_loaded:
            pygame.mixer.music.set_volume(self.bgm_volume)

    def set_sfx_volume(self, vol):
        self.sfx_volume = round(vol, 1)
        if self.slice_sound:
            self.slice_sound.set_volume(self.sfx_volume)
        if self.game_over_sound:
            self.game_over_sound.set_volume(self.sfx_volume)

    def add_splash(self, x, y, item_type='apple'):
        if item_type == 'bomb':
            for _ in range(60):
                color = random.choice([(255, 60, 0), (255, 180, 0), (80, 80, 80), (255, 255, 255)])
                self.particles.append(Particle(x, y, color, max_speed=12))
        else:
            color_map = {
                'apple': [(220, 20, 60), (255, 100, 100), (255, 255, 255)],
                'banana': [(255, 225, 53), (255, 250, 150), (255, 255, 255)],
                'orange': [(255, 140, 0), (255, 180, 50), (255, 255, 255)]
            }
            colors = color_map.get(item_type, [(255, 50, 50), (255, 255, 255)])
            for _ in range(25):
                self.particles.append(Particle(x, y, random.choice(colors)))

    def draw_background(self):
        self.screen.blit(self.background, (0, 0))

    def draw_game_elements(self, fruits, halves):
        for item in fruits:
            itype = item['type']
            if itype in self.assets:
                self.screen.blit(self.assets[itype], (int(item['x']) - 40, int(item['y']) - 40))
            else:
                if itype == 'bomb':
                    pygame.draw.circle(self.screen, (40, 40, 40), (int(item['x']), int(item['y'])), 32)
                    pygame.draw.circle(self.screen, (255, 60, 0), (int(item['x']), int(item['y']) - 32), 6)
                elif itype == 'banana':
                    pygame.draw.ellipse(self.screen, (255, 225, 53), (int(item['x']) - 40, int(item['y']) - 20, 80, 40))
                elif itype == 'orange':
                    pygame.draw.circle(self.screen, (255, 140, 0), (int(item['x']), int(item['y'])), 35)
                else:
                    pygame.draw.circle(self.screen, (220, 20, 60), (int(item['x']), int(item['y'])), 35)

        for half in halves:
            ftype = half.get('fruit', 'apple')
            h_idx = 1 if half.get('type') == 'left' else 2
            key = f"{ftype}_half_{h_idx}"

            if key in self.assets:
                rot = pygame.transform.rotate(self.assets[key], half.get('angle', 0))
                self.screen.blit(rot, rot.get_rect(center=(int(half['x']), int(half['y']))).topleft)
            else:
                color = (255, 225, 53) if ftype == 'banana' else ((255, 140, 0) if ftype == 'orange' else (220, 20, 60))
                surf = pygame.Surface((40, 70), pygame.SRCALPHA)
                pygame.draw.ellipse(surf, color, (0, 0, 40, 70))
                rot = pygame.transform.rotate(surf, half.get('angle', 0))
                self.screen.blit(rot, rot.get_rect(center=(int(half['x']), int(half['y']))).topleft)

        for p in self.particles[:]:
            p.update()
            p.draw(self.screen)
            if p.life <= 0:
                self.particles.remove(p)

    def draw_hand_cursor(self, hand_positions):
        self.blade_angle = (self.blade_angle - 25) % 360
        if hand_positions and hand_positions[0]:
            hx, hy = hand_positions[0]
            self.trail.append((hx, hy))
            if len(self.trail) > 10:
                self.trail.pop(0)

            if len(self.trail) > 1:
                pygame.draw.lines(self.screen, (255, 255, 255), False, self.trail, 6)
                pygame.draw.lines(self.screen, (0, 230, 255), False, self.trail, 3)

            if 'blade' in self.assets and self.assets['blade']:
                rotated_blade = pygame.transform.rotate(self.assets['blade'], self.blade_angle)
                rect = rotated_blade.get_rect(center=(int(hx), int(hy)))
                self.screen.blit(rotated_blade, rect.topleft)
        else:
            self.trail.clear()

    def draw_camera_feed(self, frame_rgb):
        if self.camera_on and frame_rgb is not None:
            frame_surface = pygame.surfarray.make_surface(np.swapaxes(frame_rgb, 0, 1))
            pip_w, pip_h = 260, 195
            frame_surface = pygame.transform.scale(frame_surface, (pip_w, pip_h))
            pip_rect = pygame.Rect(self.width - pip_w - 25, 75, pip_w, pip_h)
            pygame.draw.rect(self.screen, (0, 230, 255), pip_rect.inflate(6, 6), border_radius=8)
            self.screen.blit(frame_surface, pip_rect.topleft)

    def draw_player_hud(self, score, lives, player_name, high_score, current_level=1, target_score=100):
        score_surf = self.font.render(f"Score: {score}", True, (255, 255, 255))
        lives_surf = self.font.render(f"Lives: {lives}", True, (255, 70, 70))
        self.screen.blit(score_surf, (25, 25))
        self.screen.blit(lives_surf, (self.width - 150, 25))

        hud_font = pygame.font.SysFont('Arial', 22, bold=True)
        player_surf = hud_font.render(f"Ninja: {player_name}", True, (255, 215, 0))
        hs_surf = hud_font.render(f"High Score: {high_score}", True, (0, 230, 255))
        lvl_surf = hud_font.render(f"Stage {current_level} (Next: {target_score} pts)", True, (150, 255, 150))
        self.screen.blit(player_surf, (25, 65))
        self.screen.blit(hs_surf, (25, 95))
        self.screen.blit(lvl_surf, (25, 125))

    def draw_level_up(self, level):
        banner_font = pygame.font.SysFont('Arial', 54, bold=True)
        txt = banner_font.render(f"LEVEL {level} UNLOCKED!", True, (255, 215, 0))
        rect = txt.get_rect(center=(self.width // 2, self.height // 3))
        bg_rect = rect.inflate(40, 20)
        overlay = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, bg_rect.topleft)
        pygame.draw.rect(self.screen, (255, 215, 0), bg_rect, 3, border_radius=10)
        self.screen.blit(txt, rect)

    def draw_login_screen(self, username, password, active_field, message, is_success):
        self.screen.blit(self.background, (0, 0))
        card_rect = pygame.Rect(self.width // 2 - 250, self.height // 2 - 220, 500, 440)
        card_surf = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
        card_surf.fill((20, 20, 30, 230))
        self.screen.blit(card_surf, card_rect.topleft)
        pygame.draw.rect(self.screen, (255, 180, 0), card_rect, 3, border_radius=12)

        title_surf = pygame.font.SysFont('Arial', 36, bold=True).render("NINJA SLICER - LOGIN", True, (255, 255, 255))
        self.screen.blit(title_surf, title_surf.get_rect(center=(self.width // 2, self.height // 2 - 160)))

        user_box = pygame.Rect(self.width // 2 - 180, self.height // 2 - 90, 360, 45)
        pass_box = pygame.Rect(self.width // 2 - 180, self.height // 2 - 10, 360, 45)

        u_border = (0, 230, 255) if active_field == 'username' else (100, 100, 120)
        pygame.draw.rect(self.screen, (40, 40, 55), user_box, border_radius=6)
        pygame.draw.rect(self.screen, u_border, user_box, 2, border_radius=6)
        u_text = self.font.render(username if username else "Username", True, (255, 255, 255) if username else (130, 130, 150))
        self.screen.blit(u_text, (user_box.x + 10, user_box.y + 6))

        p_border = (0, 230, 255) if active_field == 'password' else (100, 100, 120)
        pygame.draw.rect(self.screen, (40, 40, 55), pass_box, border_radius=6)
        pygame.draw.rect(self.screen, p_border, pass_box, 2, border_radius=6)
        masked_pass = "*" * len(password) if password else "Password"
        p_text = self.font.render(masked_pass, True, (255, 255, 255) if password else (130, 130, 150))
        self.screen.blit(p_text, (pass_box.x + 10, pass_box.y + 6))

        login_btn = pygame.Rect(self.width // 2 - 180, self.height // 2 + 60, 170, 45)
        reg_btn = pygame.Rect(self.width // 2 + 10, self.height // 2 + 60, 170, 45)
        pygame.draw.rect(self.screen, (46, 204, 113), login_btn, border_radius=6)
        pygame.draw.rect(self.screen, (52, 152, 219), reg_btn, border_radius=6)

        btn_font = pygame.font.SysFont('Arial', 20, bold=True)
        t_log = btn_font.render("LOGIN (Enter)", True, (255, 255, 255))
        t_reg = btn_font.render("REGISTER (Tab)", True, (255, 255, 255))
        self.screen.blit(t_log, t_log.get_rect(center=login_btn.center))
        self.screen.blit(t_reg, t_reg.get_rect(center=reg_btn.center))

        if message:
            msg_color = (100, 255, 100) if is_success else (255, 80, 80)
            msg_surf = pygame.font.SysFont('Arial', 18).render(message, True, msg_color)
            self.screen.blit(msg_surf, msg_surf.get_rect(center=(self.width // 2, self.height // 2 + 140)))

        return user_box, pass_box, login_btn, reg_btn

    def draw_dashboard(self, username, high_score, total_plays):
        self.screen.blit(self.background, (0, 0))
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((15, 15, 25, 210))
        self.screen.blit(overlay, (0, 0))

        panel_w = int(self.width * 0.8)
        panel_h = int(self.height * 0.8)
        panel_x = (self.width - panel_w) // 2
        panel_y = (self.height - panel_h) // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.screen, (30, 30, 45), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, (0, 230, 255), panel_rect, 3, border_radius=15)

        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        title_surf = title_font.render(f"PROFILE: {username.upper()}", True, (255, 215, 0))
        self.screen.blit(title_surf, title_surf.get_rect(center=(self.width // 2, panel_y + 60)))
        pygame.draw.line(self.screen, (100, 100, 120), (panel_x + 50, panel_y + 110), (panel_x + panel_w - 50, panel_y + 110), 2)

        stat_title_font = pygame.font.SysFont('Arial', 32, bold=True)
        stat_font = pygame.font.SysFont('Arial', 28)

        stats_x = panel_x + 80
        stats_y = panel_y + 150
        self.screen.blit(stat_title_font.render("Career Statistics", True, (0, 230, 255)), (stats_x, stats_y))
        
        self.screen.blit(stat_font.render("Highest Score:", True, (200, 200, 200)), (stats_x, stats_y + 70))
        self.screen.blit(stat_font.render(str(high_score), True, (255, 255, 255)), (stats_x + 270, stats_y + 70))
        self.screen.blit(stat_font.render("Total Games Played:", True, (200, 200, 200)), (stats_x, stats_y + 130))
        self.screen.blit(stat_font.render(str(total_plays), True, (255, 255, 255)), (stats_x + 270, stats_y + 130))

        hist_btn = pygame.Rect(stats_x, stats_y + 200, 240, 45)
        pygame.draw.rect(self.screen, (52, 152, 219), hist_btn, border_radius=8)
        hist_txt = pygame.font.SysFont('Arial', 22, bold=True).render("VIEW ALL MATCHES ➔", True, (255, 255, 255))
        self.screen.blit(hist_txt, hist_txt.get_rect(center=hist_btn.center))

        set_x = panel_x + panel_w // 2 + 10
        set_y = panel_y + 150
        self.screen.blit(stat_title_font.render("Game Settings", True, (150, 255, 150)), (set_x, set_y))

        reg_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        bgm_y = set_y + 70
        self.screen.blit(reg_font.render("Background Music:", True, (200, 200, 220)), (set_x, bgm_y))
        bgm_m = pygame.Rect(set_x + 210, bgm_y - 2, 35, 35)
        bgm_p = pygame.Rect(set_x + 320, bgm_y - 2, 35, 35)
        pygame.draw.rect(self.screen, (255, 80, 80), bgm_m, border_radius=5)
        pygame.draw.rect(self.screen, (80, 255, 80), bgm_p, border_radius=5)
        self.screen.blit(reg_font.render("-", True, (0, 0, 0)), (bgm_m.x + 13, bgm_m.y + 3))
        self.screen.blit(reg_font.render("+", True, (0, 0, 0)), (bgm_p.x + 10, bgm_p.y + 3))
        bgm_val = reg_font.render(f"{int(self.bgm_volume * 100)}%", True, (255, 255, 255))
        self.screen.blit(bgm_val, (set_x + 260, bgm_y))

        sfx_y = bgm_y + 60
        self.screen.blit(reg_font.render("Blade / SFX Volume:", True, (200, 200, 220)), (set_x, sfx_y))
        sfx_m = pygame.Rect(set_x + 210, sfx_y - 2, 35, 35)
        sfx_p = pygame.Rect(set_x + 320, sfx_y - 2, 35, 35)
        pygame.draw.rect(self.screen, (255, 80, 80), sfx_m, border_radius=5)
        pygame.draw.rect(self.screen, (80, 255, 80), sfx_p, border_radius=5)
        self.screen.blit(reg_font.render("-", True, (0, 0, 0)), (sfx_m.x + 13, sfx_m.y + 3))
        self.screen.blit(reg_font.render("+", True, (0, 0, 0)), (sfx_p.x + 10, sfx_p.y + 3))
        sfx_val = reg_font.render(f"{int(self.sfx_volume * 100)}%", True, (255, 255, 255))
        self.screen.blit(sfx_val, (set_x + 260, sfx_y))

        cam_y = sfx_y + 60
        self.screen.blit(reg_font.render("Live Player Face:", True, (200, 200, 220)), (set_x, cam_y))
        cam_btn = pygame.Rect(set_x + 210, cam_y - 2, 145, 35)
        cam_color = (80, 255, 80) if self.camera_on else (255, 80, 80)
        pygame.draw.rect(self.screen, cam_color, cam_btn, border_radius=5)
        cam_txt = reg_font.render("CAMERA ON" if self.camera_on else "CAMERA OFF", True, (0, 0, 0))
        self.screen.blit(cam_txt, cam_txt.get_rect(center=cam_btn.center))

        logout_btn = pygame.Rect(panel_x + panel_w - 120, panel_y + 20, 100, 35)
        pygame.draw.rect(self.screen, (255, 80, 80), logout_btn, border_radius=6)
        logout_txt = pygame.font.SysFont('Arial', 16, bold=True).render("LOGOUT", True, (255, 255, 255))
        self.screen.blit(logout_txt, logout_txt.get_rect(center=logout_btn.center))

        btn_w, btn_h = 300, 60
        play_btn = pygame.Rect((self.width - btn_w) // 2, panel_y + panel_h - 90, btn_w, btn_h)
        pygame.draw.rect(self.screen, (46, 204, 113), play_btn, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), play_btn, 2, border_radius=10)
        btn_text = stat_title_font.render("START GAME", True, (255, 255, 255))
        self.screen.blit(btn_text, btn_text.get_rect(center=play_btn.center))

        return {
            'play': play_btn,
            'history': hist_btn,
            'bgm_minus': bgm_m, 'bgm_plus': bgm_p,
            'sfx_minus': sfx_m, 'sfx_plus': sfx_p,
            'cam_toggle': cam_btn,
            'logout': logout_btn
        }

    def draw_history_screen(self, username, history):
        self.screen.blit(self.background, (0, 0))
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((15, 15, 25, 240))
        self.screen.blit(overlay, (0, 0))

        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        title_surf = title_font.render(f"{username.upper()}'S FULL MATCH HISTORY", True, (0, 230, 255))
        self.screen.blit(title_surf, title_surf.get_rect(center=(self.width // 2, 70)))
        pygame.draw.line(self.screen, (100, 100, 120), (100, 110), (self.width - 100, 110), 2)

        reg_font = pygame.font.SysFont('Arial', 20)
        stat_font = pygame.font.SysFont('Arial', 24, bold=True)

        if not history:
            no_hist = reg_font.render("No games played yet.", True, (150, 150, 150))
            self.screen.blit(no_hist, no_hist.get_rect(center=(self.width//2, self.height//2)))
        else:
            max_rows = 15
            col_width = 180
            total_cols = min((len(history) // max_rows) + 1, 5)
            start_x = (self.width - (total_cols * col_width)) // 2

            for i, match_score in enumerate(history):
                col = i // max_rows
                row = i % max_rows
                if col > 4:
                    break 
                
                row_y = 150 + (row * 35)
                col_x = start_x + (col * col_width)

                pygame.draw.circle(self.screen, (150, 255, 150), (col_x, row_y + 13), 5)
                score_surf = reg_font.render(f"Match #{i+1}:", True, (200, 200, 220))
                val_surf = stat_font.render(f"{match_score} pts", True, (255, 255, 255))
                
                self.screen.blit(score_surf, (col_x + 15, row_y))
                self.screen.blit(val_surf, (col_x + 100, row_y))

        back_btn = pygame.Rect((self.width - 200) // 2, self.height - 90, 200, 50)
        pygame.draw.rect(self.screen, (255, 80, 80), back_btn, border_radius=8)
        back_txt = stat_font.render("BACK TO DASHBOARD", True, (255, 255, 255))
        self.screen.blit(back_txt, back_txt.get_rect(center=back_btn.center))

        return back_btn

    def draw_game_over(self, score):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        go_font = pygame.font.SysFont('Arial', 64, bold=True)
        go_surf = go_font.render("GAME OVER", True, (255, 50, 50))
        sub_surf = self.font.render(f"Final Score: {score} | Press R to Restart", True, (255, 255, 255))

        self.screen.blit(go_surf, go_surf.get_rect(center=(self.width // 2, self.height // 2 - 40)))
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(self.width // 2, self.height // 2 + 30)))

    def play_slice_sound(self):
        if self.slice_sound:
            self.slice_sound.play()

    def play_game_over_sound(self):
        if self.game_over_sound:
            self.game_over_sound.play()

    def update_screen(self):
        pygame.display.flip()
        self.clock.tick(self.fps)