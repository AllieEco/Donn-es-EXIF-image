from exif_utils import print_exif_json


def main() -> None:
    image_path = input("Chemin de l'image : ").strip()
    if (image_path.startswith('"') and image_path.endswith('"')) or (
        image_path.startswith("'") and image_path.endswith("'")
    ):
        image_path = image_path[1:-1].strip()
    if not image_path:
        print("Chemin vide, arrêt.")
        return
    print_exif_json(image_path)


if __name__ == "__main__":
    main()
