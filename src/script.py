import shutil
import os, sys
from nsfw_detector import predict


def open_directory(path):
    if sys.platform.startswith('darwin'):  # macOS
        os.system('open "{}"'.format(path))
    elif sys.platform.startswith('win'):  # Windows
        os.system('start "" "{}"'.format(path))
    elif sys.platform.startswith('linux'):  # Linux
        os.system('xdg-open "{}"'.format(path))
    else:
        print("Unsupported operating system.")


class NSFWModelClass:
    def __init__(self):
        self.__model = ''
        self.__image_dim = 224

    def __filter_nsfw_image_single(self, filename, result_dict):
        for k, v in predict.classify(self.__model, filename, image_dim=self.__image_dim).items():
            if v['neutral'] > v['drawings']:
                result_dict[k] = 'safe' if v['drawings'] > v['sexy'] \
                    else ('semi-nsfw' if v['drawings'] > v['hentai']
                          else 'nsfw')
            else:
                result_dict[k] = 'safe' if v['neutral'] > v['sexy'] \
                    else ('semi-nsfw' if v['neutral'] > v['porn']
                          else 'nsfw')

    def __filter_nsfw_image(self, filename):
        result_dict = {}
        # if filename is list type(multiple files)
        if isinstance(filename, list):
            for _ in filename:
                self.__filter_nsfw_image_single(_, result_dict)
        # single image or directory
        elif isinstance(filename, str):
            self.__filter_nsfw_image_single(filename, result_dict)

        return result_dict

    def set_model(self, model_filename):
        try:
            self.__model = predict.load_model(model_filename)
            self.__image_dim = 224 if model_filename.find('224') != -1 else 299
        except Exception:
            print(f'{model_filename} not found.')

    def filter_nsfw_image_in_directory(self, directory, recursive=False):
        result_dict = {}
        if recursive:
            filenames = []
            valid_extensions = ('jpg', 'jpeg', 'png', 'gif')
            for root, dirs, files in os.walk(directory):
                for file in files:
                    _, extension = os.path.splitext(file)
                    if extension[1:].lower() in valid_extensions:
                        filenames.append(os.path.join(root, file))
            result_dict = self.__filter_nsfw_image(filenames)
        else:
            result_dict = self.__filter_nsfw_image(directory)
        return result_dict

    def filter_nsfw_image_in_filenames(self, filenames):
        return self.__filter_nsfw_image(filenames)

    def backup_files_and_remove_nsfw_files(self, result_dict: dict, backup_directory='backup', level=1):
        """
        level 1 indicates this will filter only nsfw
        level 2 indicates this will filter not only nsfw, but also semi-nsfw
        """
        os.makedirs(backup_directory, exist_ok=True)

        # backup
        # copy directory tree
        result_dict_dirnames = list(set([os.path.dirname(os.path.relpath(dirname)) for dirname in result_dict.keys()]))
        result_dict_dirnames = list(filter(lambda x: x != '', result_dict_dirnames))
        for _ in result_dict_dirnames:
            os.makedirs(os.path.join(backup_directory, _), exist_ok=True)

        for k, v in result_dict.items():
            # copy backup files
            to_file = os.path.join(backup_directory, os.path.relpath(k))
            shutil.copy(k, to_file)
            if level == 1:
                f = v == 'nsfw'
            elif level == 2:
                f = v == 'nsfw' or v == 'semi-nsfw'
            if f:
                # remove files which are supposed to be filtered
                os.remove(k)


# for CUI
# filename = 'nsfw.299x299.h5'
# c = NSFWModelClass()
# c.set_model(filename)
# result_dir = c.filter_nsfw_image_in_directory('.', recursive=True)
# c.backup_files_and_remove_nsfw_files(result_dir)
