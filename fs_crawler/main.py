if __name__ == '__main__':
    desktop_path = pathlib.Path('C:/Users') / 'Henri-Olivier' / 'Desktop'
#    folder_path = pathlib.Path('M:/PhotosVideos')
#    listing, tree = crawl(folder_path)
#    duplicates = get_duplicates(listing)
#    dump_json_listing(duplicates, desktop_path / 'photos_duplicates.json')

#    duplicates = load_json_listing(desktop_path / 'photos_duplicates.json')
#    duplicates_sorted, size_gain = get_duplicates(duplicates)
#    dump_json_listing(duplicates_sorted, desktop_path / 'photos_duplicates_sorted.json')
#    print(f'you can gain {size_gain / 1E9:.2f} Gigabytes space')

    zip_path = desktop_path / 'blue.zip'
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        for file_name in zip_file.namelist():
#            print(str(desktop_path / 'blue.zip' / file_name))
            with zip_file.open(file_name) as file:
#                print(file.read())
#                print('--')
                pass
#    print('------------------')
    zip_path = desktop_path / 'blue.zip'
    print(zipfile.is_zipfile(str(zip_path)))
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        zip_file.printdir()
        print('------------------')
        import os
        dirs = list(set([os.path.dirname(x) for x in zip_file.namelist()]))
        print(dirs)
        topdirs = [os.path.split(x)[0] for x in dirs]
        print(topdirs)
#        file_info = zip_file.getinfo('fol')
#        if file_info.is_dir():
#            print('dir !!!!!!!!!!!!!!!!!')
        zip_file.extractall(desktop_path)
        print('------------------')
        for each_path in zip_file.infolist():
            print(each_path)
            file_info = zip_file.getinfo(each_path.filename)
            if file_info.is_dir():
                print('dir !!!!!!!!!!!!!!!!!')
        print('------------------')
        for each_path in zip_file.namelist():
            print(each_path)
            file_info = zip_file.getinfo(each_path)
            if file_info.is_dir():
                print('dir !!!!!!!!!!!!!!!!!')
        print('------------------')
        root_path = zipfile.Path(zip_file)
        for each_path in root_path.iterdir():
            real_path = pathlib.Path(str(each_path))
            print(each_path)
            print(real_path)
            print(zipfile.is_zipfile(str(each_path)))
            print(zipfile.is_zipfile(str(real_path)))
            if real_path.suffix == '.zip':
                print(True)
                with each_path.open() as file:
                    with zipfile.ZipFile(io.BytesIO(file.read()), 'r') as nested_zip_file:
                        nested_zip_file.printdir()
            if each_path.is_file():
                print(zip_file.getinfo(each_path.name).file_size)
                with each_path.open() as file:
                    print(file.read())
                    print('--')
