import os
import pygame

pygame.init()

root = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(root, "assets", "images")

print("=" * 50)
print(f"Checking images directory:\n{image_dir}\n")

if not os.path.exists(image_dir):
    print("❌ ERROR: 'assets/images' folder does NOT exist at this location!")
else:
    files_found = os.listdir(image_dir)
    print(f"Files found inside assets/images: {files_found}\n")

    targets = ["background.png", "background.jpg", "apple.png", "apple_half_1.png", "apple_half_2.png"]
    
    for target in targets:
        target_path = os.path.join(image_dir, target)
        if os.path.exists(target_path):

            try:
                img = pygame.image.load(target_path)
                print(f"✅ SUCCESS: Loaded '{target}' (Size: {img.get_size()})")
            except Exception as e:
                print(f"⚠️ CORRUPT FILE: Found '{target}' but Pygame failed to parse it. Error: {e}")
        else:
            print(f"❌ MISSING: '{target}' was not found.")
print("=" * 50)
pygame.quit()
