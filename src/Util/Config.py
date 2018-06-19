'''
'''
# coding = 'utf-8'

class Config(dict):
    '''
    '''

    def __init__(self, defaults=None):
        dict.__init__(self, defaults or {})
        

    def fromObj(self, obj):
        for key in dir(obj):
            if key.isupper() and not key.startswith('_'):
                self[key] = getattr(obj, key)
        return self


    def __getitem__(self, key):
        if key.isupper():
            return dict.__getitem__(self, key)
        else:
            _key = f'{key.upper()}_'
            _len = len(_key)
            _dict = {k[_len:]: v for k, v in self.items() if k.startswith(_key)}
            if not _dict:
                raise KeyError(key)
            return Config(_dict)


# config = {
#     #15张图
#     'imageRoot': 'D:/dev/unicorn/test/data/__NImage/image',
#     #10k张图
#     #'imageRoot': 'D:/1000000/image/images0/images/0',
#     #100k张图
#     # 'imageRoot': 'D:/1000000/image/images0/images',

#     'targets': [('D:/dev/unicorn/test/data/__NImage/feature/imagePathLabels.txt', ['path', 'label']),
#                 ('D:/dev/unicorn/test/data/__NImage/feature/imagePathAlias.txt', ['path', 'alias']),
#                 ('D:/dev/unicorn/test/data/__NImage/feature/aliasLabel.txt', ['alias', 'label'])],
#     'db': {
#         'hashFeatureFilename': 'D:/dev/unicorn/test/data/__NImage/feature/1.bin',
#         'imageFeatureFilename': 'D:/dev/unicorn/test/data/__NImage/feature/2.bin',
#         'labelsFilename': 'D:/dev/unicorn/test/data/__NImage/feature/labels.txt',
#     },

#     'imagePathLabelsFilename': 'D:/dev/unicorn/test/data/__NImage/feature/imagePathLabels.txt',
#     'groundTruth': 'D:/dev/unicorn/test/data/__NImage/feature/aliasLabel.txt',
#     'imagePathAlias': 'D:/dev/unicorn/test/data/__NImage/feature/imagePathAlias.txt',
#     # 'sample': [0, 10, 20]
#     'extracte': {
#         'num_classes': 11,
#         'checkpoint_path': 'D:/dev/unicorn/model/model.ckpt-42100'
#     }

# }            

    

class ConfigBase(object):
    ROOT = 'd:/dev/unicorn/test/data'
    IMAGE_PATH_LABELS_FILENAME = f'{ROOT}/__NImage/feature/imagePathLabels.txt'
    GROUN_TRUTH      = f'{ROOT}/__NImage/feature/aliasLabel.txt'
    IMAGE_PATH_ALIAS = f'{ROOT}/__NImage/feature/imagePathAlias.txt'
    ALIAS_LABEL      = f'{ROOT}/__NImage/feature/aliasLabel.txt'
    TARGETS          = [(IMAGE_PATH_LABELS_FILENAME, ['path',  'label']),
                        (IMAGE_PATH_ALIAS,           ['path',  'alias']),
                        (ALIAS_LABEL,                ['alias', 'label'])]



class DbConfig(ConfigBase):
    _DATA_ROOT                  = f'{ConfigBase.ROOT}/__NImage/feature'
    DB_HASH_FEATURE_FILENAME    = f'{_DATA_ROOT}/1.bin'
    DB_IMAGE_FEATURE_FILENAME   = f'{_DATA_ROOT}/2.bin'
    DB_LABELS_FILENAME          = f'{_DATA_ROOT}/labels.txt'



class ExtractorConfig(ConfigBase):
    EXTRACTOR_NUM_CLASSES     = 11
    EXTRACTOR_CHECKPOINT_PATH = 'D:/dev/unicorn/model/model.ckpt-42100'



class AppConfig(DbConfig, ExtractorConfig):
    pass



if __name__ == '__main__':
    config = Config().fromObj(AppConfig)
    # print(config['db']['HASH_FEATURE_FILENAME'])  #输出 d:/dev/unicorn/test/data/__NImage/feature/1.bin
    # print(config['_DATA_ROOT'])



    

    
    

