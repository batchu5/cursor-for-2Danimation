import subprocess
import os
import sys
import shutil
manim_path = shutil.which("manim")

# print("⚙️ Starting scene generation subprocess...")

env = os.environ.copy()

with open("classname.txt", "r") as f:
    class_name = f.readline().strip()

print(f"Running manim for class: {class_name}")
try:
    print("Current working directory:", os.getcwd())
    print("started to run the generate_scene.py")

    with open("render.log", "w") as f:
        subprocess.run(
            [
                manim_path,
                "generated_scene.py",
                class_name,
                "-pql",
                "--output_file", f"{class_name}.mp4"
            ],
            env=env,
            stdout=f,
            stderr=subprocess.STDOUT,
            check=True
        )
        print("fuck it completed the generate_scene.py")

except KeyboardInterrupt:
    print("Rendering interrupted by user.")
except subprocess.CalledProcessError as e:
    print(f"Render failed. Exit code: {e.returncode}")

