import os
import json
import subprocess
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image

# Unicode character starting point
UNICODE_START = 0xE800  

class RankPackCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Rank Pack Creator")
        self.rank_images = {}
        self.unicode_counter = UNICODE_START
        self.pack_name = ""

        # UI Elements
        self.label = tk.Label(root, text="Select images and assign rank names:")
        self.label.pack(pady=10)

        self.upload_button = tk.Button(root, text="Upload Image", command=self.upload_image)
        self.upload_button.pack(pady=5)

        self.listbox = tk.Listbox(root, width=50, height=10)
        self.listbox.pack(pady=10)

        self.save_button = tk.Button(root, text="Generate Pack", command=self.generate_pack)
        self.save_button.pack(pady=5)

    def upload_image(self):
        os.makedirs(self.get_texture_dir(), exist_ok=True)
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if not file_path:
            return
        
        rank_name = simpledialog.askstring("Rank Name", "Enter rank name (no spaces or capitals):")
        if not rank_name:
            messagebox.showerror("Error", "Rank name is required.")
            return

        try:
            with Image.open(file_path) as img:
                if img.height > 200:
                    messagebox.showerror("Error", f"{rank_name} exceeds 200px in height.")
                    return

                # Save image in assets/minecraft/textures/ranks/
                new_path = os.path.join(self.get_texture_dir(), f"{rank_name}.png")
                img.save(new_path)

                # Store rank and Unicode mapping
                self.rank_images[rank_name] = new_path
                self.listbox.insert(tk.END, f"{rank_name} -> {new_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {e}")

    def generate_pack(self):
        save_dir = filedialog.askdirectory(title="Select Pack Save Location")
        if not save_dir:
            messagebox.showerror("Error", "No directory selected.")
            return
        
        self.pack_name = simpledialog.askstring("Pack Name", "Enter the name of your pack:")
        if not self.pack_name:
            messagebox.showerror("Error", "Pack name is required.")
            return
        
        pack_dir = os.path.join(save_dir, self.pack_name)
        texture_dir = os.path.join(pack_dir, "assets", "minecraft", "textures", "ranks")
        os.makedirs(texture_dir, exist_ok=True)

        json_path = os.path.join(pack_dir, "assets", "minecraft", "font", "default.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        data = {"providers": []}

        # Generate JSON entries
        for index, (rank_name, image_path) in enumerate(self.rank_images.items()):
            unicode_value = f"\\uE8{str(index).zfill(2)}".encode("utf-8").decode("unicode_escape")

            entry = {
                "type": "bitmap",
                "file": f"minecraft:textures/ranks/{rank_name}.png",
                "ascent": 8,
                "height": 8,
                "chars": [unicode_value]
            }
            data["providers"].append(entry)

            # Copy images to the correct directory
            os.rename(image_path, os.path.join(texture_dir, f"{rank_name}.png"))

        # Save default.json
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

                # Save Unicode mappings
        unicode_mappings_file = os.path.join(pack_dir, "unicode_mappings.txt")
        with open(unicode_mappings_file, "w", encoding="utf-8") as mapping_file:
            mapping_file.write("Here are the unicode mappings!\n\n")
            for index, rank_name in enumerate(self.rank_images.keys()):
                unicode_value = f"\\uE8{str(index).zfill(2)}".encode("utf-8").decode("unicode_escape")
                mapping_file.write(f"{rank_name}: {unicode_value}\n")
        #windows code
        # os.startfile(unicode_mappings_file)  
        #mac code
        subprocess.run(["open", unicode_mappings_file])
        


        # Create pack.mcmeta
        mcmeta_file = os.path.join(pack_dir, "pack.mcmeta")
        mcmeta_content = {
            "pack": {
                "pack_format": 32,
                "description": self.pack_name
            }
        }
        with open(mcmeta_file, "w", encoding="utf-8") as f:
            json.dump(mcmeta_content, f, indent=4)

        # Zip the pack
        self.create_zip(pack_dir)

        messagebox.showinfo("Success", f"Pack generated: {self.pack_name}.zip")

    def create_zip(self, pack_dir):
        zip_file = f"{pack_dir}.zip"
        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as pack_zip:
            for foldername, _, filenames in os.walk(pack_dir):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, pack_dir)
                    pack_zip.write(file_path, arcname)
        unicode_mappings_file = os.path.join(pack_dir, "unicode_mappings.txt")
        messagebox.showinfo("Unicode Mappings", f"Unicode mappings saved at:\n{unicode_mappings_file}")

    def get_texture_dir(self):
        return os.path.join(os.getcwd(), "temp_textures")

# Run GUI
root = tk.Tk()
app = RankPackCreator(root)
root.mainloop()
