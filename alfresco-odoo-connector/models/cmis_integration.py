import cmislib
import logging
import ntpath


class CMISController(object):

    def __init__(self, domain_url, user_name, pass_word):

        self._logger = logging.getLogger('CMIS Wrapper')
        #self._logger.setLevel(logging.DEBUG)
        #fh = logging.FileHandler('cmis.log')
        #fh.setLevel(logging.DEBUG)
        #formatter = logging.Formatter('%(asctime)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s')
        #fh.setFormatter(formatter)
        #self._logger.addHandler(fh)
        self._cmis_conn = cmislib.CmisClient(domain_url,user_name,pass_word)

    def get_root_directory(self):

        try:
            repo = self._cmis_conn.defaultRepository
            root_folder = repo.rootFolder
            return root_folder
        except Exception as err:
            self._logger.error(err)
            return False

    def get_folder_instance(self, root_folder, directory_name):

        try:
            children = root_folder.getChildren()
            directory_instance = None
            for child in children:
                folder_name = child.name
                if folder_name == directory_name:
                    directory_instance = child
                    break
            return directory_instance
        except Exception as err:
            self._logger.error(err)
            return False

    def remove_file_instance(self, directory_name,file_name):

        try:
            root_folder = self.get_root_directory()
            if root_folder == False:
                self._logger.error("Some Error occured while getting root node")
                return False
            else:
                folder_instance = self.get_folder_instance(root_folder, directory_name)
                if folder_instance == False:
                    self._logger.error("Some Error occured while getting specified folder node")
                    return False
                else:
                    if folder_instance == None:
                        self._logger.debug(directory_name + " Folder not found skipping ..")
                    else:
                        file_already_exist_object = self.check_duplicate_file(folder_instance, file_name)
                        if file_already_exist_object:
                            self.delete_file(file_already_exist_object)
                        else:
                            self._logger.debug("File does not exist skipping.....")
            return True
        except Exception as err:
            self._logger.error(err)
            return False

    def create_directory(self,folder_name):

        try:
            root_folder = self.get_root_directory()
            if root_folder==False:
                self._logger.error("Some Error occured while getting root node")
                return False
            else:
                folder_instance = self.get_folder_instance(root_folder,folder_name)
                if folder_instance==False:
                    self._logger.error("Some Error occured while getting specified folder node")
                    return False
                else:
                    if folder_instance==None:
                        self._logger.debug(folder_name + " Folder not found adding new folder")
                        root_folder.createFolder(folder_name)
                    else:
                        self._logger.debug(folder_name + " already exist so skipping.....")
            return True
        except Exception as err:
            self._logger.error(err)
            return False


    def upload_file(self,file_name,directory_name='',overwrite_flag = False):

        try:
            root_folder = self.get_root_directory()
            file_content = open(file_name, 'rb')
            storing_file_name = ntpath.basename(file_name)

            if root_folder==False:
                self._logger.error("Some Error occured while getting root node")
                return False
            else:
                if directory_name=='':
                    self._logger.debug("Directory is not defined, Uploading file to root folder")
                    file_already_exist_object = self.check_duplicate_file(root_folder,storing_file_name)
                    if file_already_exist_object:
                        if overwrite_flag:
                            self.delete_file(file_already_exist_object)
                            root_folder.createDocument(storing_file_name, contentFile=file_content)
                        else:
                            self._logger.debug("File already exist but nothing to do it.")
                    else:
                        root_folder.createDocument(storing_file_name, contentFile=file_content)
                else:
                    folder_instance = self.get_folder_instance(root_folder, directory_name)
                    if folder_instance == False:
                        self._logger.error("Some Error occured while getting specified folder node")
                        return False
                    else:
                        if folder_instance == None:
                            self._logger.debug(directory_name + " Folder not found skipping ..")
                        else:
                            self._logger.debug(" uploading file " + storing_file_name + " to " + directory_name)
                            file_already_exist_object = self.check_duplicate_file(folder_instance, storing_file_name)
                            if file_already_exist_object:
                                if overwrite_flag:
                                    self.delete_file(file_already_exist_object)
                                    folder_instance.createDocument(storing_file_name, contentFile=file_content)
                                else:
                                    self._logger.debug("File already exist but nothing to do it.")
                            else:
                                folder_instance.createDocument(storing_file_name, contentFile=file_content)
            return True
        except Exception as err:
            self._logger.error(err)
            return False

    def download_method(self,file_already_exist_object):
        try:
            name_of_file = file_already_exist_object.getName()
            o = open(name_of_file, 'wb')
            result = file_already_exist_object.getContentStream()
            o.write(result.read())
            result.close()
            o.close()
            return True
        except Exception as err:
            self._logger.error(err)
            return False


    def download_file(self,file_name,directory_name=''):

        try:
            root_folder = self.get_root_directory()
            storing_file_name = ntpath.basename(file_name)
            if root_folder==False:
                self._logger.error("Some Error occured while getting root node")
                return False
            else:
                if directory_name=='':
                    self._logger.debug("Directory is not defined, Downloading file from root folder")
                    file_already_exist_object = self.check_duplicate_file(root_folder, storing_file_name)
                    if file_already_exist_object:
                        self.download_method(file_already_exist_object)
                    else:
                        self._logger.debug(storing_file_name + "File not found for download.")
                else:

                    folder_instance = self.get_folder_instance(root_folder, directory_name)
                    if folder_instance:
                        file_object = self.check_duplicate_file(folder_instance,storing_file_name)
                        if file_object:
                            self.download_method(file_object)
                        else:
                            self._logger.debug(storing_file_name + "File not found for download.")
                    else:
                        self._logger.debug(directory_name + " not found.")
            return True
        except Exception as err:
            self._logger.error(err)
            return False

    def check_duplicate_file(self,folder_path,file_name):

        try:
            children = folder_path.getChildren()
            file_object = None
            for child in children:
                each_file_name = child.name
                if each_file_name == file_name:
                    file_object = child
                    break
            return file_object
        except Exception as err:
            self._logger.error(err)
            return False

    def delete_file(self,file_object):

        try:
            file_object.delete()
            return True
        except Exception as err:
            self._logger.error(err)
            return False

    def delete_complete_folder(self,folder_name):

        try:
            root_folder = self.get_root_directory()
            if root_folder==False:
                self._logger.error("Some Error occured while getting root node")
                return False
            else:
                folder_instance = self.get_folder_instance(root_folder,folder_name)
                if folder_instance==False:
                    self._logger.error("Some Error occured while getting specified folder node")
                    return False
                else:
                    if folder_instance==None:
                        self._logger.debug(" Folder not found so skipping delete process ... ")
                    else:
                        self._logger.debug("Completely deleting folder " + folder_name)
                        folder_instance.deleteTree()
            return True

        except Exception as err:
            self._logger.error(err)
            return False

