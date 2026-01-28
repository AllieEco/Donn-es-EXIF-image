from exif_utils import print_exif_json


def main() -> None:
    image_path = input("Chemin de l'image : ").strip()
    if not image_path:
        print("Chemin vide, arrêt.")
        return
    print_exif_json(image_path)


if __name__ == "__main__":
    main()
