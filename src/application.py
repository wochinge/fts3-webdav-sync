import webdav.client as wc

import file_tree as tree
from time import time, sleep

options = {
    'webdav_hostname': "https://webdav1.coursework.htw/",
    'cert_path':       "/coursework/certs/client.crt",
    'key_path':        "/coursework/certs/client.key",
    'ssl_verify_peer': False,
    'ssl_verify_host': False,
}
options2 = {
    'webdav_hostname': "https://webdav2.coursework.htw/",
    'cert_path':       "/coursework/certs/client.crt",
    'key_path':        "/coursework/certs/client.key",
    'ssl_verify_peer': False,
    'ssl_verify_host': False,
}

def main():
    dav = wc.Client(options)
    file_tree = tree.FileTree(dav, 'webdav/')
    start = time()
    file_tree.populate()
    print(file_tree.all_files())
    print('Sleep')
    # sleep(10)
    # print(time() - start)
    # print(file_tree.all_files())
    # start = time()
    sleep(10)
    file_tree.update()
    # print(time() - start)
    print(file_tree.all_files())

    # dav2 = wc.Client(options2)
    # old = tree.FileTree(dav2, 'webdav/')
    # old.populate()
    # print(file_tree.diff(old))

    #print(len(new.diff(file_tree)))

    # print(dav.enhanced_list('webdav/', include_root=True))
    #print(dav.info('webdav/'))
    #print(dav.list('webdav/'))
    # print(dav._get_properties('webdav/', 1))
    # print(dav.info('webdav/test.html'))


if __name__ == "__main__":
    main()