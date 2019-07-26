import configparser
import time
import datetime
import os 
from PIL import Image, ImageFile
import errno

ImageFile.MAXBLOCK = 2**20

file_dict = dict()

def read_parser(cfg_path):
    config = configparser.ConfigParser()
    config.sections()
    config.read(cfg_path)
    return config


def create_parser(cfg_path):
    config = configparser.ConfigParser()
    config['main'] = {'inputfolder': 'in', 
                      'outputfolder': 'out',
                      'picture': 'watermark.png',
                      'opacity': 100,
                      'filetypes': 'png,jpg,gif,jpeg',
                      'processed_files_config':'processed.txt',
                      'xratio':'16',
                      'yratio':'9' }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    return config


def read_or_create_parser():
    cfg_path = os.path.join(os.getcwd(),'config.ini')
    exists = os.path.isfile(cfg_path)
    if exists:
        return read_parser(cfg_path)
    else :
        return create_parser(cfg_path)

def exclude_proccessed_files(config, files):
    filelistpath = config['main']['processed_files_config']
    exists = os.path.isfile(filelistpath)
    new_file_list = []
    if exists:
        processed_files = []
        with open(filelistpath, 'r') as listfile:
            processed_files = listfile.readlines()

        print(processed_files)

        for f in processed_files:
            file_dict[f.rstrip()]=True

        for f in files:
            if f in file_dict :
                pass
            else :
                new_file_list.append(f)
        return new_file_list
    else :
        return files


def get_unprocceessed_files(config):
    inpath = config['main']['inputfolder']
    filter_types = str.split(config['main']['filetypes'],',')
    filter_types = tuple(('.'+type) for type in filter_types)
    print(filter_types)

    listOfFiles = list()
    for (dirpath, inpath, filenames) in os.walk(inpath):
        listOfFiles += [ os.path.join(''.join(dirpath.split(os.path.sep)[1:]), file) for file in filenames]

    print('Found file(s):',listOfFiles)
    pass
    files = exclude_proccessed_files(config,listOfFiles)
    return files


def add_to_excluded(config, filename):
    filelistpath = config['main']['processed_files_config']
    exists = os.path.isfile(os.path.join(os.getcwd(),filelistpath))
    print(filelistpath, exists)
    if exists:
        with open(filelistpath, 'a') as listfile:
            listfile.write( filename + '\n')
    else :
        with open(filelistpath, 'w') as listfile:
            listfile.write( filename + '\n')

    file_dict[filename]=True
    print(filename)


def proccess_files(confing, files):
    #clear meta info
    # get image width and height
    inpath = config['main']['inputfolder']
    outpath = config['main']['outputfolder']
    logo_path = config['main']['picture']
    xratio = float(config['main']['xratio'])
    yratio = float(config['main']['yratio'])

    logo = Image.open(logo_path)
    # logox,logoy = logo.size

    for f in files:
        f_with_path = os.path.join(inpath, f)
        out_file_name = os.path.splitext(f)[0]+'{}.jpg'.format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        print(out_file_name)
        im = Image.open(f_with_path)
        width, height = im.size
        print('--------------- actual size ',width, height)

        if (width>height) :
            if(float(width)/float(height) > xratio/yratio):
                newsize = (height *xratio/yratio, height) # 
            else:
                newsize = (width, (width * yratio / xratio)) # 
        else:
            if(float(height)/float(width) > xratio/yratio):
                newsize = (width, width*xratio/yratio) # 
            else:
                newsize = (height* yratio / xratio, height ) # 
        print('--------------- new size ',newsize)
        deltax = abs(width-newsize[0])/2
        deltay = abs(height-newsize[1])/2
        # logo = Image.open(logo_path)
        # logo.thumbnail(maxsize, Image.ANTIALIAS)
        # logox,logoy = logo.size
        # im.paste(logo,(width-logox,height-logoy),logo)
        # im.convert('RGB').save(os.path.join(outpath, out_file_name),  "JPEG", quality=100, optimize=True, progressive=True)
        if not os.path.exists(os.path.dirname(os.path.join(outpath, out_file_name))):
            try:
                os.makedirs(os.path.dirname(os.path.join(outpath, out_file_name)))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        im.convert('RGB').crop((deltax,deltay,width-deltax,height-deltay)).save(os.path.join(outpath, out_file_name),  "JPEG", quality=100, optimize=True, progressive=True)
        add_to_excluded(config,f)

if __name__ == "__main__":
    config = read_or_create_parser()
    while True:
        files = get_unprocceessed_files(config)
        print(datetime.datetime.now())
        if files:
            proccess_files(config,files)
        else :
            time.sleep(1)
        time.sleep(1)

    