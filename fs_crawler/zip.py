    elif path.is_file() and path.suffix == '.zip':
        dir_content_size = 0
        dir_content_hash_list = []
        with zipfile.ZipFile(path, 'r') as zfile:
            zfile.printdir()
            for each_child in zfile.infolist():
                if each_child.is_dir():
                    print('dir !:!!!!!!!!!!!!!!!')
                file_hasher = hashlib.md5()
                with zfile.open(each_child, 'r') as file_content:
                    content_stream = file_content.read(BLOCK_SIZE)
                    while len(content_stream) > 0:
                        file_hasher.update(content_stream)
                        content_stream = file_content.read(BLOCK_SIZE)
                file_content_hash = file_hasher.hexdigest()
                file_content_size = zfile.getinfo(each_child.filename).file_size
                file_content_key = (file_content_hash, FILE_TYPE, file_content_size)
                real_path = path / str(each_child.filename)
                listing[file_content_key].add(real_path)
                tree[real_path] = file_content_key
                dir_content_size += tree[real_path][2]
                dir_content_hash_list.append(tree[real_path][0])
        dir_content = '\n'.join(sorted(dir_content_hash_list))
        dir_content_hash = hashlib.md5(dir_content.encode()).hexdigest()
        dir_content_key = (dir_content_hash, DIR_TYPE, dir_content_size)
        listing[dir_content_key].add(path)
        tree[path] = dir_content_key
