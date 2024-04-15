import os
import shutil
from concurrent.futures import ThreadPoolExecutor

def normalize(text):
    char_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'д': 'd', 'е': 'e', 'є': 'ye', 'ж': 'zh',
        'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
        'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'yu', 'я': 'ya'
    }

    text = text.lower()  
    result = []

    for char in text:
        if char in char_map:
            result.append(char_map[char])
        elif char.isalnum():
            result.append(char)
        else:
            result.append('.')

    return ''.join(result)

def sort_files(root, file):
    extensions = {
        'images': ('JPEG', 'PNG', 'JPG', 'SVG'),
        'videos': ('AVI', 'MP4', 'MOV', 'MKV'),
        'documents': ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
        'audio': ('MP3', 'OGG', 'WAV', 'AMR'),
        'archives': ('ZIP', 'GZ', 'TAR')
    }

    file_extension = file.split('.')[-1].upper()
    known = False

    for category, exts in extensions.items():
        if file_extension in exts:
            known = True

            target_folder = os.path.join(root, category)
            if not os.path.exists(target_folder):
                try:
                    os.makedirs(target_folder)
                except FileExistsError:
                    pass 

            source_file = os.path.join(root, file)
            target_file = os.path.join(target_folder, normalize(file))
            shutil.move(source_file, target_file)

    return known, file_extension

def process_directory(folder_path):
    known_extensions = set()
    unknown_extensions = set()

    with ThreadPoolExecutor() as executor:
        for root, _, files in os.walk(folder_path):
            futures = [executor.submit(sort_files, root, file) for file in files]
            
            for future in futures:
                known, file_extension = future.result()
                if known:
                    known_extensions.add(file_extension)
                else:
                    unknown_extensions.add(file_extension)

    return known_extensions, unknown_extensions

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python sort.py <folder_path>")
    else:
        folder_path = sys.argv[1]
        known_extensions, unknown_extensions = process_directory(folder_path)

        print("Known extensions:")
        for ext in known_extensions:
            print(ext)

        print("\nUnknown extensions:")
        for ext in unknown_extensions:
            print(ext)
