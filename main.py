import sys
import pygame
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CAMERA_INDEX, INITIAL_LIVES, SPAWN_INTERVAL
from backend.vision_tracker import VisionTracker
from backend.physics_engine import PhysicsEngine
from backend.auth_manager import AuthManager
from frontend.display_manager import DisplayManager

def main():
    display = DisplayManager(SCREEN_WIDTH, SCREEN_HEIGHT, FPS)
    tracker = VisionTracker(camera_index=CAMERA_INDEX)
    physics = PhysicsEngine(SCREEN_WIDTH, SCREEN_HEIGHT)
    auth = AuthManager()

    in_login = True
    in_dashboard = False
    in_history_screen = False 
    
    username = ""
    password = ""
    active_field = "username"
    auth_message = "Click fields or use Tab to switch."
    auth_success = True
    current_user = None

    total_plays = 0
    history = []

    score = 0
    lives = INITIAL_LIVES
    frame_count = 0
    game_over = False
    match_recorded = False
    running = True

    current_level = 1
    target_score_per_level = 100
    level_banner_frames = 0
    current_spawn_interval = SPAWN_INTERVAL

    while running:
        if in_login:
            user_box, pass_box, login_btn, reg_btn = display.draw_login_screen(
                username, password, active_field, auth_message, auth_success
            )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if user_box.collidepoint(event.pos): active_field = "username"
                    elif pass_box.collidepoint(event.pos): active_field = "password"
                    elif login_btn.collidepoint(event.pos):
                        success, res = auth.login(username, password)
                        if success:
                            current_user = res
                            total_plays, history = auth.get_dashboard_stats(current_user["id"])
                            in_login = False; in_dashboard = True
                        else:
                            auth_message = res; auth_success = False
                    elif reg_btn.collidepoint(event.pos):
                        success, res = auth.register(username, password)
                        auth_message = res; auth_success = success
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        active_field = "password" if active_field == "username" else "username"
                    elif event.key == pygame.K_RETURN:
                        success, res = auth.login(username, password)
                        if success:
                            current_user = res
                            total_plays, history = auth.get_dashboard_stats(current_user["id"])
                            in_login = False; in_dashboard = True
                        else:
                            auth_message = res; auth_success = False
                    elif event.key == pygame.K_BACKSPACE:
                        if active_field == "username": username = username[:-1]
                        else: password = password[:-1]
                    else:
                        if len(event.unicode) > 0 and event.unicode.isprintable():
                            if active_field == "username" and len(username) < 15: username += event.unicode
                            elif active_field == "password" and len(password) < 20: password += event.unicode

            display.update_screen()
            continue

        elif in_dashboard:
            buttons = display.draw_dashboard(current_user["username"], current_user["high_score"], total_plays)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    
                    if buttons['play'].collidepoint(event.pos):
                        in_dashboard = False
                        score = 0; lives = INITIAL_LIVES; current_level = 1
                        current_spawn_interval = SPAWN_INTERVAL; level_banner_frames = 0
                        match_recorded = False; game_over = False
                        physics.fruits.clear(); physics.sliced_halves.clear()
                    
                    elif buttons['history'].collidepoint(event.pos):
                        in_dashboard = False
                        in_history_screen = True
                        
                    elif buttons['logout'].collidepoint(event.pos):
                        in_dashboard = False
                        in_login = True
                        current_user = None
                        username = ""
                        password = ""
                        auth_message = "Logged out successfully."
                        auth_success = True
                        active_field = "username"

                    elif buttons['bgm_minus'].collidepoint(event.pos):
                        display.set_bgm_volume(max(0.0, display.bgm_volume - 0.1))
                    elif buttons['bgm_plus'].collidepoint(event.pos):
                        display.set_bgm_volume(min(1.0, display.bgm_volume + 0.1))
                    elif buttons['sfx_minus'].collidepoint(event.pos):
                        display.set_sfx_volume(max(0.0, display.sfx_volume - 0.1))
                    elif buttons['sfx_plus'].collidepoint(event.pos):
                        display.set_sfx_volume(min(1.0, display.sfx_volume + 0.1))
                    elif buttons['cam_toggle'].collidepoint(event.pos):
                        display.camera_on = not display.camera_on

            display.update_screen()
            continue

        elif in_history_screen:
            back_btn = display.draw_history_screen(current_user["username"], history)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_btn.collidepoint(event.pos):
                        in_history_screen = False
                        in_dashboard = True
            
            display.update_screen()
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    in_dashboard = True

        if not game_over:
            pos_data = tracker.get_hand_position(SCREEN_WIDTH, SCREEN_HEIGHT)
            if isinstance(pos_data, tuple) and len(pos_data) == 2 and isinstance(pos_data[0], (int, float)):
                hand_pos = (int(pos_data[0]), int(pos_data[1]))
            elif isinstance(pos_data, (list, tuple)) and len(pos_data) > 0 and isinstance(pos_data[0], (list, tuple)):
                hand_pos = (int(pos_data[0][0]), int(pos_data[0][1]))
            else:
                hand_pos = None

            frame_count += 1
            if frame_count % current_spawn_interval == 0:
                physics.spawn_fruit(level=current_level)

            missed = physics.update_physics()
            if missed > 0:
                lives -= missed
                if lives <= 0:
                    lives = 0; game_over = True
                    if not match_recorded:
                        current_user["high_score"] = auth.update_high_score(current_user["username"], score)
                        auth.record_match(current_user["id"], score)
                        total_plays, history = auth.get_dashboard_stats(current_user["id"])
                        display.play_game_over_sound()
                        match_recorded = True

            if hand_pos:
                sliced_count, hit_result = physics.check_collision(hand_pos)
                if hit_result == 'bomb':
                    display.add_splash(hand_pos[0], hand_pos[1], item_type='bomb')
                    lives = 0; game_over = True
                    if not match_recorded:
                        current_user["high_score"] = auth.update_high_score(current_user["username"], score)
                        auth.record_match(current_user["id"], score)
                        total_plays, history = auth.get_dashboard_stats(current_user["id"])
                        display.play_game_over_sound()
                        match_recorded = True

                elif sliced_count > 0:
                    score += sliced_count * 10
                    for fruit_type in hit_result:
                        display.add_splash(hand_pos[0], hand_pos[1], item_type=fruit_type)
                    display.play_slice_sound()

                    if score >= current_level * target_score_per_level:
                        current_level += 1
                        level_banner_frames = 60
                        current_spawn_interval = max(20, SPAWN_INTERVAL - (current_level * 5))

            display.draw_background()
            display.draw_game_elements(physics.fruits, physics.sliced_halves)
            
            if hand_pos:
                display.draw_hand_cursor([hand_pos])

            display.draw_player_hud(
                score, lives, current_user["username"], 
                current_user["high_score"], current_level, 
                current_level * target_score_per_level
            )

            if level_banner_frames > 0:
                display.draw_level_up(current_level)
                level_banner_frames -= 1
            
            if display.camera_on and hasattr(tracker, 'current_frame'):
                display.draw_camera_feed(tracker.current_frame)
                
        else:
            display.draw_background()
            display.draw_game_elements([], physics.sliced_halves)
            display.draw_game_over(score)

        display.update_screen()

    tracker.release()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()